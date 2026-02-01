"""스킬 시스템"""
import random
from typing import Any, Optional
from repository.skill_repo import SkillRepository, SkillData
from models.status_effect import StatusEffect, StatusType, StatusManager
from systems.combat import calculate_damage, GameConfig


class SkillResult:
    """스킬 사용 결과"""
    def __init__(self):
        self.success: bool = False
        self.message: str = ""
        self.damage: int = 0
        self.heal: int = 0
        self.is_critical: bool = False
        self.status_applied: list[str] = []
        self.enemy_killed: bool = False
        self.mp_cost: int = 0


async def get_available_skills(player: Any) -> list[SkillData]:
    """플레이어가 사용 가능한 스킬 목록"""
    return await SkillRepository.get_multiple(player.skills)


async def can_use_skill(
    player: Any,
    skill_id: str,
    combat_state: Any,
    turn: int = 1
) -> tuple[bool, str]:
    """
    스킬 사용 가능 여부 확인

    Returns:
        (사용가능여부, 실패사유)
    """
    # 스킬 보유 확인
    if skill_id not in player.skills:
        return False, "해당 스킬을 보유하고 있지 않습니다."

    # 스킬 데이터 조회
    skill = await SkillRepository.get_by_id(skill_id)
    if not skill:
        return False, "존재하지 않는 스킬입니다."

    # Phase 3: 듀오 MP 소모 감소 (아크메이지)
    from systems.blessing import get_duo_combat_effects
    duo_effects = get_duo_combat_effects(player)
    mp_cost_mult = duo_effects.get("skill_mp_cost_mult", 1.0)
    actual_mp_cost = int(skill.mp_cost * mp_cost_mult)

    # MP 확인 (듀오 효과 적용)
    if player.mp < actual_mp_cost:
        return False, f"MP가 부족합니다. (필요: {actual_mp_cost}, 현재: {player.mp})"

    # 쿨다운 확인
    cooldown_key = f"skill_{skill_id}"
    cooldown_remaining = combat_state.cooldowns.get(cooldown_key, 0)
    if cooldown_remaining > 0:
        return False, f"쿨다운 중입니다. ({cooldown_remaining}턴 남음)"

    # 첫 턴 전용 스킬 확인
    if skill.effect.get("first_turn_only") and turn > 1:
        return False, "이 스킬은 첫 턴에만 사용할 수 있습니다."

    return True, ""


async def use_skill(
    player: Any,
    enemy: Any,
    skill_id: str,
    combat_state: Any,
    player_status: StatusManager,
    enemy_status: StatusManager,
) -> SkillResult:
    """
    스킬 사용

    Args:
        player: 플레이어
        enemy: 적
        skill_id: 스킬 ID
        combat_state: 전투 상태
        player_status: 플레이어 상태 이상
        enemy_status: 적 상태 이상

    Returns:
        SkillResult
    """
    result = SkillResult()

    # 스킬 데이터 조회
    skill = await SkillRepository.get_by_id(skill_id)
    if not skill:
        result.message = "존재하지 않는 스킬입니다."
        return result

    # Phase 3: 듀오 MP 소모 감소 (아크메이지)
    from systems.blessing import get_duo_combat_effects
    duo_effects = get_duo_combat_effects(player)
    mp_cost_mult = duo_effects.get("skill_mp_cost_mult", 1.0)
    actual_mp_cost = int(skill.mp_cost * mp_cost_mult)

    # MP 소모 (듀오 효과 적용)
    player.mp -= actual_mp_cost
    result.mp_cost = actual_mp_cost

    # 쿨다운 설정
    if skill.cooldown > 0:
        cooldown_key = f"skill_{skill_id}"
        combat_state.cooldowns[cooldown_key] = skill.cooldown + 1  # 사용 턴 포함

    effect = skill.effect
    result.success = True

    # 스킬 타입별 처리
    if skill.type == "attack":
        result = await _process_attack_skill(
            player, enemy, skill, effect, player_status, enemy_status, result
        )
    elif skill.type == "buff":
        result = await _process_buff_skill(
            player, skill, effect, player_status, result
        )
    elif skill.type == "debuff":
        result = await _process_debuff_skill(
            enemy, skill, effect, enemy_status, result
        )
    elif skill.type == "heal":
        result = await _process_heal_skill(
            player, skill, effect, result
        )

    return result


async def _process_attack_skill(
    player: Any,
    enemy: Any,
    skill: SkillData,
    effect: dict,
    player_status: StatusManager,
    enemy_status: StatusManager,
    result: SkillResult
) -> SkillResult:
    """공격 스킬 처리"""
    from systems.element import calculate_elemental_damage, get_element_icon

    # 즉사 스킬 (사신 죽음의 낫)
    execute_threshold = effect.get("execute_threshold", 0)
    if execute_threshold > 0:
        enemy_hp_ratio = enemy.hp / enemy.max_hp
        if enemy_hp_ratio <= execute_threshold:
            enemy.hp = 0
            result.damage = enemy.max_hp
            result.enemy_killed = True
            result.message = f"⚡ {skill.name}! 즉사 발동!"
            return result

    # 데미지 계산
    damage_mult = effect.get("damage_mult", 1.0)
    flat_bonus = effect.get("flat_bonus", 0)
    hits = effect.get("hits", 1)

    # Phase 3: 듀오 스킬 데미지 배율 (아크메이지)
    from systems.blessing import get_duo_combat_effects
    duo_effects = get_duo_combat_effects(player)
    skill_damage_mult = duo_effects.get("skill_damage_mult", 1.0)
    damage_mult *= skill_damage_mult

    # 마법 데미지 (마법사 보너스)
    if effect.get("magic_damage") and player.class_type == "mage":
        damage_mult *= 1.3  # 마법사 30% 보너스

    # 언데드 특효 (성기사)
    if effect.get("bonus_vs_undead") and getattr(enemy, "is_undead", False):
        damage_mult = effect["bonus_vs_undead"]

    # 크리티컬 판정
    is_critical = False
    crit_chance = player.crit_chance + player_status.get_crit_bonus()

    if effect.get("guaranteed_crit") or player_status.has_guaranteed_crit():
        is_critical = True
        player_status.consume_guaranteed_crit()
    elif random.random() < crit_chance:
        is_critical = True

    # 공격력 배율 적용
    effective_atk = int(player.atk * player_status.get_atk_modifier())

    # 다중 공격 처리
    total_damage = 0
    element_msg = ""
    for i in range(hits):
        damage = calculate_damage(
            effective_atk,
            enemy.def_,
            is_critical=(is_critical and hits == 1),  # 다중 공격은 첫 타만 크리
            damage_mult=damage_mult,
            flat_bonus=flat_bonus
        )

        # v5.0: 속성 데미지 계산 (첫 히트에서만 메시지 표시)
        if skill.element:
            damage, msg = calculate_elemental_damage(damage, skill.element, enemy)
            if i == 0 and msg:
                element_msg = f" {msg}"

        total_damage += damage

    result.damage = total_damage
    result.is_critical = is_critical

    # 적에게 데미지 적용
    enemy.take_damage(total_damage)
    result.enemy_killed = not enemy.is_alive

    # 흡혈
    lifesteal = effect.get("lifesteal", 0)
    if lifesteal > 0:
        heal_amount = int(total_damage * lifesteal)
        actual_heal = player.heal(heal_amount)
        result.heal = actual_heal
        result.status_applied.append(f"HP +{actual_heal} 흡수")

    # 상태 이상 적용
    await _apply_attack_effects(effect, enemy_status, result)

    # 메시지 생성 (v5.0: 속성 아이콘 사용)
    crit_text = " 💥 크리티컬!" if is_critical else ""
    hit_text = f" ({hits}회 공격)" if hits > 1 else ""
    icon = get_element_icon(skill.element) if skill.element else "⚡"
    result.message = f"{icon} {skill.name}!{hit_text} {total_damage} 데미지!{crit_text}{element_msg}"

    return result


async def _apply_attack_effects(
    effect: dict,
    enemy_status: StatusManager,
    result: SkillResult
) -> None:
    """공격 스킬의 부가 효과 적용"""

    # 기절
    stun_chance = effect.get("stun_chance", 0)
    if stun_chance > 0 and random.random() < stun_chance:
        enemy_status.add_effect(StatusEffect(
            type=StatusType.STUN,
            duration=1,
            value=0
        ))
        result.status_applied.append("💫 기절!")

    # 빙결
    freeze_chance = effect.get("freeze_chance", 0)
    if freeze_chance > 0 and random.random() < freeze_chance:
        enemy_status.add_effect(StatusEffect(
            type=StatusType.FREEZE,
            duration=1,
            value=0
        ))
        result.status_applied.append("🧊 빙결!")

    # 독
    poison = effect.get("poison")
    if poison:
        enemy_status.add_effect(StatusEffect(
            type=StatusType.POISON,
            duration=poison["duration"],
            value=poison["damage"]
        ))
        result.status_applied.append(f"🟢 독 ({poison['duration']}턴)")

    # 화상
    burn = effect.get("burn")
    if burn:
        enemy_status.add_effect(StatusEffect(
            type=StatusType.BURN,
            duration=burn["duration"],
            value=burn["damage"]
        ))
        result.status_applied.append(f"🔥 화상 ({burn['duration']}턴)")


async def _process_buff_skill(
    player: Any,
    skill: SkillData,
    effect: dict,
    player_status: StatusManager,
    result: SkillResult
) -> SkillResult:
    """버프 스킬 처리"""

    buff = effect.get("buff", {})
    duration = buff.get("duration", 1)

    applied_buffs = []

    # 공격력 증가
    if "atk_mult" in buff:
        player_status.add_effect(StatusEffect(
            type=StatusType.ATK_UP,
            duration=duration,
            value=buff["atk_mult"] - 1,  # 배율을 보너스로 변환
            source=skill.name
        ))
        increase = int((buff["atk_mult"] - 1) * 100)
        applied_buffs.append(f"⬆️ ATK +{increase}%")

    # 방어력 증가
    if "def_mult" in buff:
        player_status.add_effect(StatusEffect(
            type=StatusType.DEF_UP,
            duration=duration,
            value=buff["def_mult"] - 1,
            source=skill.name
        ))
        increase = int((buff["def_mult"] - 1) * 100)
        applied_buffs.append(f"🔼 DEF +{increase}%")

    # 회피 증가
    if "evasion" in buff:
        player_status.add_effect(StatusEffect(
            type=StatusType.EVASION,
            duration=duration,
            value=buff["evasion"],
            source=skill.name
        ))
        applied_buffs.append(f"💨 회피 +{int(buff['evasion'] * 100)}%")

    # 데미지 감소
    if "damage_reduction" in buff:
        player_status.add_effect(StatusEffect(
            type=StatusType.DAMAGE_REDUCTION,
            duration=duration,
            value=buff["damage_reduction"],
            source=skill.name
        ))
        applied_buffs.append(f"🛡️ 피해 -{int(buff['damage_reduction'] * 100)}%")

    # 마나 실드
    if "mana_shield" in buff:
        player_status.add_effect(StatusEffect(
            type=StatusType.MANA_SHIELD,
            duration=duration,
            value=buff["mana_shield"],
            source=skill.name
        ))
        applied_buffs.append(f"🔮 마나 실드 {int(buff['mana_shield'] * 100)}%")

    # 반사
    if "reflect" in buff:
        player_status.add_effect(StatusEffect(
            type=StatusType.REFLECT,
            duration=duration,
            value=buff["reflect"],
            source=skill.name
        ))
        applied_buffs.append(f"🪞 반사 {int(buff['reflect'] * 100)}%")

    # 크리티컬 보너스
    if "crit_bonus" in buff:
        player_status.add_effect(StatusEffect(
            type=StatusType.CRIT_BONUS,
            duration=duration,
            value=buff["crit_bonus"],
            source=skill.name
        ))
        applied_buffs.append(f"🎯 크리티컬 +{int(buff['crit_bonus'] * 100)}%")

    # 확정 크리티컬
    if buff.get("next_attack_crit"):
        player_status.add_effect(StatusEffect(
            type=StatusType.NEXT_CRIT,
            duration=1,
            value=1,
            source=skill.name
        ))
        applied_buffs.append("💥 다음 공격 확정 크리티컬")

    result.status_applied = applied_buffs
    result.message = f"✨ {skill.name}! ({duration}턴)"

    return result


async def _process_debuff_skill(
    enemy: Any,
    skill: SkillData,
    effect: dict,
    enemy_status: StatusManager,
    result: SkillResult
) -> SkillResult:
    """디버프 스킬 처리"""

    debuff = effect.get("debuff", {})
    duration = debuff.get("duration", 1)

    applied_debuffs = []

    # 방어력 감소
    if "def_mult" in debuff:
        enemy_status.add_effect(StatusEffect(
            type=StatusType.DEF_DOWN,
            duration=duration,
            value=debuff["def_mult"],
            source=skill.name
        ))
        decrease = int((1 - debuff["def_mult"]) * 100)
        applied_debuffs.append(f"🔽 DEF -{decrease}%")

    # 공격력 감소
    if "atk_mult" in debuff:
        enemy_status.add_effect(StatusEffect(
            type=StatusType.ATK_DOWN,
            duration=duration,
            value=debuff["atk_mult"],
            source=skill.name
        ))
        decrease = int((1 - debuff["atk_mult"]) * 100)
        applied_debuffs.append(f"⬇️ ATK -{decrease}%")

    # 죽음의 표식
    mark = effect.get("mark")
    if mark:
        enemy_status.add_effect(StatusEffect(
            type=StatusType.DEATH_MARK,
            duration=mark["trigger_turn"],
            value=mark["damage_percent"],
            source=skill.name
        ))
        applied_debuffs.append(f"💀 죽음의 표식 ({mark['trigger_turn']}턴)")

    result.status_applied = applied_debuffs
    result.message = f"🌀 {skill.name}! ({duration}턴)"

    return result


async def _process_heal_skill(
    player: Any,
    skill: SkillData,
    effect: dict,
    result: SkillResult
) -> SkillResult:
    """회복 스킬 처리"""

    heal_amount = 0

    # 최대 HP 비율 회복
    if "heal_percent" in effect:
        heal_amount = int(player.max_hp * effect["heal_percent"])

    # 고정 회복
    if "heal_flat" in effect:
        heal_amount += effect["heal_flat"]

    actual_heal = player.heal(heal_amount)
    result.heal = actual_heal
    result.message = f"💚 {skill.name}! HP +{actual_heal}"

    return result


def reduce_cooldowns(combat_state: Any) -> None:
    """턴 종료 시 쿨다운 감소"""
    keys_to_remove = []

    for key in combat_state.cooldowns:
        if key.startswith("skill_"):
            combat_state.cooldowns[key] -= 1
            if combat_state.cooldowns[key] <= 0:
                keys_to_remove.append(key)

    for key in keys_to_remove:
        del combat_state.cooldowns[key]


async def unlock_skills_for_level(player: Any, level: int) -> list[SkillData]:
    """레벨업 시 스킬 해금"""
    new_skills = await SkillRepository.get_unlockable_skills(player.class_type, level)

    for skill in new_skills:
        if skill.id not in player.skills:
            player.skills.append(skill.id)

    return new_skills
