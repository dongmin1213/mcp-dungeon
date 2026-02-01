"""상점 관련 MCP 도구"""
from state.game_state import GameState
from models.dungeon import RoomType
from systems.shop import (
    open_shop,
    get_shop_items,
    buy_item as _buy_item,
    sell_item as _sell_item,
    close_shop,
)


async def shop_list() -> str:
    """
    상점 목록을 확인합니다.

    Returns:
        상점 아이템 목록
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    if game.in_combat:
        return "❌ 전투 중에는 상점을 이용할 수 없습니다."

    room = game.current_room
    if room.type != RoomType.SHOP:
        return "❌ 현재 위치에 상점이 없습니다."

    # 상점 아이템 생성 (아직 없으면)
    items = get_shop_items()
    if not items:
        # Phase 2: 승천 2+ - 포션 판매 안 함
        no_potions = game.ascension.is_shop_potions_disabled()
        items = await open_shop(game.floor, no_potions=no_potions)

    # player 정의 (듀오 효과 계산에 필요)
    player = game.player

    # Phase 3: 듀오 할인 (황금 손)
    from systems.blessing import get_duo_combat_effects
    duo_effects = get_duo_combat_effects(player)
    shop_discount = duo_effects.get("shop_discount", 0)

    # 등급 아이콘
    grade_icons = {"common": "⚪", "uncommon": "🟢", "rare": "🔵", "legendary": "🟡"}
    type_icons = {"weapon": "⚔️", "armor": "🛡️", "helmet": "🪖", "accessory": "💍", "consumable": "🧪", "special": "✨"}

    item_lines = []
    for item in items:
        icon = type_icons.get(item.type.value, "📦")
        grade = grade_icons.get(item.grade.value, "⚪")

        # 스탯 정보
        stats = []
        if item.stat_atk: stats.append(f"ATK+{item.stat_atk}")
        if item.stat_def: stats.append(f"DEF+{item.stat_def}")
        if item.stat_hp: stats.append(f"HP+{item.stat_hp}")
        if item.stat_mp: stats.append(f"MP+{item.stat_mp}")
        stat_str = f" ({', '.join(stats)})" if stats else ""

        item_lines.append(f"  {grade}{icon} {item.name}{stat_str}")

        # Phase 3: 할인된 가격 표시
        if shop_discount > 0:
            discounted_price = int(item.price * (1 - shop_discount))
            item_lines.append(f"      ID: {item.id} | 💰 {discounted_price}G (원가: {item.price}G)")
        else:
            item_lines.append(f"      ID: {item.id} | 💰 {item.price}G")

        item_lines.append(f"      {item.description}")
        item_lines.append("")

    # Phase 3: 할인 정보
    discount_text = ""
    if shop_discount > 0:
        discount_percent = int(shop_discount * 100)
        discount_text = f"\n  ✋💰 황금 손 효과: 모든 아이템 {discount_percent}% 할인!"

    return f"""
═══════════════════════════════════════════════════
  🏪 상점 - {game.floor}층
═══════════════════════════════════════════════════

  💰 보유 골드: {player.gold}G{discount_text}

───────────────────────────────────────────────────
  [판매 목록]

{chr(10).join(item_lines)}
───────────────────────────────────────────────────

  💡 명령어:
  • buy [아이템ID] - 구매
  • sell [아이템ID] - 판매 (50% 가격)
  • get_inventory - 인벤토리 확인

═══════════════════════════════════════════════════
"""


async def buy(item_id: str) -> str:
    """
    아이템을 구매합니다.

    Args:
        item_id: 아이템 ID

    Returns:
        구매 결과
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    room = game.current_room
    if room.type != RoomType.SHOP:
        return "❌ 현재 위치에 상점이 없습니다."

    result = await _buy_item(game.player, item_id)

    if not result["success"]:
        return result["message"]

    player = game.player
    item = result["item"]

    # 자동 저장
    from tools.save import auto_save
    await auto_save(f"상점 구매: {item.name}")

    return f"""
═══════════════════════════════════════════════════
  🛒 구매 완료!
═══════════════════════════════════════════════════

  {result['message']}

  아이템: {item.name}
  가격: {item.price}G
  남은 골드: {player.gold}G

  💾 자동 저장됨
═══════════════════════════════════════════════════
"""


async def sell(item_id: str) -> str:
    """
    아이템을 판매합니다. (구매가의 50%)

    Args:
        item_id: 아이템 ID

    Returns:
        판매 결과
    """
    game = GameState.current()
    if not game:
        return "❌ 진행 중인 게임이 없습니다."

    room = game.current_room
    if room.type != RoomType.SHOP:
        return "❌ 현재 위치에 상점이 없습니다."

    result = await _sell_item(game.player, item_id)

    if not result["success"]:
        return result["message"]

    player = game.player
    item = result["item"]

    # 자동 저장
    from tools.save import auto_save
    await auto_save(f"상점 판매: {item.name}")

    return f"""
═══════════════════════════════════════════════════
  💰 판매 완료!
═══════════════════════════════════════════════════

  {result['message']}

  아이템: {item.name}
  판매가: {result['gold']}G
  보유 골드: {player.gold}G

  💾 자동 저장됨
═══════════════════════════════════════════════════
"""
