"""저장/불러오기 MCP 도구"""
from state.game_state import GameState
from database import get_db
from repository.save_repo import SaveRepository
from systems.save_load import SaveData
from config import CLASS_NAMES


async def save_game(slot: int = 0) -> str:
    """
    현재 게임을 저장합니다.

    Args:
        slot: 저장 슬롯 번호 (1-5, 0이면 현재 슬롯 사용)

    Returns:
        저장 결과
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    if game.in_combat:
        return "❌ 전투 중에는 저장할 수 없습니다."

    # 슬롯이 지정되지 않으면 현재 플레이 중인 슬롯 사용
    if slot == 0:
        if game.current_slot is not None:
            slot = game.current_slot
        else:
            slot = 1  # 현재 슬롯도 없으면 1번 사용

    if slot < 1 or slot > 5:
        return "❌ 슬롯 번호는 1~5 사이여야 합니다."

    # 게임 상태 직렬화
    save_data = SaveData.serialize_game(game)

    async with get_db() as db:
        repo = SaveRepository(db)
        await repo.save_slot(slot, save_data)

    # 수동 저장한 슬롯을 현재 슬롯으로 변경
    game.current_slot = slot

    player = game.player
    return f"""
═══════════════════════════════════════════════════
  💾 게임 저장 완료!
═══════════════════════════════════════════════════

  슬롯: {slot}번
  캐릭터: {player.name} ({CLASS_NAMES.get(player.class_type, player.class_type)})
  레벨: Lv.{player.level}
  층: {game.floor}층
  플레이 시간: {_format_time(game.play_time)}

═══════════════════════════════════════════════════
"""


async def load_game(slot: int = 1) -> str:
    """
    저장된 게임을 불러옵니다.

    Args:
        slot: 저장 슬롯 번호 (1-5)

    Returns:
        불러오기 결과
    """
    if slot < 1 or slot > 5:
        return "❌ 슬롯 번호는 1~5 사이여야 합니다."

    async with get_db() as db:
        repo = SaveRepository(db)
        save_slot = await repo.get_slot(slot)

    if save_slot.is_empty():
        return f"❌ 슬롯 {slot}번에 저장된 데이터가 없습니다."

    # 현재 게임이 있으면 덮어쓰기 경고 (자동 진행)
    if GameState.current():
        GameState.clear()

    # 게임 상태 복원
    try:
        game = _restore_game_state(save_slot.data)
        game.current_slot = slot  # 불러온 슬롯 기억
        summary = save_slot.summary

        return f"""
═══════════════════════════════════════════════════
  📂 게임 불러오기 완료!
═══════════════════════════════════════════════════

  슬롯: {slot}번
  캐릭터: {game.player.name} ({CLASS_NAMES.get(game.player.class_type, game.player.class_type)})
  레벨: Lv.{game.player.level}
  층: {game.floor}층
  HP: {game.player.hp}/{game.player.max_hp}
  골드: {game.player.gold}G

  💡 'get_status'로 상태 확인, 'move'로 이동하세요.

═══════════════════════════════════════════════════
"""
    except Exception as e:
        return f"""
═══════════════════════════════════════════════════
  ❌ 불러오기 실패
═══════════════════════════════════════════════════

  저장 데이터를 복원하는 중 오류가 발생했습니다.
  오류: {str(e)}

  'start_game'으로 새 게임을 시작하세요.

═══════════════════════════════════════════════════
"""


def _restore_game_state(data: dict) -> GameState:
    """저장 데이터로부터 게임 상태 복원"""
    from models.player import Player
    from models.dungeon import Dungeon, Room, Position, RoomType

    # Player 복원
    player_data = data["player"]
    player = Player(
        name=player_data["name"],
        class_type=player_data["class_id"],
        level=player_data["level"],
        exp=player_data["exp"],
        hp=player_data["hp"],
        max_hp=player_data["max_hp"],
        mp=player_data["mp"],
        max_mp=player_data["max_mp"],
        atk=player_data["atk"],
        def_=player_data["def_"],
        gold=player_data["gold"],
        crit_chance=player_data.get("crit_chance", 0.15),
        inventory=player_data.get("inventory", []),
        equipment=player_data.get("equipment", {
            "weapon": None, "armor": None, "helmet": None,
            "accessory1": None, "accessory2": None
        }),
        skills=player_data.get("skills", []),
    )

    # Dungeon 복원
    dungeon_data = data["dungeon"]
    rooms_data = dungeon_data["rooms"]
    width = dungeon_data["width"]
    height = dungeon_data["height"]

    # 2D 그리드로 변환
    rooms = []
    for y in range(height):
        row = []
        for x in range(width):
            key = f"{x},{y}"
            room_info = rooms_data.get(key, {"type": "wall", "cleared": False, "visited": False})
            room_type = room_info.get("type", "wall")
            if isinstance(room_type, str):
                room_type = RoomType(room_type)
            room = Room(
                x=x,
                y=y,
                type=room_type,
                cleared=room_info.get("cleared", False),
                visited=room_info.get("visited", False),
                event_id=room_info.get("event_id"),
                monster_id=room_info.get("monster_id"),
            )
            row.append(room)
        rooms.append(row)

    current_pos = dungeon_data["current_pos"]
    start_pos = dungeon_data.get("start_pos", current_pos)
    boss_pos = dungeon_data.get("boss_pos", [0, 0])
    exit_pos = dungeon_data.get("exit_pos", [0, 0])

    dungeon = Dungeon(
        floor=dungeon_data["floor"],
        width=width,
        height=height,
        rooms=rooms,
        start_pos=Position(x=start_pos[0], y=start_pos[1]),
        boss_pos=Position(x=boss_pos[0], y=boss_pos[1]),
        exit_pos=Position(x=exit_pos[0], y=exit_pos[1]),
        current_pos=Position(x=current_pos[0], y=current_pos[1]),
    )

    # GameState 생성
    game = GameState.create(player, dungeon)

    # 통계 복원
    stats = data.get("stats", {})
    game.monsters_killed = stats.get("monsters_killed", 0)
    game.gold_earned = stats.get("gold_earned", 0)
    game.souls_earned = stats.get("souls_earned", 0)

    return game


async def get_save_slots() -> str:
    """
    저장 슬롯 목록을 조회합니다.

    Returns:
        저장 슬롯 정보
    """
    async with get_db() as db:
        repo = SaveRepository(db)
        slots = await repo.get_all_slots()

    output = """
═══════════════════════════════════════════════════
  💾 저장 슬롯
═══════════════════════════════════════════════════
"""

    for slot in slots:
        if slot.is_empty():
            output += f"\n  [{slot.slot_id}] 빈 슬롯\n"
        else:
            s = slot.summary
            output += f"""
  [{slot.slot_id}] {s['name']} ({CLASS_NAMES.get(s['class_id'], s['class_id'])})
      Lv.{s['level']} | {s['floor']}층 | {s['mode']}
      플레이 시간: {_format_time(s['play_time'])}
      저장 시간: {slot.saved_at[:16] if slot.saved_at else '-'}
"""

    output += """
───────────────────────────────────────────────────
  💡 'save_game [슬롯]'으로 저장
     'load_game [슬롯]'으로 불러오기
═══════════════════════════════════════════════════
"""
    return output


async def delete_save(slot: int) -> str:
    """
    저장 슬롯을 삭제합니다.

    Args:
        slot: 삭제할 슬롯 번호 (1-5)

    Returns:
        삭제 결과
    """
    if slot < 1 or slot > 5:
        return "❌ 슬롯 번호는 1~5 사이여야 합니다."

    async with get_db() as db:
        repo = SaveRepository(db)
        save_slot = await repo.get_slot(slot)

        if save_slot.is_empty():
            return f"❌ 슬롯 {slot}번에 저장된 데이터가 없습니다."

        await repo.delete_slot(slot)

    return f"""
═══════════════════════════════════════════════════
  🗑️ 저장 데이터 삭제 완료
═══════════════════════════════════════════════════

  슬롯 {slot}번의 저장 데이터가 삭제되었습니다.

═══════════════════════════════════════════════════
"""


def _format_time(seconds: int) -> str:
    """시간 포맷팅"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}시간 {minutes}분"
    elif minutes > 0:
        return f"{minutes}분 {secs}초"
    else:
        return f"{secs}초"


async def auto_save(reason: str = "") -> bool:
    """
    자동 저장 (현재 슬롯에 저장, 메시지 없이 조용히 저장)

    Args:
        reason: 저장 사유 (로깅용)

    Returns:
        저장 성공 여부
    """
    game = GameState.current()
    if not game:
        return False

    # 전투 중에는 저장하지 않음
    if game.in_combat:
        return False

    # 슬롯이 지정되지 않았으면 저장하지 않음
    slot = game.current_slot
    if slot is None:
        return False

    try:
        save_data = SaveData.serialize_game(game)
        async with get_db() as db:
            repo = SaveRepository(db)
            await repo.save_slot(slot, save_data)
        return True
    except Exception:
        return False
