"""상점 시스템"""
from typing import Any, Optional
from repository.item_repo import ItemRepository
from models.item import Item


class ShopState:
    """상점 상태 (방문 중인 상점의 아이템 목록)"""
    _current_items: list[Item] = []

    @classmethod
    def set_items(cls, items: list[Item]) -> None:
        cls._current_items = items

    @classmethod
    def get_items(cls) -> list[Item]:
        return cls._current_items

    @classmethod
    def get_item(cls, item_id: str) -> Optional[Item]:
        return next((i for i in cls._current_items if i.id == item_id), None)

    @classmethod
    def remove_item(cls, item_id: str) -> None:
        """상점 목록에서 아이템 제거 (장비류 구매 시)"""
        cls._current_items = [i for i in cls._current_items if i.id != item_id]

    @classmethod
    def clear(cls) -> None:
        cls._current_items = []


async def open_shop(floor: int, no_potions: bool = False) -> list[Item]:
    """
    상점 열기 - 판매 아이템 생성

    Args:
        floor: 현재 층
        no_potions: Phase 2 승천 2+ - 포션 판매 안 함

    Returns:
        판매 아이템 목록
    """
    items = await ItemRepository.get_shop_items(floor, count=6)

    # Phase 2: 승천 2+ 효과 - 포션 판매 안 함
    if no_potions:
        potion_ids = ["hp_potion_s", "hp_potion_m", "hp_potion_l",
                      "mp_potion_s", "mp_potion_m", "elixir", "antidote"]
        items = [i for i in items if i.id not in potion_ids]

    ShopState.set_items(items)
    return items


def get_shop_items() -> list[Item]:
    """현재 상점 아이템 목록"""
    return ShopState.get_items()


async def buy_item(player: Any, item_id: str) -> dict:
    """
    아이템 구매

    Returns:
        {
            "success": 성공 여부,
            "item": 구매한 아이템,
            "message": 결과 메시지,
        }
    """
    item = ShopState.get_item(item_id)

    if not item:
        return {
            "success": False,
            "item": None,
            "message": "❌ 해당 아이템이 상점에 없습니다.",
        }

    # Phase 3: 듀오 할인 (황금 손)
    from systems.blessing import get_duo_combat_effects
    duo_effects = get_duo_combat_effects(player)
    shop_discount = duo_effects.get("shop_discount", 0)
    actual_price = int(item.price * (1 - shop_discount))

    if player.gold < actual_price:
        price_text = f"{actual_price}G (원가: {item.price}G)" if shop_discount > 0 else f"{item.price}G"
        return {
            "success": False,
            "item": item,
            "message": f"❌ 골드가 부족합니다. (필요: {price_text}, 보유: {player.gold}G)",
        }

    if not player.can_add_item():
        return {
            "success": False,
            "item": item,
            "message": "❌ 인벤토리가 가득 찼습니다.",
        }

    # v5.0 포션 슬롯 제한 체크
    from state.game_state import GameState
    from config import ResourceConfig
    game = GameState.current()
    if game and game.is_potion(item.id) and not game.can_add_potion():
        return {
            "success": False,
            "item": item,
            "message": f"❌ 포션 슬롯이 가득 찼습니다. (최대 {ResourceConfig.MAX_POTION_SLOTS}개)",
        }

    # 구매 처리 (할인 적용된 가격)
    player.spend_gold(actual_price)
    player.add_item(item.id)

    # 장비류는 구매 후 상점 목록에서 제거 (소비 아이템은 유지)
    equipment_types = ["weapon", "armor", "helmet", "accessory"]
    if item.type.value in equipment_types:
        ShopState.remove_item(item_id)

    # Phase 3: 할인 메시지
    if shop_discount > 0:
        discount_percent = int(shop_discount * 100)
        return {
            "success": True,
            "item": item,
            "message": f"✅ {item.name}을(를) {actual_price}G에 구매했습니다! (✋💰 황금 손 -{discount_percent}%)",
        }

    return {
        "success": True,
        "item": item,
        "message": f"✅ {item.name}을(를) {actual_price}G에 구매했습니다!",
    }


async def sell_item(player: Any, item_id: str) -> dict:
    """
    아이템 판매 (50% 가격)

    Returns:
        {
            "success": 성공 여부,
            "item": 판매한 아이템,
            "gold": 획득 골드,
            "message": 결과 메시지,
        }
    """
    if item_id not in player.inventory:
        return {
            "success": False,
            "item": None,
            "gold": 0,
            "message": "❌ 해당 아이템을 보유하고 있지 않습니다.",
        }

    item = await ItemRepository.get_by_id(item_id)
    if not item:
        return {
            "success": False,
            "item": None,
            "gold": 0,
            "message": "❌ 존재하지 않는 아이템입니다.",
        }

    # 장착 중인 아이템은 판매 불가
    for slot, equipped_id in player.equipment.items():
        if equipped_id == item_id:
            return {
                "success": False,
                "item": item,
                "gold": 0,
                "message": f"❌ 장착 중인 아이템은 판매할 수 없습니다. 먼저 해제하세요.",
            }

    # 판매 처리 (50% 가격)
    sell_price = item.price // 2
    player.remove_item(item_id)
    player.add_gold(sell_price)

    return {
        "success": True,
        "item": item,
        "gold": sell_price,
        "message": f"✅ {item.name}을(를) {sell_price}G에 판매했습니다!",
    }


def close_shop() -> None:
    """상점 닫기"""
    ShopState.clear()
