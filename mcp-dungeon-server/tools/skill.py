"""스킬 관련 MCP 도구"""
from state.game_state import GameState
from systems.skill import (
    use_skill as _use_skill,
    can_use_skill,
    get_available_skills,
    reduce_cooldowns,
    unlock_skills_for_level,
)
from systems.combat import process_enemy_attack
from repository.skill_repo import SkillRepository


async def get_skills() -> str:
    """
    보유한 스킬 목록을 확인합니다.

    Returns:
        스킬 목록
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    player = game.player

    if not player.skills:
        return """
═══════════════════════════════════════════════════
  📚 스킬 목록
═══════════════════════════════════════════════════

  보유한 스킬이 없습니다.
  레벨업하면 새로운 스킬을 습득합니다.

═══════════════════════════════════════════════════
"""

    skills = await get_available_skills(player)

    # 전투 중이면 쿨다운 표시
    cooldowns = {}
    if game.combat:
        cooldowns = game.combat.cooldowns

    # Phase 3: 듀오 MP 소모 감소 (아크메이지)
    from systems.blessing import get_duo_combat_effects
    duo_effects = get_duo_combat_effects(player)
    mp_cost_mult = duo_effects.get("skill_mp_cost_mult", 1.0)
    skill_damage_mult = duo_effects.get("skill_damage_mult", 1.0)

    skill_lines = []
    for skill in skills:
        icon = skill.get_icon()
        cooldown_key = f"skill_{skill.id}"
        cooldown_left = cooldowns.get(cooldown_key, 0)

        # 쿨다운 표시
        if cooldown_left > 0:
            cd_text = f" [🔄 {cooldown_left}턴]"
        elif skill.cooldown > 0:
            cd_text = f" [CD: {skill.cooldown}]"
        else:
            cd_text = ""

        # Phase 3: 듀오 MP 소모 감소 적용
        actual_mp_cost = int(skill.mp_cost * mp_cost_mult)

        # MP 사용 가능 여부
        mp_ok = "✓" if player.mp >= actual_mp_cost else "✗"

        skill_lines.append(f"  {icon} {skill.name}{cd_text}")

        # 듀오 효과 표시
        if mp_cost_mult < 1.0:
            skill_lines.append(f"      ID: {skill.id} | 💧 MP: {actual_mp_cost} (원가: {skill.mp_cost}) [{mp_ok}]")
        else:
            skill_lines.append(f"      ID: {skill.id} | 💧 MP: {skill.mp_cost} [{mp_ok}]")

        skill_lines.append(f"      {skill.description}")
        skill_lines.append("")

    return f"""
═══════════════════════════════════════════════════
  📚 스킬 목록 ({player.class_name})
═══════════════════════════════════════════════════

  💧 MP: {player.mp}/{player.max_mp}

{''.join(skill_lines)}
───────────────────────────────────────────────────
  💡 사용법: use_skill [스킬ID]
═══════════════════════════════════════════════════
"""


async def use_skill(skill_id: str) -> str:
    """
    스킬을 사용합니다.

    Args:
        skill_id: 스킬 ID

    Returns:
        스킬 사용 결과
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    if not game.in_combat:
        return "❌ 전투 중이 아닙니다. 스킬은 전투 중에만 사용할 수 있습니다."

    player = game.player
    enemy = game.combat.enemy
    combat = game.combat

    # Phase 1B: 궁극기 처리
    if skill_id == "ultimate":
        return await _use_ultimate(game, player, enemy, combat)

    # 사용 가능 여부 확인
    can_use, reason = await can_use_skill(player, skill_id, combat, combat.turn)
    if not can_use:
        return f"❌ {reason}"

    # 플레이어 턴 시작 처리 (상태이상)
    turn_start = combat.player_status.process_turn_start()

    # 도트 데미지 처리
    if turn_start["dot_damage"] > 0:
        player.take_damage(turn_start["dot_damage"])

    # 행동 불가 상태 확인
    if not turn_start["can_act"]:
        # 적 턴
        enemy_result = process_enemy_attack(enemy, player, player_defending=False)

        output = f"""
═══════════════════════════════════════════════════
  ⚠️ 행동 불가!
═══════════════════════════════════════════════════

  {chr(10).join(turn_start['messages'])}

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

    # 스킬 사용
    result = await _use_skill(
        player, enemy, skill_id, combat,
        combat.player_status, combat.enemy_status
    )

    # v5.0: 스킬 기록 추가
    combat.skill_history.append(skill_id)

    # v5.0: 콤보 체크
    from systems.combo import check_combo, apply_combo_effect, get_combo_hint, clear_combo_history
    combo = check_combo(combat.skill_history)

    combo_text = ""
    if combo:
        # 콤보 효과 적용
        result.damage, combo_messages = apply_combo_effect(
            combo, result.damage, player, enemy
        )
        combo_text = f"\n  🔥 {chr(10).join(combo_messages)}\n"

        # Phase 1B: 콤보 체인 보상 적용
        chain_msg, chain_reward = combat.combo_chain.on_combo_success(player)
        combo_text += f"  {chain_msg}\n"

        # 콤보 발동 후 기록 초기화
        combat.skill_history = []
    else:
        # Phase 1B: 콤보 실패 시 체인 리셋
        combat.combo_chain.on_combo_fail()

        # 콤보 힌트 표시
        hint = get_combo_hint(combat.skill_history, player.skills)
        if hint:
            combo_text = f"\n  {hint}\n"

    # 스킬 기록 정리
    combat.skill_history = clear_combo_history(combat.skill_history)

    output = f"""
═══════════════════════════════════════════════════
  ✨ 스킬 사용!
═══════════════════════════════════════════════════

  {result.message}{combo_text}
  💧 MP 소모: {result.mp_cost} (남은 MP: {player.mp})
"""

    # 부가 효과 표시
    if result.status_applied:
        output += f"\n  {' | '.join(result.status_applied)}\n"

    # 회복 표시
    if result.heal > 0:
        output += f"\n  💚 HP +{result.heal} (현재: {player.hp}/{player.max_hp})\n"

    # 적 처치 확인
    if result.enemy_killed:
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
        # 레벨업 처리
        for lv_info in level_ups:
            output += f"\n  🎊 레벨 업! Lv.{lv_info['level']} 달성!"
            # 스킬 해금
            new_skills = await unlock_skills_for_level(player, lv_info["level"])
            for skill in new_skills:
                output += f"\n  📚 새 스킬 습득: {skill.name}!"

        output += "\n═══════════════════════════════════════════════════"
        return output

    # 적 HP 표시
    output += f"\n  적 HP: {enemy.hp}/{enemy.max_hp}\n"

    # 적 상태 이상 표시
    enemy_status_display = combat.enemy_status.get_status_display()
    if enemy_status_display:
        output += f"  적 상태: {enemy_status_display}\n"

    # 적 반격
    combat.player_defending = False

    # 적 턴 시작 처리
    enemy_turn = combat.enemy_status.process_turn_start()
    if enemy_turn["dot_damage"] > 0:
        enemy.take_damage(enemy_turn["dot_damage"])
        output += f"\n  {chr(10).join(enemy_turn['messages'])}\n"

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

    # 적 행동 가능 여부
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

            # 회복 표시
            if action_result["healed"] > 0:
                output += f"\n  적 HP: {enemy.hp}/{enemy.max_hp}"
        else:
            enemy_result = process_enemy_attack(enemy, player, player_defending=False)
            enemy_damage = enemy_result["damage"]
            output += f"\n  🐺 {enemy.name}의 반격! {enemy_damage} 데미지!"

        # 반사 데미지
        reflect_ratio = combat.player_status.get_reflect_ratio()
        if reflect_ratio > 0 and enemy_damage > 0:
            reflect_damage = int(enemy_damage * reflect_ratio)
            enemy.take_damage(reflect_damage)
            output += f"\n  🪞 {reflect_damage} 반사 데미지!"

        if enemy_damage > 0:
            output += f"\n  당신의 HP: {player.hp}/{player.max_hp}\n"

        # 플레이어 상태 표시
        player_status_display = combat.player_status.get_status_display()
        if player_status_display:
            output += f"  상태: {player_status_display}\n"

        if not player.is_alive:
            output += await _get_game_over_text(game)
            GameState.clear()
            output += "═══════════════════════════════════════════════════"
            return output
        else:
            output += _get_action_menu(player, combat)
    else:
        output += f"\n  {chr(10).join(enemy_turn['messages'])}\n"
        output += _get_action_menu(player, combat)

    # 턴 종료 처리
    combat.turn += 1
    reduce_cooldowns(combat)
    combat.player_status.process_turn_end()
    combat.enemy_status.process_turn_end()

    # v5.0: 다음 턴 적 행동 결정
    combat._determine_enemy_action(player.hp / player.max_hp if player.max_hp > 0 else 1.0)

    output += "═══════════════════════════════════════════════════"
    return output


async def _use_ultimate(game: GameState, player, enemy, combat) -> str:
    """
    Phase 1B: 궁극기 사용
    콤보 3연속 달성 시 사용 가능
    """
    from systems.combo import ULTIMATE_SKILL

    # 플레이어 턴 시작 처리 (상태이상)
    turn_start = combat.player_status.process_turn_start()

    # 도트 데미지 처리
    if turn_start["dot_damage"] > 0:
        player.take_damage(turn_start["dot_damage"])

    # 행동 불가 상태 확인
    if not turn_start["can_act"]:
        from systems.combat import process_enemy_attack
        enemy_result = process_enemy_attack(enemy, player, player_defending=False)

        output = f"""
═══════════════════════════════════════════════════
  ⚠️ 행동 불가!
═══════════════════════════════════════════════════

  {chr(10).join(turn_start['messages'])}

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

    # 궁극기 사용
    damage, message = combat.combo_chain.use_ultimate(player, enemy)

    if damage == 0:
        return f"❌ {message}"

    output = f"""
═══════════════════════════════════════════════════
  ⚡💥 궁극기 발동!
═══════════════════════════════════════════════════

  {ULTIMATE_SKILL['icon']} {ULTIMATE_SKILL['name']}!

  {message}
"""

    # 적 처치 확인
    if not enemy.is_alive:
        rewards = game.end_combat(victory=True)
        level_ups = player.add_exp(0)

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

        output += "\n═══════════════════════════════════════════════════"
        return output

    # 적 HP 표시
    output += f"\n  적 HP: {enemy.hp}/{enemy.max_hp}\n"

    # 적 상태 이상 표시
    enemy_status_display = combat.enemy_status.get_status_display()
    if enemy_status_display:
        output += f"  적 상태: {enemy_status_display}\n"

    # 적 턴 시작 처리
    enemy_turn = combat.enemy_status.process_turn_start()
    if enemy_turn["dot_damage"] > 0:
        enemy.take_damage(enemy_turn["dot_damage"])
        output += f"\n  {chr(10).join(enemy_turn['messages'])}\n"

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

    # 적 행동
    if enemy_turn["can_act"]:
        from systems.enemy_ai import execute_enemy_action

        if combat.enemy_next_action:
            action_result = execute_enemy_action(
                enemy, combat.enemy_next_action, player,
                player_defending=False
            )
            enemy_damage = action_result["damage"]
            output += f"\n  {action_result['message']}"

            if action_result["healed"] > 0:
                output += f"\n  적 HP: {enemy.hp}/{enemy.max_hp}"
        else:
            from systems.combat import process_enemy_attack
            enemy_result = process_enemy_attack(enemy, player, player_defending=False)
            enemy_damage = enemy_result["damage"]
            output += f"\n  🐺 {enemy.name}의 반격! {enemy_damage} 데미지!"

        # 반사 데미지
        reflect_ratio = combat.player_status.get_reflect_ratio()
        if reflect_ratio > 0 and enemy_damage > 0:
            reflect_damage = int(enemy_damage * reflect_ratio)
            enemy.take_damage(reflect_damage)
            output += f"\n  🪞 {reflect_damage} 반사 데미지!"

        if enemy_damage > 0:
            output += f"\n  당신의 HP: {player.hp}/{player.max_hp}\n"

        player_status_display = combat.player_status.get_status_display()
        if player_status_display:
            output += f"  상태: {player_status_display}\n"

        if not player.is_alive:
            output += await _get_game_over_text(game)
            GameState.clear()
            output += "═══════════════════════════════════════════════════"
            return output
        else:
            output += _get_action_menu(player, combat)
    else:
        output += f"\n  {chr(10).join(enemy_turn['messages'])}\n"
        output += _get_action_menu(player, combat)

    # 턴 종료 처리
    combat.turn += 1
    reduce_cooldowns(combat)
    combat.player_status.process_turn_end()
    combat.enemy_status.process_turn_end()
    combat._determine_enemy_action(player.hp / player.max_hp if player.max_hp > 0 else 1.0)

    output += "═══════════════════════════════════════════════════"
    return output


async def _get_game_over_text(game: GameState) -> str:
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
    """행동 선택 메뉴"""
    # 사용 가능한 스킬 수
    available_skills = len([
        s for s in player.skills
        if combat.cooldowns.get(f"skill_{s}", 0) <= 0
    ])

    # Phase 1B: 콤보 체인 상태 표시
    combo_status = combat.combo_chain.get_status_display()
    combo_line = f"\n  {combo_status}" if combo_status else ""

    # Phase 1B: 궁극기 사용 가능 시 메뉴에 추가
    ultimate_option = ""
    if combat.combo_chain.ultimate_ready:
        ultimate_option = "\n  • use_skill ultimate - 💥 궁극기: 멸절의 일격!"

    return f"""
───────────────────────────────────────────────────{combo_line}
  [행동 선택]
  • attack - 공격
  • use_skill [스킬ID] - 스킬 (사용 가능: {available_skills}개){ultimate_option}
  • defend - 방어
  • flee - 도망 (보스전 불가)
  • get_skills - 스킬 목록
"""
