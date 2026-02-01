"""v5.0 축복 시스템"""
import random
from typing import TYPE_CHECKING, Optional

from models.blessing import Blessing, BlessingRarity, PlayerBlessings
from seeds.blessings import BLESSINGS, RARITY_WEIGHTS, get_blessing_by_id

# v6.6: 순환 참조 방지를 위한 TYPE_CHECKING 사용
if TYPE_CHECKING:
    from models.player import Player


def generate_blessing_choices(
    player_blessings: PlayerBlessings,
    count: int = 3,
    floor: int = 1,
    force_rare: bool = False,  # v5.0 악마의 거래용
) -> list[Blessing]:
    """
    전투 승리 후 축복 선택지 생성

    Args:
        player_blessings: 플레이어가 이미 보유한 축복
        count: 선택지 개수 (기본 3개)
        floor: 현재 층 (높을수록 좋은 축복 확률 증가)
        force_rare: True면 희귀 이상만 선택

    Returns:
        축복 선택지 리스트
    """
    # 이미 보유한 축복 ID
    if hasattr(player_blessings, 'blessings'):
        owned_ids = {b.id for b in player_blessings.blessings}
    else:
        # list로 전달된 경우
        owned_ids = {b.id for b in player_blessings} if player_blessings else set()

    # 사용 가능한 축복
    available = [b for b in BLESSINGS if b.id not in owned_ids]

    # v5.0: 희귀 이상 강제
    if force_rare:
        available = [b for b in available if b.rarity in [BlessingRarity.RARE, BlessingRarity.LEGENDARY]]

    if not available:
        return []

    # 층에 따른 희귀도 보정
    # 높은 층일수록 좋은 축복 확률 증가
    floor_bonus = min(floor * 2, 10)  # 최대 10% 보정

    adjusted_weights = RARITY_WEIGHTS.copy()
    adjusted_weights[BlessingRarity.RARE] += floor_bonus
    adjusted_weights[BlessingRarity.LEGENDARY] += floor_bonus // 2

    # 희귀도별 축복 분류
    by_rarity = {rarity: [] for rarity in BlessingRarity}
    for blessing in available:
        by_rarity[blessing.rarity].append(blessing)

    # 선택지 생성
    choices = []

    if force_rare:
        # 희귀 이상만 선택
        rarities = [BlessingRarity.RARE, BlessingRarity.LEGENDARY]
        weights = [70, 30]  # 희귀 70%, 전설 30%
    else:
        rarities = list(BlessingRarity)
        weights = [adjusted_weights[r] for r in rarities]

    attempts = 0
    max_attempts = count * 3  # 최대 시도 횟수

    while len(choices) < count and attempts < max_attempts:
        attempts += 1

        # 희귀도 선택
        chosen_rarity = random.choices(rarities, weights=weights)[0]

        # 해당 희귀도의 축복 중 하나 선택
        rarity_blessings = by_rarity[chosen_rarity]
        if not rarity_blessings:
            continue

        blessing = random.choice(rarity_blessings)

        # 중복 체크
        if blessing not in choices:
            choices.append(blessing)
            rarity_blessings.remove(blessing)  # 중복 방지

    return choices


def apply_blessing(player: "Player", blessing: Blessing) -> dict:
    """
    축복을 플레이어에게 적용

    Args:
        player: 플레이어
        blessing: 적용할 축복

    Returns:
        적용 결과 (변경된 스탯)
    """
    effect = blessing.effect
    changes = {}

    # 직접 스탯 변경
    if "atk" in effect:
        player.atk += effect["atk"]
        changes["atk"] = effect["atk"]

    if "def" in effect:
        player.def_ += effect["def"]
        changes["def"] = effect["def"]

    if "max_hp" in effect:
        player.max_hp += effect["max_hp"]
        player.hp = min(player.hp, player.max_hp)  # HP가 최대치 초과 방지
        if effect["max_hp"] > 0:
            player.hp += effect["max_hp"]  # 증가분만큼 현재 HP도 증가
        changes["max_hp"] = effect["max_hp"]

    if "max_mp" in effect:
        player.max_mp += effect["max_mp"]
        player.mp = min(player.mp, player.max_mp)
        if effect["max_mp"] > 0:
            player.mp += effect["max_mp"]
        changes["max_mp"] = effect["max_mp"]

    if "crit_chance" in effect:
        player.crit_chance += effect["crit_chance"]
        changes["crit_chance"] = effect["crit_chance"]

    # 축복 목록에 추가
    if hasattr(player, "blessings"):
        player.blessings.append(blessing)

    return changes


def get_blessing_effect_text(blessing: Blessing) -> str:
    """축복 효과 텍스트 생성"""
    effect = blessing.effect
    parts = []

    if "atk" in effect:
        sign = "+" if effect["atk"] >= 0 else ""
        parts.append(f"ATK {sign}{effect['atk']}")

    if "def" in effect:
        sign = "+" if effect["def"] >= 0 else ""
        parts.append(f"DEF {sign}{effect['def']}")

    if "max_hp" in effect:
        sign = "+" if effect["max_hp"] >= 0 else ""
        parts.append(f"최대 HP {sign}{effect['max_hp']}")

    if "max_mp" in effect:
        sign = "+" if effect["max_mp"] >= 0 else ""
        parts.append(f"최대 MP {sign}{effect['max_mp']}")

    if "crit_chance" in effect:
        parts.append(f"크리티컬 +{int(effect['crit_chance'] * 100)}%")

    if "damage_mult" in effect:
        bonus = int((effect["damage_mult"] - 1) * 100)
        parts.append(f"데미지 +{bonus}%")

    if "lifesteal" in effect:
        parts.append(f"흡혈 {int(effect['lifesteal'] * 100)}%")

    if "gold_mult" in effect:
        bonus = int((effect["gold_mult"] - 1) * 100)
        parts.append(f"골드 +{bonus}%")

    if "exp_mult" in effect:
        bonus = int((effect["exp_mult"] - 1) * 100)
        parts.append(f"경험치 +{bonus}%")

    if "thorns" in effect:
        parts.append(f"반사 데미지 {effect['thorns']}")

    if "double_hit" in effect:
        parts.append(f"이중 타격 {int(effect['double_hit'] * 100)}%")

    if "execute_threshold" in effect:
        parts.append(f"즉사 (HP {int(effect['execute_threshold'] * 100)}% 이하)")

    return ", ".join(parts) if parts else blessing.description


def format_blessing_choice(blessing: Blessing, index: int, owned_ids: set[str] = None) -> str:
    """축복 선택지 포맷팅 (Phase 3: 듀오 힌트 포함)"""
    effect_text = get_blessing_effect_text(blessing)

    # Phase 3: 듀오 힌트 확인
    duo_hint = ""
    if owned_ids:
        from seeds.duo_blessings import get_potential_duo
        potential_duo = get_potential_duo(blessing.id, owned_ids)
        if potential_duo:
            duo_hint = f"\n  │     💫 ??? (특수 조합 가능!)"

    return f"""  ┌─────────────────────────────────────────────┐
  │ [{index}] {blessing.icon} {blessing.name} ({blessing.rarity_name})
  │     {blessing.description}
  │     효과: {effect_text}{duo_hint}
  └─────────────────────────────────────────────┘"""


def format_blessing_choices(choices: list[Blessing], owned_blessings: list = None) -> str:
    """축복 선택지 전체 포맷팅 (Phase 3: 듀오 힌트 포함)"""
    if not choices:
        return "  선택 가능한 축복이 없습니다."

    # 보유 축복 ID 추출
    owned_ids = set()
    if owned_blessings:
        owned_ids = {b.id for b in owned_blessings}

    lines = []
    for i, blessing in enumerate(choices, 1):
        lines.append(format_blessing_choice(blessing, i, owned_ids))

    return "\n".join(lines)


# ============================================================
# Phase 3: 듀오 축복 시스템
# ============================================================

def check_and_apply_duos(player: "Player") -> list[tuple[str, dict]]:
    """
    플레이어의 활성 듀오 축복 확인 및 효과 적용

    Returns:
        [(듀오 이름, 효과)] 리스트
    """
    from seeds.duo_blessings import check_active_duos

    if not hasattr(player, 'blessings') or not player.blessings:
        return []

    owned_ids = {b.id for b in player.blessings}
    active_duos = check_active_duos(owned_ids)

    applied = []
    for duo in active_duos:
        applied.append((duo.name, duo.effect))

    return applied


def get_duo_combat_effects(player: "Player") -> dict:
    """
    전투에서 사용할 듀오 효과 계산

    Returns:
        전투용 효과 딕셔너리
    """
    effects = {
        "lifesteal_bonus": 0.0,
        "skill_mp_cost_mult": 1.0,
        "skill_damage_mult": 1.0,
        "attack_hits": 1,
        "gold_mult": 1.0,
        "shop_discount": 0.0,
        "defend_full_reflect": False,
        "poison_execute_threshold": 0.0,
        "death_save": 0,
        "hp_regen_percent": 0.0,
        "mp_regen_percent": 0.0,
        "full_mp_damage_bonus": 0.0,
        "sync_atk_def": False,
        # 분노의 화신
        "hit_to_atk": 0.0,
        "max_rage_stacks": 0,
    }

    applied_duos = check_and_apply_duos(player)
    for duo_name, duo_effect in applied_duos:
        for key, value in duo_effect.items():
            if key in effects:
                if isinstance(value, bool):
                    effects[key] = effects[key] or value
                elif key.endswith("_mult"):
                    effects[key] *= value
                elif key in ["attack_hits", "death_save", "max_rage_stacks"]:
                    effects[key] = max(effects[key], value)
                else:
                    effects[key] += value

    return effects


def get_active_duo_display(player: "Player") -> str:
    """활성 듀오 축복 표시"""
    from seeds.duo_blessings import check_active_duos

    if not hasattr(player, 'blessings') or not player.blessings:
        return ""

    owned_ids = {b.id for b in player.blessings}
    active_duos = check_active_duos(owned_ids)

    if not active_duos:
        return ""

    lines = [
        "",
        "───────────────────────────────────────────────────",
        "  💫 활성 듀오 축복",
    ]

    for duo in active_duos:
        lines.append(f"  • {duo.icon} {duo.name}: {duo.description}")

    return "\n".join(lines)
