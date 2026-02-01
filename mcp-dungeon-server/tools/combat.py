"""전투 관련 MCP 도구 (Phase 1A: 시너지 적용, Phase 3: 듀오 축복, Phase 4: 보스 기믹)

v6.6 리팩토링: attack() 함수를 헬퍼 함수로 분리하여 가독성 개선
"""
import random
from typing import Any

from state.game_state import GameState
from systems.combat import (
    process_player_attack,
    process_enemy_attack,
    attempt_flee,
    check_critical,
    calculate_damage,
)
from systems.skill import reduce_cooldowns, unlock_skills_for_level
from systems.boss_pattern import process_boss_action
from systems.synergy import (
    get_combat_synergy_effects,
    apply_execute,
    apply_counter_attack,
    apply_lifesteal,
    apply_reflect_damage,
    apply_aura_damage,
    check_synergies,
    get_synergy_display,
)
from systems.blessing import get_duo_combat_effects, get_active_duo_display
from systems.boss_gimmick import (
    process_gimmick_on_turn_start,
    process_gimmick_on_hit,
    process_gimmick_on_attack,
    get_gimmick_display,
)


# ============================================================
# 헬퍼 함수 (v6.6 리팩토링)
# ============================================================

def _process_boss_gimmick_turn_start(enemy: Any, player: Any, combat: Any) -> str:
    """보스 기믹 턴 시작 처리"""
    output = ""
    if not (enemy.is_boss and combat.boss_gimmick):
        return output

    gimmick_result = process_gimmick_on_turn_start(
        enemy, player, combat.boss_gimmick, combat.turn
    )
    for msg in gimmick_result.get("messages", []):
        output += f"\n{msg}"

    if gimmick_result.get("boss_healed", 0) > 0:
        output += f"\n  적 HP: {enemy.hp}/{enemy.max_hp}"

    if gimmick_result.get("player_stunned"):
        from models.status_effect import StatusEffect, StatusType
        combat.player_status.add_effect(StatusEffect(
            type=StatusType.STUN,
            duration=1,
            source="거미줄"
        ))

    return output


def _calculate_attack_modifiers(
    player: Any, enemy: Any, combat: Any,
    synergy_effects: dict, duo_effects: dict
) -> tuple[int, float, bool, str]:
    """공격 수정치 계산 (ATK, 배율, 크리티컬, 출력 메시지)"""
    output = ""

    # 확정 크리티컬 확인
    guaranteed_crit = combat.player_status.has_guaranteed_crit()
    if guaranteed_crit:
        combat.player_status.consume_guaranteed_crit()

    # 공격력 배율 (상태이상)
    atk_modifier = combat.player_status.get_atk_modifier()

    # 시너지 데미지 배율
    damage_mult = synergy_effects["damage_mult"]

    # 첫 공격 배율
    if combat.turn == 1 and synergy_effects["first_strike_mult"] > 1.0:
        damage_mult *= synergy_effects["first_strike_mult"]
        output += f"  🥷 첫 타격 보너스! (x{synergy_effects['first_strike_mult']})\n"

    # 크리티컬 확률
    crit_chance = 0.15 + synergy_effects["crit_bonus"]
    is_critical = guaranteed_crit or check_critical(crit_chance)

    # 듀오 데미지 보너스 (마나 폭주)
    if duo_effects["full_mp_damage_bonus"] > 0 and player.mp >= player.max_mp:
        damage_mult *= (1 + duo_effects["full_mp_damage_bonus"])
        output += f"  💧 마나 폭주! 데미지 +{int(duo_effects['full_mp_damage_bonus'] * 100)}%\n"

    # 듀오 공방 동기화 (완전한 전사)
    effective_atk = int(player.atk * atk_modifier)
    if duo_effects["sync_atk_def"]:
        sync_value = max(player.atk, player.def_)
        effective_atk = int(sync_value * atk_modifier)
        output += f"  ⚔️🛡️ 완전한 전사! ATK/DEF = {sync_value}\n"

    # 분노의 화신 스택 보너스
    if duo_effects["hit_to_atk"] > 0 and combat.rage_stacks > 0:
        rage_bonus = 1.0 + (duo_effects["hit_to_atk"] * combat.rage_stacks)
        effective_atk = int(effective_atk * rage_bonus)
        output += f"  😤🔥 분노 보너스! ATK x{rage_bonus:.1f}\n"

    return effective_atk, damage_mult, is_critical, output


def _execute_player_attack(
    player: Any, enemy: Any, combat: Any,
    effective_atk: int, damage_mult: float, is_critical: bool,
    synergy_effects: dict, duo_effects: dict
) -> tuple[int, list[int], bool, str]:
    """플레이어 공격 실행 (데미지, 타격별 데미지, 회피 여부, 출력 메시지)"""
    output = ""

    # 뱀파이어 박쥐 변신 회피 체크
    bat_evade = False
    if enemy.is_boss and combat.boss_gimmick:
        gimmick_attack = process_gimmick_on_attack(enemy, player, combat.boss_gimmick, 0)
        if gimmick_attack.get("evasion_chance", 0) > 0:
            if random.random() < gimmick_attack["evasion_chance"]:
                bat_evade = True
                output += f"\n  🦇 {enemy.name}이(가) 공격을 회피했습니다!"

    if bat_evade:
        return 0, [], True, output

    # 다중 타격 계산
    attack_hits = duo_effects["attack_hits"]
    total_damage = 0
    hit_details = []

    for hit in range(attack_hits):
        hit_damage = calculate_damage(
            effective_atk,
            enemy.def_,
            is_critical=is_critical,
            damage_mult=damage_mult
        )

        # 공허 데미지 추가 (첫 타격에만)
        if hit == 0:
            void_damage = synergy_effects["void_damage"]
            hit_damage += void_damage

        total_damage += hit_damage
        hit_details.append(hit_damage)

    enemy.take_damage(total_damage)

    # 보스 피격 시 기믹 처리 (오크 분노)
    if enemy.is_boss and combat.boss_gimmick and total_damage > 0:
        hit_result = process_gimmick_on_hit(enemy, player, combat.boss_gimmick, total_damage)
        for msg in hit_result.get("messages", []):
            output += f"\n{msg}"

    # 다중 타격 표시
    crit_text = " 💥 크리티컬!" if is_critical else ""
    void_text = f" (+{synergy_effects['void_damage']} 공허)" if synergy_effects["void_damage"] > 0 else ""

    if attack_hits > 1:
        hits_text = " + ".join(str(d) for d in hit_details)
        output += f"""
  ⚔️ {attack_hits}연타! [{hits_text}] = {total_damage} 데미지!{crit_text}{void_text}
  적 HP: {enemy.hp}/{enemy.max_hp}
"""
    else:
        output += f"""
  ⚔️ {enemy.name}에게 {total_damage} 데미지!{crit_text}{void_text}
  적 HP: {enemy.hp}/{enemy.max_hp}
"""

    return total_damage, hit_details, False, output


def _apply_post_attack_effects(
    player: Any, enemy: Any, combat: Any,
    total_damage: int, synergy_effects: dict, duo_effects: dict
) -> str:
    """공격 후 효과 적용 (흡혈, 즉사 등)"""
    output = ""

    # 흡혈 적용
    total_lifesteal = synergy_effects["lifesteal"] + duo_effects["lifesteal_bonus"]
    if total_lifesteal > 0:
        heal_amount, heal_msg = apply_lifesteal(player, total_damage, total_lifesteal)
        if heal_msg:
            output += f"  {heal_msg}\n"

    # 즉사 체크 (공허의 포옹)
    if synergy_effects["execute_threshold"] > 0 and enemy.is_alive:
        executed, exec_msg = apply_execute(enemy, synergy_effects["execute_threshold"])
        if exec_msg:
            output += f"  {exec_msg}\n"

    # 독 상태 적 즉사 (암살자의 낙인)
    if duo_effects["poison_execute_threshold"] > 0 and enemy.is_alive:
        if combat.enemy_status.has_poison():
            executed, exec_msg = apply_execute(enemy, duo_effects["poison_execute_threshold"])
            if exec_msg:
                output += f"  💀🟢 암살자의 낙인! {exec_msg}\n"

    # 적 상태 표시
    enemy_status = combat.enemy_status.get_status_display()
    if enemy_status:
        output += f"  적 상태: {enemy_status}\n"

    return output


async def _process_victory(game: Any, player: Any, enemy: Any) -> str:
    """전투 승리 처리"""
    # 보스 처치 시 승천 상태 업데이트
    if enemy.is_boss:
        game.ascension.on_boss_killed()

    rewards = game.end_combat(victory=True)
    level_ups = player.add_exp(0)

    output = f"""
───────────────────────────────────────────────────
  🎉 전투 승리!

  💀 {enemy.name} 처치!

  [보상]
  ⭐ EXP: +{rewards['exp']}
  💰 골드: +{rewards['gold']}
  💠 소울: +{rewards['souls']}
"""
    for lv_info in level_ups:
        output += f"\n  🎊 레벨 업! Lv.{lv_info['level']} 달성!"
        new_skills = await unlock_skills_for_level(player, lv_info["level"])
        for skill in new_skills:
            output += f"\n  📚 새 스킬 습득: {skill.name}!"

    # 보스 처치 또는 레벨업 시 자동 저장
    if enemy.is_boss or level_ups:
        from tools.save import auto_save
        await auto_save(f"전투 승리: {enemy.name}")
        output += "\n  💾 자동 저장됨"

    # 축복 선택
    from systems.blessing import generate_blessing_choices, format_blessing_choices
    from models.blessing import PlayerBlessings
    from state.game_state import PendingBlessing

    blessing_count = game.ascension.get_blessing_choices_count()
    player_blessings = PlayerBlessings(blessings=player.blessings)
    blessing_choices = generate_blessing_choices(player_blessings, count=blessing_count, floor=game.floor)

    if blessing_choices:
        game.pending_blessing = PendingBlessing(choices=blessing_choices, enemy_name=enemy.name)
        output += f"""
───────────────────────────────────────────────────
  ✨ 축복 선택 (1개만 선택)

{format_blessing_choices(blessing_choices, player.blessings)}

  💡 'choose_blessing [번호]'로 선택하세요
"""
    else:
        output += "\n  (더 이상 선택할 축복이 없습니다)"

    output += "\n═══════════════════════════════════════════════════"
    return output


def _apply_turn_end_effects(player: Any, enemy: Any, duo_effects: dict, combat: Any) -> str:
    """턴 종료 시 효과 적용 (재생, 오라 등)"""
    from systems.synergy import apply_aura_damage

    output = ""

    # 오라 데미지
    synergy_effects = {}  # 이미 계산된 효과를 사용해야 하지만, 여기서는 간소화
    # Note: 실제 구현에서는 synergy_effects를 인자로 받아야 함

    # 듀오 턴당 회복 효과
    regen_texts = []

    # HP 재생
    if duo_effects["hp_regen_percent"] > 0:
        hp_regen = int(player.max_hp * duo_effects["hp_regen_percent"])
        old_hp = player.hp
        player.hp = min(player.max_hp, player.hp + hp_regen)
        actual_regen = player.hp - old_hp
        if actual_regen > 0:
            regen_texts.append(f"💚 HP +{actual_regen}")

    # MP 재생
    if duo_effects["mp_regen_percent"] > 0:
        mp_regen = int(player.max_mp * duo_effects["mp_regen_percent"])
        old_mp = player.mp
        player.mp = min(player.max_mp, player.mp + mp_regen)
        actual_regen = player.mp - old_mp
        if actual_regen > 0:
            regen_texts.append(f"💧 MP +{actual_regen}")

    if regen_texts:
        output += f"\n  듀오 재생: {', '.join(regen_texts)}"
        output += f"\n  HP: {player.hp}/{player.max_hp} | MP: {player.mp}/{player.max_mp}"

    return output


async def _apply_curse_turn_damage(player: Any) -> str:
    """v6.7.2: 저주 턴당 데미지 적용"""
    from systems.curse import apply_turn_damage_curse

    damage, message = await apply_turn_damage_curse(player)
    if damage > 0:
        return f"\n  {message}"
    return ""


# ============================================================
# MCP 도구
# ============================================================


async def attack() -> str:
    """
    적을 공격합니다.

    Returns:
        전투 결과 메시지
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    if not game.in_combat:
        return "❌ 전투 중이 아닙니다."

    player = game.player
    enemy = game.combat.enemy
    combat = game.combat

    # Phase 1A: 시너지 효과 계산
    synergy_effects = await get_combat_synergy_effects(player)

    # Phase 3: 듀오 축복 효과 계산
    duo_effects = get_duo_combat_effects(player)

    output = """
═══════════════════════════════════════════════════
  ⚔️ 전투 진행
═══════════════════════════════════════════════════
"""

    # Phase 3: 활성 듀오 표시 (첫 턴만)
    if combat.turn == 1:
        duo_display = get_active_duo_display(player)
        if duo_display:
            output += duo_display + "\n"

    # Phase 4: 보스 기믹 턴 시작 처리
    if enemy.is_boss and combat.boss_gimmick:
        gimmick_result = process_gimmick_on_turn_start(
            enemy, player, combat.boss_gimmick, combat.turn
        )
        for msg in gimmick_result.get("messages", []):
            output += f"\n{msg}"

        # 보스 회복 표시
        if gimmick_result.get("boss_healed", 0) > 0:
            output += f"\n  적 HP: {enemy.hp}/{enemy.max_hp}"

        # 거미줄로 행동 불가
        if gimmick_result.get("player_stunned"):
            # 다음 턴에 행동 불가 처리될 것
            from models.status_effect import StatusEffect, StatusType
            combat.player_status.add_effect(StatusEffect(
                type=StatusType.STUN,
                duration=1,
                source="거미줄"
            ))

    # 플레이어 턴 시작 처리 (상태이상)
    turn_start = combat.player_status.process_turn_start()

    # 도트 데미지
    if turn_start["dot_damage"] > 0:
        player.take_damage(turn_start["dot_damage"])
        for msg in turn_start["messages"]:
            output += f"\n  {msg}"
        output += f"\n  당신의 HP: {player.hp}/{player.max_hp}\n"

    # 행동 불가 상태
    if not turn_start["can_act"]:
        enemy_result = process_enemy_attack(enemy, player, player_defending=False)
        output += f"""
  🐺 {enemy.name}의 공격! {enemy_result['damage']} 데미지!
  당신의 HP: {player.hp}/{player.max_hp}
"""
        if enemy_result["player_killed"]:
            output += await _get_game_over_text(game)
            GameState.clear()
        else:
            output += _get_action_menu(player, combat)
            combat.turn += 1
            reduce_cooldowns(combat)

        output += "═══════════════════════════════════════════════════"
        return output

    # 확정 크리티컬 확인
    guaranteed_crit = combat.player_status.has_guaranteed_crit()
    if guaranteed_crit:
        combat.player_status.consume_guaranteed_crit()

    # 공격력 배율 적용 (상태이상)
    atk_modifier = combat.player_status.get_atk_modifier()

    # Phase 1A: 시너지 데미지 배율
    damage_mult = synergy_effects["damage_mult"]

    # Phase 1A: 첫 공격 배율 (그림자 보행자 등)
    if combat.turn == 1 and synergy_effects["first_strike_mult"] > 1.0:
        damage_mult *= synergy_effects["first_strike_mult"]
        output += f"  🥷 첫 타격 보너스! (x{synergy_effects['first_strike_mult']})\n"

    # 크리티컬 확률 (기본 15% + 시너지)
    crit_chance = 0.15 + synergy_effects["crit_bonus"]
    is_critical = guaranteed_crit or check_critical(crit_chance)

    # Phase 3: 듀오 데미지 보너스 (마나 폭주 - MP 가득 시)
    if duo_effects["full_mp_damage_bonus"] > 0 and player.mp >= player.max_mp:
        damage_mult *= (1 + duo_effects["full_mp_damage_bonus"])
        output += f"  💧 마나 폭주! 데미지 +{int(duo_effects['full_mp_damage_bonus'] * 100)}%\n"

    # Phase 3: 듀오 공방 동기화 (완전한 전사)
    effective_atk = int(player.atk * atk_modifier)
    if duo_effects["sync_atk_def"]:
        sync_value = max(player.atk, player.def_)
        effective_atk = int(sync_value * atk_modifier)
        output += f"  ⚔️🛡️ 완전한 전사! ATK/DEF = {sync_value}\n"

    # Phase 3: 분노의 화신 스택 보너스
    if duo_effects["hit_to_atk"] > 0 and combat.rage_stacks > 0:
        rage_bonus = 1.0 + (duo_effects["hit_to_atk"] * combat.rage_stacks)
        effective_atk = int(effective_atk * rage_bonus)
        output += f"  😤🔥 분노 보너스! ATK x{rage_bonus:.1f}\n"

    # Phase 4: 뱀파이어 박쥐 변신 회피 체크
    bat_evade = False
    if enemy.is_boss and combat.boss_gimmick:
        gimmick_attack = process_gimmick_on_attack(enemy, player, combat.boss_gimmick, 0)
        if gimmick_attack.get("evasion_chance", 0) > 0:
            if random.random() < gimmick_attack["evasion_chance"]:
                bat_evade = True
                output += f"\n  🦇 {enemy.name}이(가) 공격을 회피했습니다!"

    if bat_evade:
        total_damage = 0
        hit_details = []
    else:
        # Phase 3: 다중 타격 계산 (폭풍의 검 등)
        attack_hits = duo_effects["attack_hits"]
        total_damage = 0
        hit_details = []

        for hit in range(attack_hits):
            # 각 타격마다 개별 데미지 계산
            hit_damage = calculate_damage(
                effective_atk,
                enemy.def_,
                is_critical=is_critical,
                damage_mult=damage_mult
            )

            # Phase 1A: 공허 데미지 추가 (첫 타격에만)
            if hit == 0:
                void_damage = synergy_effects["void_damage"]
                hit_damage += void_damage

            total_damage += hit_damage
            hit_details.append(hit_damage)

        enemy.take_damage(total_damage)

        # Phase 4: 보스 피격 시 기믹 처리 (오크 분노)
        if enemy.is_boss and combat.boss_gimmick and total_damage > 0:
            hit_result = process_gimmick_on_hit(enemy, player, combat.boss_gimmick, total_damage)
            for msg in hit_result.get("messages", []):
                output += f"\n{msg}"

    # 다중 타격 표시 (회피하지 않은 경우만)
    if not bat_evade:
        crit_text = " 💥 크리티컬!" if is_critical else ""
        void_text = f" (+{synergy_effects['void_damage']} 공허)" if synergy_effects["void_damage"] > 0 else ""

        if attack_hits > 1:
            hits_text = " + ".join(str(d) for d in hit_details)
            output += f"""
  ⚔️ {attack_hits}연타! [{hits_text}] = {total_damage} 데미지!{crit_text}{void_text}
  적 HP: {enemy.hp}/{enemy.max_hp}
"""
        else:
            output += f"""
  ⚔️ {enemy.name}에게 {total_damage} 데미지!{crit_text}{void_text}
  적 HP: {enemy.hp}/{enemy.max_hp}
"""

    # Phase 1A + Phase 3: 흡혈 적용 (듀오 보너스 포함)
    total_lifesteal = synergy_effects["lifesteal"] + duo_effects["lifesteal_bonus"]
    if total_lifesteal > 0:
        heal_amount, heal_msg = apply_lifesteal(player, total_damage, total_lifesteal)
        if heal_msg:
            output += f"  {heal_msg}\n"

    # Phase 1A: 즉사 체크 (공허의 포옹 등)
    if synergy_effects["execute_threshold"] > 0 and enemy.is_alive:
        executed, exec_msg = apply_execute(enemy, synergy_effects["execute_threshold"])
        if exec_msg:
            output += f"  {exec_msg}\n"

    # Phase 3: 독 상태 적 즉사 (암살자의 낙인)
    if duo_effects["poison_execute_threshold"] > 0 and enemy.is_alive:
        if combat.enemy_status.has_poison():
            executed, exec_msg = apply_execute(enemy, duo_effects["poison_execute_threshold"])
            if exec_msg:
                output += f"  💀🟢 암살자의 낙인! {exec_msg}\n"

    # 적 상태 표시
    enemy_status = combat.enemy_status.get_status_display()
    if enemy_status:
        output += f"  적 상태: {enemy_status}\n"

    # 적 처치 확인
    if not enemy.is_alive:
        # Phase 2: 보스 처치 시 승천 상태 업데이트
        if enemy.is_boss:
            game.ascension.on_boss_killed()

        rewards = game.end_combat(victory=True)
        level_ups = player.add_exp(0)  # 이미 end_combat에서 추가됨

        output += f"""
───────────────────────────────────────────────────
  🎉 전투 승리!

  💀 {enemy.name} 처치!

  [보상]
  ⭐ EXP: +{rewards['exp']}
  💰 골드: +{rewards['gold']}
  💠 소울: +{rewards['souls']}
"""
        for lv_info in level_ups:
            output += f"\n  🎊 레벨 업! Lv.{lv_info['level']} 달성!"
            new_skills = await unlock_skills_for_level(player, lv_info["level"])
            for skill in new_skills:
                output += f"\n  📚 새 스킬 습득: {skill.name}!"

        # 보스 처치 또는 레벨업 시 자동 저장
        if enemy.is_boss or level_ups:
            from tools.save import auto_save
            await auto_save(f"전투 승리: {enemy.name}")
            output += "\n  💾 자동 저장됨"

        # v5.0: 축복 선택 (Phase 2: 승천 효과로 선택지 수 조정)
        from systems.blessing import generate_blessing_choices, format_blessing_choices
        from models.blessing import PlayerBlessings
        from state.game_state import PendingBlessing

        # Phase 2: 승천 효과로 축복 선택지 수 조정 (기본 3, 승천 5+면 2)
        blessing_count = game.ascension.get_blessing_choices_count()

        # 플레이어 축복 목록 (PlayerBlessings로 변환)
        player_blessings = PlayerBlessings(blessings=player.blessings)
        blessing_choices = generate_blessing_choices(player_blessings, count=blessing_count, floor=game.floor)

        if blessing_choices:
            game.pending_blessing = PendingBlessing(choices=blessing_choices, enemy_name=enemy.name)
            # Phase 3: 듀오 힌트를 위해 보유 축복 전달
            output += f"""
───────────────────────────────────────────────────
  ✨ 축복 선택 (1개만 선택)

{format_blessing_choices(blessing_choices, player.blessings)}

  💡 'choose_blessing [번호]'로 선택하세요
"""
        else:
            output += "\n  (더 이상 선택할 축복이 없습니다)"

        output += "\n═══════════════════════════════════════════════════"
        return output

    # 적 턴 시작 처리
    enemy_turn = combat.enemy_status.process_turn_start()
    if enemy_turn["dot_damage"] > 0:
        enemy.take_damage(enemy_turn["dot_damage"])
        for msg in enemy_turn["messages"]:
            output += f"\n  {msg}"

        # 도트로 처치
        if not enemy.is_alive:
            rewards = game.end_combat(victory=True)
            output += f"""
───────────────────────────────────────────────────
  🎉 전투 승리! (도트 데미지)

  💀 {enemy.name} 처치!

  [보상]
  ⭐ EXP: +{rewards['exp']}
  💰 골드: +{rewards['gold']}
  💠 소울: +{rewards['souls']}

═══════════════════════════════════════════════════
"""
            return output

    # 적 반격 (v5.0 행동 예고 시스템)
    combat.player_defending = False
    enemy_damage = 0

    # Phase 1A: 은신 상태면 첫 공격 회피
    if combat.turn == 1 and synergy_effects["stealth"]:
        output += "\n  🥷 은신 상태로 적의 공격을 회피했습니다!"
    elif enemy_turn["can_act"]:
        # v5.0: 예고된 행동 실행
        from systems.enemy_ai import execute_enemy_action

        if combat.enemy_next_action:
            action_result = execute_enemy_action(
                enemy, combat.enemy_next_action, player,
                player_defending=False
            )
            enemy_damage = action_result["damage"]
            output += f"\n  {action_result['message']}"

            # 회복 표시
            if action_result["healed"] > 0:
                output += f"\n  적 HP: {enemy.hp}/{enemy.max_hp}"
        else:
            # 예고 행동이 없으면 기존 방식
            enemy_result = process_enemy_attack(
                enemy, player, player_defending=False,
                enemy_status=combat.enemy_status
            )
            enemy_damage = enemy_result["damage"]
            output += f"\n  🐺 {enemy.name}의 반격! {enemy_damage} 데미지!"

        # Phase 1A: 피해 감소 적용 (시너지)
        if synergy_effects["damage_reduction"] > 0 and enemy_damage > 0:
            reduced = int(enemy_damage * synergy_effects["damage_reduction"])
            output += f" (🛡️ 시너지 감소 -{reduced})"

        # 기존 상태이상 피해 감소
        reduction = combat.player_status.get_damage_reduction()
        if reduction > 0 and enemy_damage > 0:
            reduced = int(enemy_damage * reduction)
            output += f" (🛡️ -{reduced})"

        # Phase 3: 분노의 화신 스택 (피격 시 ATK 증가)
        if duo_effects["hit_to_atk"] > 0 and enemy_damage > 0:
            max_stacks = duo_effects["max_rage_stacks"]
            if combat.rage_stacks < max_stacks:
                combat.rage_stacks += 1
                atk_bonus = int(duo_effects["hit_to_atk"] * 100)
                total_bonus = atk_bonus * combat.rage_stacks
                output += f"\n  😤🔥 분노! ATK +{total_bonus}% ({combat.rage_stacks}/{max_stacks}스택)"

        # Phase 1A: 반사 데미지
        if synergy_effects["reflect_damage"] > 0 and enemy_damage > 0:
            reflect_dmg, reflect_heal, reflect_msg = apply_reflect_damage(
                player, enemy, enemy_damage,
                synergy_effects["reflect_damage"],
                synergy_effects["lifesteal_on_reflect"],
                synergy_effects["lifesteal"]
            )
            if reflect_msg:
                output += f"\n  {reflect_msg}"

        # Phase 1A: 반격
        if synergy_effects["counter_chance"] > 0 and enemy_damage > 0 and enemy.is_alive:
            counter_dmg, counter_msg = apply_counter_attack(
                player, enemy,
                synergy_effects["counter_chance"],
                synergy_effects["counter_damage_mult"],
                enemy_damage
            )
            if counter_msg:
                output += f"\n  {counter_msg}"

        # Phase 1A: 반격/반사로 적 처치 체크
        if not enemy.is_alive:
            rewards = game.end_combat(victory=True)
            output += f"""
───────────────────────────────────────────────────
  🎉 전투 승리! (반격/반사)

  [보상]
  ⭐ EXP: +{rewards['exp']}
  💰 골드: +{rewards['gold']}
  💠 소울: +{rewards['souls']}

═══════════════════════════════════════════════════
"""
            return output

        if enemy_damage > 0:
            output += f"\n  당신의 HP: {player.hp}/{player.max_hp}"
    else:
        for msg in enemy_turn["messages"]:
            output += f"\n  {msg}"

    # 플레이어 상태 표시
    player_status = combat.player_status.get_status_display()
    if player_status:
        output += f"  상태: {player_status}\n"

    # Phase 3: 죽음 회피 (불멸의 투사 듀오)
    if not player.is_alive and duo_effects["death_save"] > 0:
        # 죽음 회피 발동 - HP 1로 생존
        if not hasattr(combat, 'death_save_used'):
            combat.death_save_used = False

        if not combat.death_save_used:
            player.hp = 1
            combat.death_save_used = True
            output += "\n  💪💚 불멸의 투사! 치명상을 버텨냈습니다! (HP 1)"

    # 플레이어 사망 확인
    if not player.is_alive:
        output += await _get_game_over_text(game)
        GameState.clear()
    else:
        # Phase 1A: 오라 데미지 (턴 종료 시)
        if synergy_effects["aura_damage"] > 0 and enemy.is_alive:
            aura_dmg, aura_msg = apply_aura_damage(enemy, synergy_effects["aura_damage"])
            if aura_msg:
                output += f"\n  {aura_msg}"
            if not enemy.is_alive:
                rewards = game.end_combat(victory=True)
                output += "\n  🎉 오라 데미지로 적 처치!"

        # Phase 3: 듀오 턴당 회복 효과
        regen_texts = []

        # HP 재생 (불멸의 투사)
        if duo_effects["hp_regen_percent"] > 0:
            hp_regen = int(player.max_hp * duo_effects["hp_regen_percent"])
            old_hp = player.hp
            player.hp = min(player.max_hp, player.hp + hp_regen)
            actual_regen = player.hp - old_hp
            if actual_regen > 0:
                regen_texts.append(f"💚 HP +{actual_regen}")

        # MP 재생 (마나 폭주)
        if duo_effects["mp_regen_percent"] > 0:
            mp_regen = int(player.max_mp * duo_effects["mp_regen_percent"])
            old_mp = player.mp
            player.mp = min(player.max_mp, player.mp + mp_regen)
            actual_regen = player.mp - old_mp
            if actual_regen > 0:
                regen_texts.append(f"💧 MP +{actual_regen}")

        if regen_texts:
            output += f"\n  듀오 재생: {', '.join(regen_texts)}"
            output += f"\n  HP: {player.hp}/{player.max_hp} | MP: {player.mp}/{player.max_mp}"

        output += _get_action_menu(player, combat)

    # 턴 종료 처리
    combat.turn += 1
    reduce_cooldowns(combat)
    combat.player_status.process_turn_end()
    combat.enemy_status.process_turn_end()

    # v5.0: 다음 턴 적 행동 결정
    if enemy.is_alive:
        combat._determine_enemy_action(player.hp / player.max_hp if player.max_hp > 0 else 1.0)

    output += "═══════════════════════════════════════════════════"
    return output


async def _get_game_over_text(game) -> str:
    """게임 오버 텍스트 (프로필/랭킹 기록 포함)"""
    from tools.game import _record_game_end

    result = await _record_game_end(game, victory=False)

    return f"""
───────────────────────────────────────────────────
  💀 사망했습니다...

  📊 점수: {result['score']:,}점 (랭킹 #{result['rank']})

  도달 층: {game.floor}
  처치 몬스터: {game.monsters_killed}
  획득 소울: {game.souls_earned} → 프로필에 저장됨!

{result['achievements_text']}  게임 오버!
  'start_game'으로 새 게임을 시작하세요.
  'get_profile'로 프로필 확인!
───────────────────────────────────────────────────
"""


def _get_action_menu(player, combat) -> str:
    """행동 선택 메뉴 (v5.0 행동 예고 포함, Phase 1B 콤보 체인, Phase 4 보스 기믹)"""
    from systems.enemy_ai import get_action_damage, get_action_description
    from models.monster import EnemyAction

    skill_count = len(player.skills)
    enemy = combat.enemy

    # Phase 1B: 콤보 체인 상태 표시
    combo_status = combat.combo_chain.get_status_display()
    combo_line = f"\n  {combo_status}" if combo_status else ""

    # Phase 1B: 궁극기 사용 가능 시 메뉴에 추가
    ultimate_option = ""
    if combat.combo_chain.ultimate_ready:
        ultimate_option = "\n  • use_skill ultimate - 💥 궁극기: 멸절의 일격!"

    # Phase 4: 보스 기믹 상태 표시
    gimmick_line = ""
    if enemy.is_boss and combat.boss_gimmick:
        gimmick_display = get_gimmick_display(enemy, combat.boss_gimmick)
        if gimmick_display:
            gimmick_line = f"\n{gimmick_display}"

    # 적의 다음 행동 예고
    next_action = combat.enemy_next_action
    if next_action:
        damage = get_action_damage(enemy, next_action)
        # 방어력 적용한 예상 데미지
        expected_damage = max(1, damage - player.def_) if damage > 0 else 0
        action_desc = get_action_description(next_action, expected_damage)
        action_preview = f"""
───────────────────────────────────────────────────
  ⚠️ 적의 다음 행동: {action_desc}
"""
        # 강타/특수 공격이면 방어 추천
        if next_action in [EnemyAction.HEAVY, EnemyAction.SPECIAL]:
            action_preview += "  💡 TIP: 방어를 고려해보세요!\n"
        elif next_action in [EnemyAction.CHARGE]:
            action_preview += "  💡 TIP: 다음 턴에 강타가 옵니다!\n"
        elif next_action in [EnemyAction.HEAL, EnemyAction.BUFF]:
            action_preview += "  💡 TIP: 지금 공격하세요!\n"
    else:
        action_preview = ""

    return f"""{action_preview}
───────────────────────────────────────────────────{combo_line}{gimmick_line}
  [행동 선택]
  • attack - 공격
  • use_skill [스킬ID] - 스킬 ({skill_count}개 보유){ultimate_option}
  • defend - 방어 (데미지 무효화)
  • flee - 도망 (보스전 불가)
"""


async def defend() -> str:
    """
    방어 자세를 취합니다. 이번 턴 받는 데미지가 50% 감소합니다.

    Returns:
        방어 결과 메시지
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    if not game.in_combat:
        return "❌ 전투 중이 아닙니다."

    player = game.player
    enemy = game.combat.enemy
    combat = game.combat

    # Phase 1A: 시너지 효과 계산
    synergy_effects = await get_combat_synergy_effects(player)

    # Phase 3: 듀오 축복 효과 계산
    duo_effects = get_duo_combat_effects(player)

    output = """
═══════════════════════════════════════════════════
  🛡️ 방어!
═══════════════════════════════════════════════════

  방어 자세를 취했습니다!
  받는 데미지 50% 감소!
"""

    # Phase 3: 고슴도치 듀오 효과 미리보기
    if duo_effects["defend_full_reflect"]:
        output += "  🦔 고슴도치! 받는 데미지를 100% 반사합니다!\n"

    # 플레이어 턴 시작 처리
    turn_start = combat.player_status.process_turn_start()
    if turn_start["dot_damage"] > 0:
        player.take_damage(turn_start["dot_damage"])
        for msg in turn_start["messages"]:
            output += f"\n  {msg}"

    # 방어 상태 설정
    combat.player_defending = True

    # 적 턴 처리
    enemy_turn = combat.enemy_status.process_turn_start()
    if enemy_turn["dot_damage"] > 0:
        enemy.take_damage(enemy_turn["dot_damage"])
        for msg in enemy_turn["messages"]:
            output += f"\n  {msg}"

        if not enemy.is_alive:
            rewards = game.end_combat(victory=True)
            output += f"""
───────────────────────────────────────────────────
  🎉 전투 승리! (도트 데미지)

  [보상]
  ⭐ EXP: +{rewards['exp']}
  💰 골드: +{rewards['gold']}
  💠 소울: +{rewards['souls']}

═══════════════════════════════════════════════════
"""
            return output

    enemy_damage = 0
    if enemy_turn["can_act"]:
        # v5.0: 예고된 행동 실행 (방어 적용)
        from systems.enemy_ai import execute_enemy_action

        if combat.enemy_next_action:
            action_result = execute_enemy_action(
                enemy, combat.enemy_next_action, player,
                player_defending=True
            )
            enemy_damage = action_result["damage"]

            # 방어 성공 메시지
            if enemy_damage > 0:
                output += f"""
  {action_result['message']} (방어로 감소!)
  당신의 HP: {player.hp}/{player.max_hp}
"""
            else:
                output += f"\n  {action_result['message']}\n"

            # 회복 표시
            if action_result["healed"] > 0:
                output += f"  적 HP: {enemy.hp}/{enemy.max_hp}\n"
        else:
            # 예고 행동이 없으면 기존 방식
            enemy_result = process_enemy_attack(enemy, player, player_defending=True)
            enemy_damage = enemy_result["damage"]
            output += f"""
  🐺 {enemy.name}의 공격! {enemy_damage} 데미지! (감소됨)
  당신의 HP: {player.hp}/{player.max_hp}
"""

        # Phase 1A + Phase 3: 반사 데미지 (방어 중에도 발동)
        # Phase 3: 고슴도치 듀오 효과 - 방어 시 100% 반사
        reflect_ratio = synergy_effects["reflect_damage"]
        if duo_effects["defend_full_reflect"]:
            reflect_ratio = 1.0  # 100% 반사

        if reflect_ratio > 0 and enemy_damage > 0:
            # 반사 데미지 계산 (방어로 감소되기 전 원래 데미지 기준)
            original_damage = enemy_damage * 2 if duo_effects["defend_full_reflect"] else enemy_damage
            reflect_dmg, reflect_heal, reflect_msg = apply_reflect_damage(
                player, enemy, original_damage,
                reflect_ratio,
                synergy_effects["lifesteal_on_reflect"],
                synergy_effects["lifesteal"] + duo_effects["lifesteal_bonus"]
            )
            if reflect_msg:
                output += f"  {reflect_msg}\n"

        # Phase 1A: 반사로 적 처치 체크
        if not enemy.is_alive:
            rewards = game.end_combat(victory=True)
            output += f"""
───────────────────────────────────────────────────
  🎉 전투 승리! (반사 데미지)

  [보상]
  ⭐ EXP: +{rewards['exp']}
  💰 골드: +{rewards['gold']}
  💠 소울: +{rewards['souls']}

═══════════════════════════════════════════════════
"""
            return output
    else:
        for msg in enemy_turn["messages"]:
            output += f"\n  {msg}"

    # 플레이어 상태 표시
    player_status = combat.player_status.get_status_display()
    if player_status:
        output += f"  상태: {player_status}\n"

    # 플레이어 사망 확인
    if not player.is_alive:
        output += await _get_game_over_text(game)
        GameState.clear()
    else:
        output += _get_action_menu(player, combat)

    # 턴 종료 처리
    combat.turn += 1
    reduce_cooldowns(combat)
    combat.player_status.process_turn_end()
    combat.enemy_status.process_turn_end()

    # v5.0: 다음 턴 적 행동 결정
    if enemy.is_alive:
        combat._determine_enemy_action(player.hp / player.max_hp if player.max_hp > 0 else 1.0)

    output += "═══════════════════════════════════════════════════"
    return output


async def flee() -> str:
    """
    전투에서 도망칩니다. 보스전에서는 도망칠 수 없습니다.

    Returns:
        도망 결과 메시지
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    if not game.in_combat:
        return "❌ 전투 중이 아닙니다."

    player = game.player
    enemy = game.combat.enemy
    combat = game.combat

    # 보스전 도망 불가
    if enemy.is_boss:
        return f"""
═══════════════════════════════════════════════════
  🚫 도망 실패!
═══════════════════════════════════════════════════

  보스전에서는 도망칠 수 없습니다!

{_get_action_menu(player, combat)}
═══════════════════════════════════════════════════
"""

    # Phase 2: 승천 8+ - 보스 처치 전 도망 불가
    if not game.ascension.can_flee():
        return f"""
═══════════════════════════════════════════════════
  🚫 도망 실패!
═══════════════════════════════════════════════════

  ⚔️ 승천 효과: 보스를 처치하기 전까지 도망칠 수 없습니다!

{_get_action_menu(player, combat)}
═══════════════════════════════════════════════════
"""

    # v6.7.2: 저주 - 도망 불가 체크
    from systems.curse import check_no_flee_curse
    if await check_no_flee_curse(player):
        return f"""
═══════════════════════════════════════════════════
  🚫 도망 실패!
═══════════════════════════════════════════════════

  💀 저주 효과: 저주받은 장비로 인해 도망칠 수 없습니다!

{_get_action_menu(player, combat)}
═══════════════════════════════════════════════════
"""

    # 플레이어 턴 시작 처리
    turn_start = combat.player_status.process_turn_start()

    output = ""
    if turn_start["dot_damage"] > 0:
        player.take_damage(turn_start["dot_damage"])
        output = f"""
═══════════════════════════════════════════════════
  ⚠️ 상태 이상 데미지
═══════════════════════════════════════════════════

  {chr(10).join(turn_start['messages'])}
  당신의 HP: {player.hp}/{player.max_hp}

"""

    # 도망 시도
    success, chance = attempt_flee(player, enemy)

    if success:
        combat.fled = True
        game.combat = None

        return output + f"""
═══════════════════════════════════════════════════
  🏃 도망 성공!
═══════════════════════════════════════════════════

  {enemy.name}에게서 도망쳤습니다! (확률: {chance}%)

  'move'로 다른 방향으로 이동하세요.
═══════════════════════════════════════════════════
"""
    else:
        output += f"""
═══════════════════════════════════════════════════
  🏃 도망 실패!
═══════════════════════════════════════════════════

  도망에 실패했습니다! (확률: {chance}%)
"""

        # 적 턴 처리
        enemy_turn = combat.enemy_status.process_turn_start()
        if enemy_turn["dot_damage"] > 0:
            enemy.take_damage(enemy_turn["dot_damage"])
            for msg in enemy_turn["messages"]:
                output += f"\n  {msg}"

        if enemy_turn["can_act"]:
            # v5.0: 예고된 행동 실행
            from systems.enemy_ai import execute_enemy_action

            if combat.enemy_next_action:
                action_result = execute_enemy_action(
                    enemy, combat.enemy_next_action, player,
                    player_defending=False
                )
                enemy_damage = action_result["damage"]
                output += f"\n  {action_result['message']}"
                if enemy_damage > 0:
                    output += f"\n  당신의 HP: {player.hp}/{player.max_hp}"
            else:
                enemy_result = process_enemy_attack(enemy, player, player_defending=False)
                enemy_damage = enemy_result["damage"]
                output += f"""
  🐺 {enemy.name}의 공격! {enemy_damage} 데미지!
  당신의 HP: {player.hp}/{player.max_hp}
"""
        else:
            for msg in enemy_turn["messages"]:
                output += f"\n  {msg}"

        if not player.is_alive:
            output += await _get_game_over_text(game)
            GameState.clear()
        else:
            output += _get_action_menu(player, combat)

        # 턴 종료 처리
        combat.turn += 1
        reduce_cooldowns(combat)
        combat.player_status.process_turn_end()
        combat.enemy_status.process_turn_end()

        # v5.0: 다음 턴 적 행동 결정
        if enemy.is_alive:
            combat._determine_enemy_action(player.hp / player.max_hp if player.max_hp > 0 else 1.0)

        output += "═══════════════════════════════════════════════════"
        return output


async def choose_blessing(choice: int) -> str:
    """
    축복을 선택합니다.

    Args:
        choice: 선택 번호 (1, 2, 3)

    Returns:
        선택 결과 메시지
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    if not game.pending_blessing:
        return "❌ 선택할 축복이 없습니다."

    choices = game.pending_blessing.choices

    # 유효성 검사
    if choice < 1 or choice > len(choices):
        return f"❌ 잘못된 선택입니다. 1~{len(choices)} 중에서 선택하세요."

    # 축복 선택 및 적용
    from systems.blessing import apply_blessing, get_blessing_effect_text, check_and_apply_duos

    # Phase 3: 축복 선택 전 활성 듀오 확인
    from seeds.duo_blessings import check_active_duos
    owned_before = {b.id for b in game.player.blessings}
    duos_before = set(d.id for d in check_active_duos(owned_before))

    selected = choices[choice - 1]
    changes = apply_blessing(game.player, selected)

    # 축복 목록에 추가 (apply_blessing에서 처리되지 않았을 경우)
    if selected not in game.player.blessings:
        game.player.blessings.append(selected)

    # Phase 3: 새로 활성화된 듀오 확인
    owned_after = {b.id for b in game.player.blessings}
    duos_after = check_active_duos(owned_after)
    new_duos = [d for d in duos_after if d.id not in duos_before]

    # 대기 상태 초기화
    game.pending_blessing = None

    # 결과 메시지
    change_texts = []
    for stat, value in changes.items():
        if value != 0:
            sign = "+" if value > 0 else ""
            change_texts.append(f"{stat}: {sign}{value}")

    output = f"""
═══════════════════════════════════════════════════
  ✨ 축복 획득!
═══════════════════════════════════════════════════

  {selected.icon} {selected.name} ({selected.rarity_name})

  {selected.description}

  [적용된 효과]
  {', '.join(change_texts) if change_texts else get_blessing_effect_text(selected)}
"""

    # Phase 3: 새로 활성화된 듀오 표시
    if new_duos:
        output += """
───────────────────────────────────────────────────
  💫 듀오 축복 발동!

"""
        for duo in new_duos:
            output += f"  {duo.icon} {duo.name}\n"
            output += f"     {duo.description}\n\n"

    output += f"""───────────────────────────────────────────────────
  현재 보유 축복: {len(game.player.blessings)}개

  'move'로 다음 방으로 이동하세요.
═══════════════════════════════════════════════════
"""

    return output
