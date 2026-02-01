"""v5.0 시너지 시스템 (Phase 1A 확장)"""
from typing import Any, Optional
import random
from models.synergy import Synergy, SynergyType, PlayerSynergies
from seeds.synergies import ALL_SYNERGIES, SET_SYNERGIES, ELEMENT_SYNERGIES, HIDDEN_SYNERGIES


async def check_synergies(player: Any) -> list[Synergy]:
    """
    플레이어의 장착 아이템 기반 활성 시너지 확인

    Returns:
        활성화된 시너지 목록
    """
    from repository.item_repo import ItemRepository

    # 장착 중인 아이템 ID 목록
    equipped_ids = set()
    equipped_items = []

    for slot, item_id in player.equipment.items():
        if item_id:
            equipped_ids.add(item_id)
            item = await ItemRepository.get_by_id(item_id)
            if item:
                equipped_items.append(item)

    active_synergies = []

    # 세트 시너지 체크 (숨겨진 시너지 포함)
    for synergy in SET_SYNERGIES + HIDDEN_SYNERGIES:
        if synergy.type != SynergyType.SET:
            continue
        # 필요 아이템 중 장착 중인 개수
        matched = sum(1 for item_id in synergy.required_items if item_id in equipped_ids)
        if matched >= synergy.required_count:
            active_synergies.append(synergy)

    # 속성 시너지 체크 (장착 아이템의 effect에서 속성 확인)
    element_counts = {}
    for item in equipped_items:
        if item.effect:
            # 화염 관련
            if item.effect.get("fire_damage") or item.effect.get("fire_resist"):
                element_counts["fire"] = element_counts.get("fire", 0) + 1
            # 냉기 관련
            if item.effect.get("ice_damage") or item.effect.get("slow_chance"):
                element_counts["ice"] = element_counts.get("ice", 0) + 1
            # 독 관련
            if item.effect.get("poison") or item.effect.get("poison_damage") or "poison" in item.id:
                element_counts["poison"] = element_counts.get("poison", 0) + 1
            # 흡혈 관련 (암흑)
            if item.effect.get("lifesteal"):
                element_counts["dark"] = element_counts.get("dark", 0) + 1
            # 신성 관련
            if item.effect.get("holy_damage") or item.effect.get("heal_bonus"):
                element_counts["holy"] = element_counts.get("holy", 0) + 1

    for synergy in ELEMENT_SYNERGIES:
        if synergy.required_category:
            count = element_counts.get(synergy.required_category, 0)
            if count >= synergy.required_count:
                active_synergies.append(synergy)

    return active_synergies


def apply_synergy_effects(player: Any, synergies: list[Synergy]) -> dict:
    """
    시너지 효과 적용

    Returns:
        적용된 효과 요약

    Note:
        v6.7.2: _mult 키는 1.0으로 초기화하여 곱셈 안정성 보장
    """
    total_effects = {}

    for synergy in synergies:
        for key, value in synergy.effect.items():
            if key in total_effects:
                if key.endswith("_mult"):
                    total_effects[key] *= value
                elif isinstance(value, bool):
                    total_effects[key] = total_effects[key] or value
                else:
                    total_effects[key] += value
            else:
                # _mult 키는 첫 값 그대로 사용 (이미 배율이므로)
                # 다른 키는 값 그대로 사용
                total_effects[key] = value

    # 없는 _mult 키를 기본값 1.0으로 보장
    # (호출자가 기대하는 배율 키가 없을 때 1.0 반환)
    return total_effects


def get_synergy_bonus(synergies: list[Synergy], effect_name: str) -> float:
    """특정 효과의 시너지 보너스"""
    total = 0
    for synergy in synergies:
        if effect_name in synergy.effect:
            value = synergy.effect[effect_name]
            if effect_name.endswith("_mult"):
                total = (total or 1) * value
            else:
                total += value
    return total


def has_synergy_effect(synergies: list[Synergy], effect_name: str) -> bool:
    """특정 효과가 있는지 확인"""
    return any(effect_name in s.effect for s in synergies)


async def get_synergy_display(player: Any) -> str:
    """시너지 UI 표시"""
    synergies = await check_synergies(player)

    if not synergies:
        return ""

    lines = [
        "",
        "───────────────────────────────────────────────────",
        "  🔗 활성 시너지",
    ]

    for synergy in synergies:
        hidden_mark = "❓" if synergy.hidden else ""
        powerful_mark = "⚡" if synergy.is_powerful else ""
        lines.append(f"  • {hidden_mark}{powerful_mark}{synergy.name}: {synergy.effect_text}")

    return "\n".join(lines)


async def discover_synergy(player: Any, synergy_id: str) -> Optional[Synergy]:
    """
    숨겨진 시너지 발견 처리

    Returns:
        발견한 시너지 (이미 발견했으면 None)
    """
    from seeds.synergies import get_synergy_by_id

    synergy = get_synergy_by_id(synergy_id)
    if not synergy:
        return None

    if not synergy.hidden:
        return None  # 숨겨진 시너지가 아님

    # 플레이어 발견 목록에 추가 (메타 데이터로 저장 필요)
    # 여기서는 단순히 synergy 반환
    return synergy


def format_synergy_discovery(synergy: Synergy) -> str:
    """시너지 발견 메시지"""
    powerful_text = "\n  ⚡ 강력한 시너지입니다!" if synergy.is_powerful else ""
    return f"""
═══════════════════════════════════════════════════
  🎉 숨겨진 시너지 발견!

  🔗 {synergy.name}
  {synergy.description}

  효과: {synergy.effect_text}{powerful_text}
═══════════════════════════════════════════════════
"""


# 시너지 조합 힌트 (발견 전에 보여줄 수 있음)
SYNERGY_HINTS = {
    "fire_master": "화염의 힘을 모아보세요...",
    "vampire_lord": "피에 굶주린 자의 길...",
    "shadow_walker": "어둠 속에 숨겨진 힘...",
    "fortune_seeker": "행운은 두 번 찾아온다...",
    "curse_bearer": "저주 속에서 힘을 찾는 자...",
    "dungeon_master": "던전의 주인이 되려면...",
    # Phase 1A 신규
    "curse_master": "저주를 받아들이면 축복이 된다...",
    "elemental_avatar": "원소와 하나가 되어라...",
    "immortal_tank": "맞으면서 회복하는 자...",
}


def get_synergy_hint(synergy_id: str) -> str:
    """시너지 힌트 반환"""
    return SYNERGY_HINTS.get(synergy_id, "???")


# ============================================================
# Phase 1A: 시너지 전투 효과 적용 함수들
# ============================================================

async def get_combat_synergy_effects(player: Any) -> dict:
    """
    전투에서 사용할 시너지 효과 계산

    Returns:
        전투용 효과 딕셔너리
    """
    synergies = await check_synergies(player)
    hp_ratio = player.hp / player.max_hp if player.max_hp > 0 else 1.0

    effects = {
        # 기본 배율
        "damage_mult": 1.0,
        "skill_damage_mult": 1.0,
        "crit_bonus": 0.0,

        # 속성 배율
        "fire_damage_mult": 1.0,
        "ice_damage_mult": 1.0,
        "poison_damage_mult": 1.0,

        # 흡혈
        "lifesteal": 0.0,
        "lifesteal_on_reflect": False,

        # 방어
        "damage_reduction": 0.0,
        "reflect_damage": 0.0,
        "counter_chance": 0.0,
        "counter_damage_mult": 1.0,

        # 특수 효과
        "execute_threshold": 0.0,
        "first_strike_mult": 1.0,
        "stealth": False,
        "curse_immunity": False,
        "curse_to_blessing": False,

        # 고정 데미지
        "void_damage": 0,
        "aura_damage": 0,

        # 상태이상 확률
        "burn_chance": 0.0,
        "freeze_chance": 0.0,
    }

    for synergy in synergies:
        effect = synergy.effect

        # 데미지 배율 (곱셈)
        if "damage_mult" in effect:
            effects["damage_mult"] *= effect["damage_mult"]
        if "skill_damage_mult" in effect:
            effects["skill_damage_mult"] *= effect["skill_damage_mult"]

        # 속성 배율 (곱셈)
        if "fire_damage_mult" in effect:
            effects["fire_damage_mult"] *= effect["fire_damage_mult"]
        if "ice_damage_mult" in effect:
            effects["ice_damage_mult"] *= effect["ice_damage_mult"]
        if "poison_damage_mult" in effect:
            effects["poison_damage_mult"] *= effect["poison_damage_mult"]
        if "element_damage_mult" in effect:
            # 모든 속성에 적용
            effects["fire_damage_mult"] *= effect["element_damage_mult"]
            effects["ice_damage_mult"] *= effect["element_damage_mult"]
            effects["poison_damage_mult"] *= effect["element_damage_mult"]

        # 크리티컬 (합산)
        if "crit_bonus" in effect:
            effects["crit_bonus"] += effect["crit_bonus"]

        # 흡혈 (합산, 저HP 배율 적용)
        if "lifesteal" in effect:
            base = effect["lifesteal"]
            threshold = effect.get("lifesteal_threshold", 0)
            multiplier = effect.get("lifesteal_on_low_hp", 1.0)
            if threshold > 0 and hp_ratio <= threshold:
                base *= multiplier
            effects["lifesteal"] += base

        if effect.get("lifesteal_on_reflect"):
            effects["lifesteal_on_reflect"] = True

        # 방어 (합산)
        if "damage_reduction" in effect:
            effects["damage_reduction"] += effect["damage_reduction"]
        if "reflect_damage" in effect:
            effects["reflect_damage"] += effect["reflect_damage"]
        if "counter_chance" in effect:
            effects["counter_chance"] += effect["counter_chance"]
        if "counter_damage_mult" in effect:
            effects["counter_damage_mult"] = max(
                effects["counter_damage_mult"], effect["counter_damage_mult"]
            )

        # 특수 효과 (최대값 또는 OR)
        if "execute_threshold" in effect:
            effects["execute_threshold"] = max(
                effects["execute_threshold"], effect["execute_threshold"]
            )
        if "first_strike_mult" in effect:
            effects["first_strike_mult"] = max(
                effects["first_strike_mult"], effect["first_strike_mult"]
            )
        if effect.get("stealth"):
            effects["stealth"] = True
        if effect.get("curse_immunity"):
            effects["curse_immunity"] = True
        if effect.get("curse_to_blessing"):
            effects["curse_to_blessing"] = True

        # 고정 데미지 (합산)
        if "void_damage" in effect:
            effects["void_damage"] += effect["void_damage"]
        if "aura_damage" in effect:
            effects["aura_damage"] += effect["aura_damage"]

        # 상태이상 확률 (합산)
        if "burn_chance" in effect:
            effects["burn_chance"] += effect["burn_chance"]
        if "freeze_chance" in effect:
            effects["freeze_chance"] += effect["freeze_chance"]

    # 상한 적용
    effects["counter_chance"] = min(1.0, effects["counter_chance"])
    effects["damage_reduction"] = min(0.75, effects["damage_reduction"])  # 최대 75% 감소

    return effects


def apply_execute(enemy: Any, threshold: float) -> tuple[bool, str]:
    """
    즉사 효과 적용

    Returns:
        (즉사 여부, 메시지)

    Note:
        보스에게는 즉사 효과가 적용되지 않습니다.
    """
    if threshold <= 0:
        return False, ""

    # Phase 1C: 보스 즉사 불가 (밸런스)
    if hasattr(enemy, 'is_boss') and enemy.is_boss:
        return False, ""

    hp_ratio = enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 1.0
    if hp_ratio <= threshold:
        enemy.hp = 0
        return True, f"⚡ 처형! {enemy.name}이(가) 즉사했습니다!"

    return False, ""


def apply_counter_attack(
    player: Any,
    enemy: Any,
    counter_chance: float,
    counter_mult: float,
    received_damage: int
) -> tuple[int, str]:
    """
    반격 효과 적용

    Returns:
        (반격 데미지, 메시지)
    """
    if counter_chance <= 0:
        return 0, ""

    if random.random() > counter_chance:
        return 0, ""

    counter_damage = int(received_damage * counter_mult)
    enemy.take_damage(counter_damage)
    return counter_damage, f"⚔️ 반격! {enemy.name}에게 {counter_damage} 데미지!"


def apply_lifesteal(
    player: Any,
    damage: int,
    lifesteal_ratio: float
) -> tuple[int, str]:
    """
    흡혈 효과 적용

    Returns:
        (회복량, 메시지)

    Note:
        Phase 1C: 흡혈 상한 = 최대 HP의 30% (무한 회복 방지)
    """
    if lifesteal_ratio <= 0 or damage <= 0:
        return 0, ""

    heal = int(damage * lifesteal_ratio)

    # Phase 1C: 흡혈 상한 (최대 HP의 30%)
    max_heal = int(player.max_hp * 0.3)
    heal = min(heal, max_heal)

    if heal > 0:
        player.heal(heal)
        return heal, f"🩸 흡혈! HP +{heal}"

    return 0, ""


def apply_reflect_damage(
    player: Any,
    enemy: Any,
    received_damage: int,
    reflect_ratio: float,
    lifesteal_on_reflect: bool = False,
    lifesteal_ratio: float = 0.0
) -> tuple[int, int, str]:
    """
    반사 데미지 적용 (흡혈 연계 가능)

    Returns:
        (반사 데미지, 흡혈량, 메시지)
    """
    if reflect_ratio <= 0 or received_damage <= 0:
        return 0, 0, ""

    reflect_damage = int(received_damage * reflect_ratio)
    enemy.take_damage(reflect_damage)

    heal = 0
    if lifesteal_on_reflect and lifesteal_ratio > 0:
        heal = int(reflect_damage * lifesteal_ratio)
        if heal > 0:
            player.heal(heal)

    if heal > 0:
        return reflect_damage, heal, f"🪞 반사 {reflect_damage} 데미지! 🩸 흡혈 +{heal}"
    else:
        return reflect_damage, 0, f"🪞 반사 {reflect_damage} 데미지!"


def apply_aura_damage(enemy: Any, aura_damage: int) -> tuple[int, str]:
    """
    오라 데미지 적용 (턴마다)

    Returns:
        (데미지, 메시지)
    """
    if aura_damage <= 0:
        return 0, ""

    enemy.take_damage(aura_damage)
    return aura_damage, f"✨ 오라 데미지! {enemy.name}에게 {aura_damage} 데미지!"


def check_burn_proc(burn_chance: float) -> bool:
    """화상 발동 확인"""
    return random.random() < burn_chance


def check_freeze_proc(freeze_chance: float) -> bool:
    """빙결 발동 확인"""
    return random.random() < freeze_chance


# ============================================================
# 시너지 발동 알림
# ============================================================

def get_new_synergy_message(old_synergies: list[Synergy], new_synergies: list[Synergy]) -> str:
    """새로 발동된 시너지 메시지"""
    old_ids = {s.id for s in old_synergies}
    new_ones = [s for s in new_synergies if s.id not in old_ids]

    if not new_ones:
        return ""

    lines = ["\n🔗 새로운 시너지 발동!"]
    for synergy in new_ones:
        mark = "⚡" if synergy.is_powerful else ""
        lines.append(f"  {mark}{synergy.name}: {synergy.effect_text}")

    return "\n".join(lines)
