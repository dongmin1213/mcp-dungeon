"""게임 진행 관련 MCP 도구"""
import random
from config import CLASS_STATS, CLASS_NAMES, GameConfig
from models.player import Player
from models.dungeon import RoomType
from state.game_state import GameState, PendingChoice
from systems.dungeon import generate_dungeon
from systems.skill import unlock_skills_for_level
from systems.shop import close_shop
from datetime import datetime

# 기본 해금 직업 목록
DEFAULT_UNLOCKED_CLASSES = ["warrior", "archer"]


async def start_game(player_name: str, ascension: int = 0) -> str:
    """
    새로운 던전 탐험을 시작합니다.
    저장된 게임이 있으면 이어하기/새로 시작 선택지를 보여줍니다.
    직업은 기본 해금 직업 중 랜덤으로 선택됩니다.

    Args:
        player_name: 플레이어 이름 (필수)
        ascension: 승천 레벨 (0-10, 기본 0)

    Returns:
        게임 시작 메시지
    """
    from database import get_db
    from repository.save_repo import SaveRepository

    # 이름이 비어있으면 세이브 확인만
    if not player_name or player_name.strip() == "":
        async with get_db() as db:
            repo = SaveRepository(db)
            slots = await repo.get_all_slots()

        saved_slots = [s for s in slots if not s.is_empty()]

        if saved_slots:
            save_list = ""
            for slot in saved_slots:
                s = slot.summary
                class_name = CLASS_NAMES.get(s['class_id'], s['class_id'])
                save_list += f"""
  [{slot.slot_id}] {s['name']} ({class_name})
      Lv.{s['level']} | {s['floor']}층 | HP: {s.get('hp', '?')}/{s.get('max_hp', '?')}
      저장: {slot.saved_at[:16] if slot.saved_at else '-'}"""

            return f"""
═══════════════════════════════════════════════════
  🏰 MCP 던전
═══════════════════════════════════════════════════

  💾 저장된 게임이 있습니다!
{save_list}

───────────────────────────────────────────────────
  [선택]
  • 이어하기: load_game(슬롯번호)
  • 새 게임: start_game("플레이어이름")

═══════════════════════════════════════════════════
"""
        else:
            return """
═══════════════════════════════════════════════════
  🏰 MCP 던전
═══════════════════════════════════════════════════

  저장된 게임이 없습니다.

  새 게임을 시작하려면 이름을 입력하세요:
  start_game("플레이어이름")

═══════════════════════════════════════════════════
"""

    # Phase 2: 승천 레벨 검증
    from systems.ascension import get_ascension_display, get_ascension_description

    ascension = max(0, min(10, ascension))  # 0-10 범위로 제한

    # 새 게임 시작
    # 빈 슬롯 찾기
    async with get_db() as db:
        repo = SaveRepository(db)
        slots = await repo.get_all_slots()

    empty_slots = [s.slot_id for s in slots if s.is_empty()]

    if not empty_slots:
        # 빈 슬롯이 없으면 사용자에게 선택 요청
        slot_info = ""
        for slot in slots:
            s = slot.summary
            class_name = CLASS_NAMES.get(s['class_id'], s['class_id'])
            slot_info += f"\n  [{slot.slot_id}] {s['name']} ({class_name}) - Lv.{s['level']} | {s['floor']}층"

        return f"""
═══════════════════════════════════════════════════
  ⚠️ 저장 슬롯이 가득 찼습니다!
═══════════════════════════════════════════════════

  새 게임을 시작하려면 기존 세이브를 삭제해야 합니다.
{slot_info}

───────────────────────────────────────────────────
  • delete_save(슬롯번호) - 세이브 삭제
  • 삭제 후 다시 start_game("{player_name}")

═══════════════════════════════════════════════════
"""

    # 첫 번째 빈 슬롯 할당
    assigned_slot = empty_slots[0]

    # 기본 해금 직업 중 랜덤 선택
    class_type = random.choice(DEFAULT_UNLOCKED_CLASSES)

    # 상점 초기화
    close_shop()

    # 새 게임 생성 (Phase 2: 승천 레벨 포함)
    player = Player.create(player_name, class_type)
    dungeon = generate_dungeon(floor=1)
    game = GameState.create(player, dungeon, ascension_level=ascension)
    game.current_slot = assigned_slot  # 슬롯 할당

    # 초기 스킬 부여 (레벨 1 스킬) - 저장 전에 부여해야 함!
    initial_skills = await unlock_skills_for_level(player, 1)
    skill_text = ""
    if initial_skills:
        skill_names = ", ".join([s.name for s in initial_skills])
        skill_text = f"\n  📚 초기 스킬: {skill_names}"

    # 새 게임 시작 시 즉시 저장 (스킬 부여 후)
    from tools.save import auto_save
    await auto_save(f"새 게임 시작: {player_name}")

    # Phase 2: 승천 정보 표시
    ascension_text = ""
    if ascension > 0:
        ascension_text = f"\n  ⚔️ 난이도: {get_ascension_display(ascension)}"
        ascension_text += f"\n{get_ascension_description(ascension)}"

    return f"""
═══════════════════════════════════════════════════
  🏰 MCP 던전에 오신 것을 환영합니다!
═══════════════════════════════════════════════════
  플레이어: {player.name} ({player.class_name})
  ❤️  HP: {player.hp}/{player.max_hp}
  💧 MP: {player.mp}/{player.max_mp}
  ⚔️  ATK: {player.atk}  |  🛡️  DEF: {player.def_}{skill_text}{ascension_text}

  📍 현재 위치: 1층 - 던전 입구
  💾 저장 슬롯: {assigned_slot}번
═══════════════════════════════════════════════════

  당신은 어두운 던전 입구에 서 있습니다.
  앞으로 무엇이 기다리고 있을지 알 수 없습니다...

  💡 'get_status'로 상태 확인, 'move'로 이동하세요.
  💡 'get_skills'로 스킬 확인, 전투 중 'use_skill'로 사용!
═══════════════════════════════════════════════════
"""


async def get_status() -> str:
    """
    현재 게임 상태를 확인합니다.

    Returns:
        현재 상태 정보
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다. 'start_game'으로 시작하세요."

    player = game.player
    room = game.current_room
    dungeon = game.dungeon

    # 인접 방향 정보
    adjacent = dungeon.get_adjacent_rooms()
    directions = []
    for dir_name, adj_room in adjacent.items():
        if adj_room and adj_room.can_enter:
            dir_kr = {"north": "북", "south": "남", "east": "동", "west": "서"}[dir_name]
            if adj_room.visited:
                directions.append(f"{dir_kr}({adj_room.icon})")
            else:
                directions.append(f"{dir_kr}(?)")

    dir_info = " | ".join(directions) if directions else "없음"

    status = f"""
═══════════════════════════════════════════════════
  🏰 MCP 던전 - {game.floor}층 {room.name}
═══════════════════════════════════════════════════
  ❤️  HP: {player.hp}/{player.max_hp}  |  💧 MP: {player.mp}/{player.max_mp}
  ⚔️  ATK: {player.atk}  |  🛡️  DEF: {player.def_}
  💰 골드: {player.gold}  |  🎒 아이템: {len(player.inventory)}개
  📊 Lv.{player.level} ({player.exp}/{player.exp_to_next} EXP)
═══════════════════════════════════════════════════

  📍 현재 위치: {room.name}
  🧭 이동 가능: {dir_info}
"""

    # 전투 중이면 전투 정보 추가
    if game.in_combat:
        enemy = game.combat.enemy
        status += f"""
───────────────────────────────────────────────────
  ⚔️ 전투 중! - {enemy.name}
  적 HP: {enemy.hp}/{enemy.max_hp}
───────────────────────────────────────────────────
"""

    status += "═══════════════════════════════════════════════════"
    return status


async def move(direction: str) -> str:
    """
    지정한 방향으로 이동합니다.

    Args:
        direction: 이동 방향 (north/south/east/west)

    Returns:
        이동 결과 메시지
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    success, message = game.move(direction)
    if not success:
        return f"❌ {message}"

    room = game.current_room
    dir_kr = {"north": "북쪽", "south": "남쪽", "east": "동쪽", "west": "서쪽"}.get(direction, direction)

    result = f"""
═══════════════════════════════════════════════════
  🚶 {dir_kr}으로 이동했습니다.
═══════════════════════════════════════════════════

  📍 {room.name}
"""

    # 방 타입별 메시지
    if room.type == RoomType.MONSTER and not room.cleared:
        # 몬스터 방 진입 시 자동 전투 시작
        combat_result = await _start_combat(game, room)
        result += f"\n{combat_result}"
    elif room.type == RoomType.TREASURE and not room.cleared:
        result += """
  💎 보물 상자를 발견했습니다!
  'interact'로 열어보세요.
"""
    elif room.type == RoomType.SHOP:
        result += """
  🏪 상점에 도착했습니다.
  'interact'로 상점을 이용하세요.
"""
    elif room.type == RoomType.REST and not room.cleared:
        result += """
  🏕️ 휴식처를 발견했습니다.
  'interact'로 휴식하세요.
"""
    elif room.type == RoomType.TRAP and not room.cleared:
        # 함정 자동 발동
        trap_result = await _trigger_trap(game, room)
        result += f"\n{trap_result}"
    elif room.type == RoomType.MYSTERY and not room.cleared:
        result += """
  ❓ 무언가 이상한 기운이 느껴집니다...
  'interact'로 조사하세요.
"""
    elif room.type == RoomType.BOSS and not room.cleared:
        # 보스 방 진입 시 자동 전투 시작 (도망 불가)
        combat_result = await _start_combat(game, room)
        result += f"\n{combat_result}"
    elif room.type == RoomType.EXIT:
        result += """
  🚪 다음 층으로 가는 계단입니다.
  'interact'로 다음 층으로 이동하세요.
"""
    elif room.type == RoomType.MONSTER and room.cleared:
        result += "\n  ⚔️ 몬스터를 처치한 방입니다."
    elif room.type == RoomType.BOSS and room.cleared:
        result += "\n  👑 보스를 처치한 방입니다."
    else:
        result += "\n  텅 빈 방입니다."

    result += "\n═══════════════════════════════════════════════════"
    return result


async def get_map() -> str:
    """
    현재 층의 미니맵을 확인합니다.

    Returns:
        미니맵
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    minimap = game.dungeon.get_minimap()

    return f"""
═══════════════════════════════════════════════════
  🗺️ {game.floor}층 지도
═══════════════════════════════════════════════════

{minimap}

  범례: @ 현재위치 | S 시작 | B 보스 | E 계단
        M 몬스터 | T 보물 | P 상점 | R 휴식
        ! 함정 | ? 미스터리 | · 빈방 | █ 벽
═══════════════════════════════════════════════════
"""


async def interact(choice: int = 0) -> str:
    """
    현재 방과 상호작용합니다.

    Args:
        choice: 선택지 번호 (1, 2, 3 등). 0이면 선택지 표시

    Returns:
        상호작용 결과
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    if game.in_combat:
        return "❌ 전투 중입니다. 'attack' 또는 'flee'를 사용하세요."

    # 대기 중인 선택지가 있고 선택 번호가 주어진 경우
    if game.pending_choice and choice > 0:
        return await _process_choice(game, choice)

    room = game.current_room

    # 이미 클리어된 방
    if room.cleared and room.type not in [RoomType.SHOP, RoomType.EXIT, RoomType.START]:
        return "이 방에서는 더 이상 할 일이 없습니다."

    # 방 타입별 처리
    if room.type == RoomType.MONSTER or room.type == RoomType.BOSS:
        return await _start_combat(game, room)
    elif room.type == RoomType.TREASURE:
        return await _open_treasure(game, room)
    elif room.type == RoomType.TRAP:
        return await _trigger_trap(game, room)
    elif room.type == RoomType.REST:
        return await _use_rest(game, room)
    elif room.type == RoomType.EXIT:
        return await _use_exit(game, room)
    elif room.type == RoomType.SHOP:
        return await _use_shop(game, room)
    elif room.type == RoomType.MYSTERY:
        return await _trigger_mystery(game, room)
    else:
        return "이 방에서는 특별히 할 일이 없습니다."


async def _start_combat(game: GameState, room) -> str:
    """전투 시작 (DB에서 몬스터 조회)"""
    from repository.monster_repo import MonsterRepository
    import random

    floor = game.floor
    is_boss = room.type == RoomType.BOSS

    if is_boss:
        enemy = await MonsterRepository.get_boss_for_floor(floor)
    else:
        # 엘리트 확률 (v4.0: 10% → 25%)
        if random.random() < GameConfig.ELITE_SPAWN_RATE:
            enemy = await MonsterRepository.get_elite_for_floor(floor)
        else:
            enemy = await MonsterRepository.get_random_for_floor(floor, "normal")

    # DB에 몬스터가 없으면 기본 몬스터 생성
    if not enemy:
        from models.monster import Monster, MonsterType
        base_hp = 20 + floor * 10
        base_atk = 5 + floor * 3
        base_def = 1 + floor
        enemy = Monster(
            id="unknown",
            name="미지의 적",
            type=MonsterType.BOSS if is_boss else MonsterType.NORMAL,
            hp=base_hp,
            max_hp=base_hp,
            atk=base_atk,
            def_=base_def,
            exp=10 + floor * 5,
            gold_min=5 + floor * 3,
            gold_max=15 + floor * 5,
            souls=floor * (10 if is_boss else 1),
        )

    # Phase 2: 승천 효과 적용 (HP 배율)
    if game.ascension_level > 0:
        if enemy.is_boss:
            hp_mult = game.ascension.get_boss_hp_modifier()
        elif enemy.is_elite:
            hp_mult = game.ascension.get_elite_hp_modifier()
        else:
            hp_mult = 1.0
        if hp_mult > 1.0:
            enemy.max_hp = int(enemy.max_hp * hp_mult)
            enemy.hp = enemy.max_hp

    combat = game.start_combat(enemy)
    player = game.player

    boss_warning = ""
    if enemy.is_boss:
        boss_warning = "\n  ⚠️ 보스전입니다! 도망칠 수 없습니다!"
    elif enemy.is_elite:
        boss_warning = "\n  ⚠️ 엘리트 몬스터입니다! 주의하세요!"

    # v5.0: 적의 첫 행동 예고
    from systems.enemy_ai import get_action_damage, get_action_description
    from models.monster import EnemyAction

    next_action = combat.enemy_next_action
    action_preview = ""
    if next_action:
        damage = get_action_damage(enemy, next_action)
        expected_damage = max(1, damage - player.def_) if damage > 0 else 0
        action_desc = get_action_description(next_action, expected_damage)
        action_preview = f"\n  ⚠️ 적의 다음 행동: {action_desc}"

        if next_action in [EnemyAction.HEAVY, EnemyAction.SPECIAL]:
            action_preview += "\n  💡 TIP: 방어를 고려해보세요!"

    # v5.0: 적 속성 정보 표시
    from systems.element import get_weakness_hint
    weakness_hint = get_weakness_hint(enemy)
    element_info = ""
    if weakness_hint:
        element_info = f"\n  🔍 {weakness_hint}"

    # Phase 2: 적 선공 (승천 4+)
    first_strike_text = ""
    if game.ascension.is_enemy_first_strike():
        from systems.combat import process_enemy_attack
        first_result = process_enemy_attack(enemy, player, player_defending=False)
        first_strike_text = f"""
  ⚠️ 승천 효과: 적 선공!
  🐺 {enemy.name}이(가) 먼저 공격합니다! {first_result['damage']} 데미지!
  당신의 HP: {player.hp}/{player.max_hp}
"""
        if not player.is_alive:
            # 선공으로 사망
            result_data = await _record_game_end(game, victory=False)
            GameState.clear()
            return f"""
═══════════════════════════════════════════════════
  ⚔️ 전투 시작!
═══════════════════════════════════════════════════
{first_strike_text}
───────────────────────────────────────────────────
  💀 사망했습니다...
  📊 점수: {result_data['score']:,}점 (랭킹 #{result_data['rank']})
  게임 오버!
═══════════════════════════════════════════════════
"""

    return f"""
═══════════════════════════════════════════════════
  ⚔️ 전투 시작!
═══════════════════════════════════════════════════

  👤 {player.name}          vs          👹 {enemy.name}
  ❤️ {player.hp}/{player.max_hp}                    ❤️ {enemy.hp}/{enemy.max_hp}
{boss_warning}{element_info}{first_strike_text}{action_preview}
═══════════════════════════════════════════════════

  [행동 선택]
  • attack - 기본 공격
  • defend - 방어 (데미지 무효화)
  • flee - 도망치기 (보스전 불가)

═══════════════════════════════════════════════════
"""


async def _open_treasure(game: GameState, room) -> str:
    """보물 상자 열기 (DB 이벤트 사용)"""
    from systems.event import process_treasure

    result = await process_treasure(game.floor, game.player)
    room.cleared = True

    # 아이템 목록 문자열
    item_str = ""
    if result.get("items"):
        items = [item.name for item in result["items"]]
        item_str = f"\n  🎁 아이템: {', '.join(items)}"

    return f"""
═══════════════════════════════════════════════════
  💎 {result['event']['name']}
═══════════════════════════════════════════════════

  {result['event']['description']}

  💰 {result['gold']} 골드 획득!{item_str}

  현재 골드: {game.player.gold}
═══════════════════════════════════════════════════
"""


async def _trigger_trap(game: GameState, room) -> str:
    """함정 발동 (DB 이벤트 사용)"""
    from systems.event import process_trap

    # Phase 2: 승천 효과 적용 (함정 데미지 배율)
    trap_mult = game.ascension.get_trap_damage_modifier()
    result = await process_trap(game.floor, game.player, damage_mult=trap_mult)
    room.cleared = True

    output = f"""
═══════════════════════════════════════════════════
  ⚠️ {result['event']['name']}
═══════════════════════════════════════════════════

  {result['message']}

  현재 HP: {game.player.hp}/{game.player.max_hp}
"""

    if not game.player.is_alive:
        # 함정 사망 시에도 프로필 기록 (BUG-008 수정)
        result = await _record_game_end(game, victory=False)
        output += f"""
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
        GameState.clear()

    output += "═══════════════════════════════════════════════════"
    return output


async def _process_choice(game: GameState, choice: int) -> str:
    """대기 중인 선택지 처리"""
    pending = game.pending_choice
    if not pending:
        return "❌ 선택할 수 있는 항목이 없습니다."

    if choice < 1 or choice > len(pending.choices):
        return f"❌ 잘못된 선택입니다. (1~{len(pending.choices)} 중 선택)"

    selected = pending.choices[choice - 1]
    room = game.current_room
    player = game.player
    result = ""

    if pending.room_type == "rest":
        # 휴식처 선택 처리
        effect = selected.get("effect", {})

        # Phase 2: 승천 효과로 휴식 회복량 감소
        rest_mult = game.ascension.get_rest_heal_modifier()

        if "heal_percent" in effect:
            # HP 회복
            percent = effect.get("heal_percent", 0.30)
            heal_amount = int(player.max_hp * percent * rest_mult)
            actual = player.heal(heal_amount)
            result = f"""
═══════════════════════════════════════════════════
  🏕️ {selected['text']}
═══════════════════════════════════════════════════

  ❤️ HP가 {actual} 회복되었습니다!

  현재 HP: {player.hp}/{player.max_hp}
═══════════════════════════════════════════════════
"""
        elif "heal_mp_percent" in effect:
            # MP 회복
            percent = effect.get("heal_mp_percent", 0.50)
            restore_amount = int(player.max_mp * percent)
            actual = player.heal_mp(restore_amount)
            result = f"""
═══════════════════════════════════════════════════
  🧘 {selected['text']}
═══════════════════════════════════════════════════

  💧 MP가 {actual} 회복되었습니다!

  현재 MP: {player.mp}/{player.max_mp}
═══════════════════════════════════════════════════
"""
        elif "buff" in effect:
            # ATK 버프
            buff = effect.get("buff", {})
            atk_mult = buff.get("atk_mult", 1.1)
            buff_amount = int(player.atk * (atk_mult - 1))
            player.atk += buff_amount
            result = f"""
═══════════════════════════════════════════════════
  ⚔️ {selected['text']}
═══════════════════════════════════════════════════

  ⚔️ 공격력이 {buff_amount} 증가했습니다!

  현재 ATK: {player.atk}
═══════════════════════════════════════════════════
"""
        else:
            result = f"""
═══════════════════════════════════════════════════
  🏕️ {selected['text']}
═══════════════════════════════════════════════════

  선택을 완료했습니다.
═══════════════════════════════════════════════════
"""
        room.cleared = True

        # 휴식처 사용 후 자동 저장
        from tools.save import auto_save
        await auto_save(f"휴식처 사용: {selected['text']}")
        result = result.rstrip("═\n") + "\n  💾 자동 저장됨\n═══════════════════════════════════════════════════\n"

    elif pending.room_type == "mystery":
        # 미스터리 방 선택 처리
        effect = selected.get("effect", {})
        result = await _apply_mystery_effect(game, selected, effect)
        room.cleared = True

    # 선택 완료 후 pending_choice 초기화
    game.pending_choice = None
    return result


async def _apply_mystery_effect(game: GameState, selected: dict, effect: dict) -> str:
    """미스터리 이벤트 효과 적용"""
    player = game.player
    effect_type = effect.get("type", "")
    value = effect.get("value", 0)

    if effect_type == "heal":
        actual = player.heal(value)
        return f"""
═══════════════════════════════════════════════════
  ✨ {selected.get('text', '선택')}
═══════════════════════════════════════════════════

  ❤️ HP가 {actual} 회복되었습니다!
  현재 HP: {player.hp}/{player.max_hp}
═══════════════════════════════════════════════════
"""
    elif effect_type == "damage":
        player.take_damage(value)
        return f"""
═══════════════════════════════════════════════════
  💥 {selected.get('text', '선택')}
═══════════════════════════════════════════════════

  💔 {value} 데미지를 받았습니다!
  현재 HP: {player.hp}/{player.max_hp}
═══════════════════════════════════════════════════
"""
    elif effect_type == "gold":
        player.add_gold(value)
        return f"""
═══════════════════════════════════════════════════
  💰 {selected.get('text', '선택')}
═══════════════════════════════════════════════════

  💰 {value} 골드를 획득했습니다!
  현재 골드: {player.gold}
═══════════════════════════════════════════════════
"""
    else:
        return f"""
═══════════════════════════════════════════════════
  ❓ {selected.get('text', '선택')}
═══════════════════════════════════════════════════

  아무 일도 일어나지 않았습니다.
═══════════════════════════════════════════════════
"""


async def _use_rest(game: GameState, room) -> str:
    """휴식처 사용 (선택지 표시)"""
    from repository.event_repo import EventRepository

    event = await EventRepository.get_rest(game.floor)
    if not event or not event.get("choices"):
        # 기본 휴식
        heal_amount = int(game.player.max_hp * 0.3)
        actual = game.player.heal(heal_amount)
        room.cleared = True
        return f"""
═══════════════════════════════════════════════════
  🏕️ 휴식처
═══════════════════════════════════════════════════

  모닥불 옆에서 휴식을 취했습니다.
  ❤️ HP가 {actual} 회복되었습니다!

  현재 HP: {game.player.hp}/{game.player.max_hp}
═══════════════════════════════════════════════════
"""

    # 선택지 표시 및 pending_choice 저장
    choices = event.get("choices", [])
    game.pending_choice = PendingChoice("rest", choices, event)

    choice_lines = []
    for i, choice in enumerate(choices, 1):
        choice_lines.append(f"  [{i}] {choice['text']} - {choice['description']}")

    return f"""
═══════════════════════════════════════════════════
  🏕️ {event['name']}
═══════════════════════════════════════════════════

  {event['description']}

  [행동 선택]
{chr(10).join(choice_lines)}

  💡 'interact(번호)'로 선택하세요. 예: interact(1)
═══════════════════════════════════════════════════
"""


async def _use_exit(game: GameState, room) -> str:
    """다음 층으로 이동"""
    current_floor = game.floor

    # 최종 층이면 클리어
    if current_floor >= GameConfig.MAX_FLOOR:
        # 게임 종료 기록
        result = await _record_game_end(game, victory=True)
        GameState.clear()

        return f"""
═══════════════════════════════════════════════════
  🎉 축하합니다! 던전을 클리어했습니다!
═══════════════════════════════════════════════════

  📊 점수: {result['score']:,}점 (랭킹 #{result['rank']})

  총 처치 몬스터: {game.monsters_killed}
  획득 골드: {game.gold_earned}
  획득 소울: {game.souls_earned} → 프로필에 저장됨!
  플레이 시간: {game.play_time // 60}분 {game.play_time % 60}초

{result['achievements_text']}
  'start_game'으로 새 게임을 시작하세요.
  'get_profile'로 프로필 확인!
═══════════════════════════════════════════════════
"""

    # 상점 초기화 (층 이동 시)
    close_shop()

    # 다음 층 생성
    next_floor = current_floor + 1
    new_dungeon = generate_dungeon(floor=next_floor)
    game.set_dungeon(new_dungeon)

    # 자동 저장
    from tools.save import auto_save
    await auto_save(f"층 이동: {next_floor}층")

    return f"""
═══════════════════════════════════════════════════
  🚪 {next_floor}층으로 이동합니다...
═══════════════════════════════════════════════════

  📍 {next_floor}층 - {game.current_room.name}

  더 깊은 던전으로 내려왔습니다.
  적들이 더 강해질 것입니다...

  💾 자동 저장됨
═══════════════════════════════════════════════════
"""


async def _record_game_end(game: GameState, victory: bool) -> dict:
    """게임 종료 시 기록 저장"""
    from database import get_db
    from repository.profile_repo import ProfileRepository
    from systems.ranking import RankingRepository, RankingEntry, calculate_score
    from systems.meta import check_and_complete_achievements

    player = game.player
    bosses_killed = game.floor // 2 if victory else (game.floor - 1) // 2

    # 점수 계산
    score = calculate_score(
        victory=victory,
        floor=game.floor,
        level=player.level,
        monsters_killed=game.monsters_killed,
        bosses_killed=bosses_killed,
        gold_earned=game.gold_earned,
        play_time=game.play_time,
        mode=getattr(game, "mode", "normal")
    )

    async with get_db() as db:
        # 프로필 업데이트
        profile_repo = ProfileRepository(db)
        profile = await profile_repo.record_run(
            profile_id="default",
            victory=victory,
            floor=game.floor,
            level=player.level,
            monsters_killed=game.monsters_killed,
            bosses_killed=bosses_killed,
            gold_earned=game.gold_earned,
            souls_earned=game.souls_earned,
            play_time=game.play_time
        )

        # 업적 확인
        completed = check_and_complete_achievements(profile)
        await profile_repo.save(profile)

        # 랭킹 등록
        ranking_repo = RankingRepository(db)
        entry = RankingEntry(
            profile_id="default",
            profile_name=profile.name,
            class_id=player.class_type,
            mode=getattr(game, "mode", "normal"),
            score=score,
            floor=game.floor,
            level=player.level,
            monsters_killed=game.monsters_killed,
            bosses_killed=bosses_killed,
            play_time=game.play_time,
            victory=victory,
            created_at=datetime.now()
        )
        await ranking_repo.add_entry(entry)
        rank = await ranking_repo.get_rank(score)

    # 달성한 업적 텍스트
    achievements_text = ""
    if completed:
        achievements_text = "  🏆 달성한 업적:\n"
        for achievement, reward in completed:
            if isinstance(reward, int):
                achievements_text += f"    • {achievement.name} (+{reward} 소울)\n"
            else:
                achievements_text += f"    • {achievement.name} (🔓 {reward})\n"
        achievements_text += "\n"

    return {
        "score": score,
        "rank": rank,
        "achievements_text": achievements_text,
    }


async def _use_shop(game: GameState, room) -> str:
    """상점 이용 안내"""
    from tools.shop import shop_list
    return await shop_list()


async def _trigger_mystery(game: GameState, room) -> str:
    """미스터리 이벤트 처리"""
    from repository.event_repo import EventRepository

    event = await EventRepository.get_mystery(game.floor)
    if not event:
        room.cleared = True
        return """
═══════════════════════════════════════════════════
  ❓ 미스터리
═══════════════════════════════════════════════════

  이상한 기운이 느껴졌지만...
  아무 일도 일어나지 않았습니다.

═══════════════════════════════════════════════════
"""

    # 선택지가 있는 이벤트
    choices = event.get("choices", [])
    if choices:
        # pending_choice에 저장
        game.pending_choice = PendingChoice("mystery", choices, event)

        choice_lines = []
        for i, choice in enumerate(choices, 1):
            cost_text = ""
            if choice.get("requires", {}).get("gold", 0) > 0:
                cost_text = f" (💰 {choice['requires']['gold']}G)"
            choice_lines.append(f"  [{i}] {choice['text']}{cost_text}")
            if choice.get("description"):
                choice_lines.append(f"      {choice['description']}")

        return f"""
═══════════════════════════════════════════════════
  ❓ {event['name']}
═══════════════════════════════════════════════════

  {event['description']}

  [선택지]
{chr(10).join(choice_lines)}

  💡 'interact(번호)'로 선택하세요. 예: interact(1)
═══════════════════════════════════════════════════
"""

    # 선택지 없는 이벤트 (즉시 효과)
    room.cleared = True
    return f"""
═══════════════════════════════════════════════════
  ❓ {event['name']}
═══════════════════════════════════════════════════

  {event['description']}

═══════════════════════════════════════════════════
"""
