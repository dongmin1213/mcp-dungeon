"""인벤토리 관련 MCP 도구"""
from state.game_state import GameState
from systems.item import (
    use_item as _use_item,
    equip_item as _equip_item,
    unequip_item as _unequip_item,
    get_inventory_display,
)
from systems.curse import get_curse_description


async def get_inventory() -> str:
    """
    인벤토리를 확인합니다.

    Returns:
        인벤토리 목록
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    player = game.player
    data = await get_inventory_display(player)

    # 장비 목록
    equip_lines = []
    slot_names = {
        "weapon": "무기",
        "armor": "방어구",
        "helmet": "투구",
        "accessory1": "장신구1",
        "accessory2": "장신구2",
    }

    for slot, name in slot_names.items():
        eq = data["equipment"].get(slot)
        if eq:
            stats = eq["stats"]
            stat_str = []
            if stats["atk"]: stat_str.append(f"ATK+{stats['atk']}")
            if stats["def"]: stat_str.append(f"DEF+{stats['def']}")
            if stats["hp"]: stat_str.append(f"HP+{stats['hp']}")
            if stats["mp"]: stat_str.append(f"MP+{stats['mp']}")

            # v5.0 저주 표시
            curse_str = ""
            if eq.get("curse"):
                curse_str = f" 💀{get_curse_description(eq['curse'])}"

            grade_icon = "💀" if eq.get("grade") == "cursed" else ""
            equip_lines.append(f"  {name}: {grade_icon}{eq['name']} ({', '.join(stat_str) if stat_str else '-'}){curse_str}")
        else:
            equip_lines.append(f"  {name}: (비어있음)")

    # 인벤토리 목록 (장착된 아이템 제외)
    item_lines = []
    grade_icons = {"common": "⚪", "uncommon": "🟢", "rare": "🔵", "legendary": "🟡", "cursed": "💀"}
    type_icons = {"weapon": "⚔️", "armor": "🛡️", "helmet": "🪖", "accessory": "💍", "consumable": "🧪", "special": "✨"}

    # 장착된 아이템 ID 목록 (중복 표시 방지)
    equipped_ids = set()
    for slot_data in data["equipment"].values():
        if slot_data and slot_data.get("id"):
            equipped_ids.add(slot_data["id"])

    for item in data["items"]:
        # 장착된 아이템은 [소지품]에서 제외
        if item.get("id") in equipped_ids:
            continue
        icon = type_icons.get(item["type"], "📦")
        grade = grade_icons.get(item["grade"], "⚪")
        curse_mark = " ⚠️저주" if item.get("curse") else ""
        item_lines.append(f"  {grade}{icon} {item['name']} - {item['price']}G{curse_mark}")

    if not item_lines:
        item_lines.append("  (비어있음)")

    current, maximum = data["capacity"]

    return f"""
═══════════════════════════════════════════════════
  🎒 인벤토리 ({current}/{maximum})
═══════════════════════════════════════════════════

  [장착 장비]
{chr(10).join(equip_lines)}

───────────────────────────────────────────────────

  [소지품]
{chr(10).join(item_lines)}

───────────────────────────────────────────────────
  💰 보유 골드: {player.gold}G

  💡 명령어:
  • use_item [아이템ID] - 소비 아이템 사용
  • equip [아이템ID] - 장비 장착
  • unequip [슬롯] - 장비 해제
═══════════════════════════════════════════════════
"""


async def use_item(item_id: str) -> str:
    """
    소비 아이템을 사용합니다.

    Args:
        item_id: 아이템 ID

    Returns:
        사용 결과
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    result = await _use_item(game.player, item_id)

    if not result["success"]:
        return result["message"]

    # 특수 효과 처리
    for effect_type, value in result["effects"]:
        if effect_type == "reveal_map":
            # 맵 전체 공개
            for row in game.dungeon.rooms:
                for room in row:
                    if room.can_enter:
                        room.visited = True

        elif effect_type == "teleport" and value == "start":
            # 시작 지점으로 이동
            game.dungeon.current_pos = game.dungeon.start_pos

        elif effect_type == "guaranteed_flee" and game.in_combat:
            # 확정 도망
            game.combat.fled = True
            game.combat = None
            return f"""
═══════════════════════════════════════════════════
  {result['message']}

  💨 전투에서 성공적으로 도망쳤습니다!
═══════════════════════════════════════════════════
"""

    player = game.player

    # 행운의 주사위는 별도 포맷
    if result.get("is_dice"):
        death_msg = ""
        if not player.is_alive:
            death_msg = """
───────────────────────────────────────────────────
  💀 사망했습니다...
  'start_game'으로 새 게임을 시작하세요.
"""
            GameState.clear()

        return f"""
═══════════════════════════════════════════════════
{result['message']}

───────────────────────────────────────────────────
  현재 상태:
  ❤️  HP: {player.hp}/{player.max_hp}
  💧 MP: {player.mp}/{player.max_mp}
  💰 골드: {player.gold}G
{death_msg}═══════════════════════════════════════════════════
"""

    return f"""
═══════════════════════════════════════════════════
  {result['message']}

  현재 HP: {player.hp}/{player.max_hp}
  현재 MP: {player.mp}/{player.max_mp}
═══════════════════════════════════════════════════
"""


async def equip(item_id: str) -> str:
    """
    아이템을 장착합니다.

    Args:
        item_id: 아이템 ID

    Returns:
        장착 결과
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    if game.in_combat:
        return "❌ 전투 중에는 장비를 변경할 수 없습니다."

    result = await _equip_item(game.player, item_id)

    if not result["success"]:
        return result["message"]

    player = game.player

    # v5.0 저주 아이템 경고
    curse_warning = ""
    if result.get("curse"):
        curse_warning = f"""
───────────────────────────────────────────────────
  💀 경고: 저주받은 아이템!
  저주 효과: {get_curse_description(result['curse'])}
"""

    return f"""
═══════════════════════════════════════════════════
  {result['message']}{curse_warning}

  현재 스탯:
  ⚔️  ATK: {player.atk}  |  🛡️  DEF: {player.def_}
  ❤️  HP: {player.hp}/{player.max_hp}
  💧 MP: {player.mp}/{player.max_mp}
═══════════════════════════════════════════════════
"""


async def unequip(slot: str) -> str:
    """
    장비를 해제합니다.

    Args:
        slot: 장비 슬롯 (weapon/armor/helmet/accessory1/accessory2)

    Returns:
        해제 결과
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    if game.in_combat:
        return "❌ 전투 중에는 장비를 변경할 수 없습니다."

    result = await _unequip_item(game.player, slot)

    if not result["success"]:
        return result["message"]

    player = game.player
    return f"""
═══════════════════════════════════════════════════
  {result['message']}

  현재 스탯:
  ⚔️  ATK: {player.atk}  |  🛡️  DEF: {player.def_}
  ❤️  HP: {player.hp}/{player.max_hp}
  💧 MP: {player.mp}/{player.max_mp}
═══════════════════════════════════════════════════
"""
