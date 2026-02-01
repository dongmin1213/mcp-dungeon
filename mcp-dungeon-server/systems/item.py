"""아이템 시스템"""
import random
from typing import Any, Optional
from repository.item_repo import ItemRepository
from models.item import Item, ItemType


# 행운의 주사위 효과 테이블 (확률 가중치 기반)
LUCKY_DICE_EFFECTS = [
    # 긍정적 효과 (70%)
    {"id": "small_gold", "weight": 25, "type": "positive",
     "message": "🪙 주사위에서 동전이 쏟아집니다!",
     "gold": (30, 50)},
    {"id": "heal_hp", "weight": 15, "type": "positive",
     "message": "❤️ 따뜻한 기운이 몸을 감쌉니다!",
     "heal_hp": (40, 60)},
    {"id": "heal_mp", "weight": 10, "type": "positive",
     "message": "💧 마력이 충전됩니다!",
     "heal_mp": (25, 40)},
    {"id": "medium_gold", "weight": 10, "type": "positive",
     "message": "💰 주사위가 황금빛으로 빛납니다!",
     "gold": (80, 120)},
    {"id": "full_heal", "weight": 5, "type": "positive",
     "message": "✨ 눈부신 빛이 모든 상처를 치유합니다!",
     "full_heal": True},
    {"id": "jackpot", "weight": 3, "type": "positive",
     "message": "💎 대박! 주사위가 보석으로 변합니다!",
     "gold": (200, 300)},
    {"id": "item_drop", "weight": 2, "type": "positive",
     "message": "🎁 주사위에서 무언가 나타납니다!",
     "item": True},
    # 부정적 효과 (30%)
    {"id": "damage", "weight": 15, "type": "negative",
     "message": "💥 주사위가 폭발합니다!",
     "damage": (15, 25)},
    {"id": "gold_loss", "weight": 10, "type": "negative",
     "message": "💸 주사위가 주머니 속 금화를 먹어버립니다...",
     "gold_loss": (30, 50)},
    {"id": "nothing", "weight": 5, "type": "negative",
     "message": "😑 ...아무 일도 일어나지 않았다.",
     "nothing": True},
]


async def _roll_lucky_dice(player: Any) -> dict:
    """
    행운의 주사위 효과 처리

    Returns:
        {"effects": [...], "message": "결과 메시지"}
    """
    # 가중치 기반 랜덤 선택
    total_weight = sum(e["weight"] for e in LUCKY_DICE_EFFECTS)
    roll = random.uniform(0, total_weight)

    cumulative = 0
    selected = LUCKY_DICE_EFFECTS[0]
    for effect in LUCKY_DICE_EFFECTS:
        cumulative += effect["weight"]
        if roll <= cumulative:
            selected = effect
            break

    effects = []
    messages = ["🎲 행운의 주사위를 굴립니다...", "", selected["message"]]

    # 효과 적용
    if "gold" in selected:
        amount = random.randint(*selected["gold"])
        player.add_gold(amount)
        effects.append(("gold", amount))
        messages.append(f"   +{amount}G 획득!")

    if "heal_hp" in selected:
        amount = random.randint(*selected["heal_hp"])
        actual = player.heal(amount)
        effects.append(("heal_hp", actual))
        messages.append(f"   HP +{actual} 회복!")

    if "heal_mp" in selected:
        amount = random.randint(*selected["heal_mp"])
        actual = player.heal_mp(amount)
        effects.append(("heal_mp", actual))
        messages.append(f"   MP +{actual} 회복!")

    if "full_heal" in selected:
        hp_healed = player.max_hp - player.hp
        mp_healed = player.max_mp - player.mp
        player.hp = player.max_hp
        player.mp = player.max_mp
        effects.append(("full_heal", True))
        messages.append(f"   HP/MP 전부 회복!")

    if "item" in selected:
        # 랜덤 포션 지급
        potions = ["hp_potion_s", "hp_potion_m", "mp_potion_s", "mp_potion_m"]
        potion_names = {
            "hp_potion_s": "소형 HP 포션",
            "hp_potion_m": "중형 HP 포션",
            "mp_potion_s": "소형 MP 포션",
            "mp_potion_m": "중형 MP 포션",
        }
        chosen = random.choice(potions)
        if player.can_add_item():
            player.add_item(chosen)
            effects.append(("item", chosen))
            messages.append(f"   🧪 {potion_names[chosen]} 획득!")
        else:
            # 인벤토리 가득 차면 골드로 대체
            player.add_gold(50)
            effects.append(("gold", 50))
            messages.append(f"   (인벤토리 가득) +50G로 대체!")

    if "damage" in selected:
        amount = random.randint(*selected["damage"])
        player.take_damage(amount)
        effects.append(("damage", amount))
        messages.append(f"   💔 {amount} 데미지!")
        if not player.is_alive:
            messages.append("   💀 치명상을 입었습니다...")

    if "gold_loss" in selected:
        amount = random.randint(*selected["gold_loss"])
        actual_loss = min(amount, player.gold)  # 보유량 이상 잃지 않음
        player.spend_gold(actual_loss)
        effects.append(("gold_loss", actual_loss))
        if actual_loss > 0:
            messages.append(f"   -{actual_loss}G 손실...")
        else:
            messages.append(f"   (잃을 골드가 없어서 무효!)")

    if "nothing" in selected:
        effects.append(("nothing", True))

    return {
        "effects": effects,
        "message": "\n".join(messages),
        "effect_type": selected["type"],
    }


async def use_item(player: Any, item_id: str) -> dict:
    """
    아이템 사용 (소비 아이템만)

    Returns:
        {
            "success": 성공 여부,
            "item": 사용한 아이템,
            "effects": 적용된 효과,
            "message": 결과 메시지,
        }
    """
    if item_id not in player.inventory:
        return {
            "success": False,
            "item": None,
            "effects": [],
            "message": "❌ 해당 아이템을 보유하고 있지 않습니다.",
        }

    item = await ItemRepository.get_by_id(item_id)
    if not item:
        return {
            "success": False,
            "item": None,
            "effects": [],
            "message": "❌ 존재하지 않는 아이템입니다.",
        }

    # 사용 가능한 아이템 타입 확인 (소비 아이템 + 일부 특수 아이템)
    usable_types = [ItemType.CONSUMABLE, ItemType.SPECIAL]
    if item.type not in usable_types:
        return {
            "success": False,
            "item": item,
            "effects": [],
            "message": f"❌ {item.name}은(는) 사용할 수 없는 아이템입니다.",
        }

    # 아이템 효과 적용
    effect = item.effect or {}

    # 행운의 주사위 특수 처리
    if "random_dice" in effect:
        player.remove_item(item_id)
        dice_result = await _roll_lucky_dice(player)
        return {
            "success": True,
            "item": item,
            "effects": dice_result["effects"],
            "message": dice_result["message"],
            "is_dice": True,
        }

    effects = []
    messages = [f"🧪 {item.name} 사용!"]

    # HP 회복
    if "heal_hp" in effect:
        actual = player.heal(effect["heal_hp"])
        effects.append(("heal_hp", actual))
        messages.append(f"❤️ HP +{actual}")

    # MP 회복
    if "heal_mp" in effect:
        actual = player.heal_mp(effect["heal_mp"])
        effects.append(("heal_mp", actual))
        messages.append(f"💧 MP +{actual}")

    # 상태 이상 치료
    if "cure" in effect:
        effects.append(("cure", effect["cure"]))
        messages.append(f"✨ {effect['cure']} 상태 해제!")

    # 확정 도망
    if "guaranteed_flee" in effect:
        effects.append(("guaranteed_flee", True))
        messages.append("💨 확정 도망!")

    # 맵 공개
    if "reveal_map" in effect:
        effects.append(("reveal_map", True))
        messages.append("🗺️ 지도가 공개되었습니다!")

    # 귀환
    if "teleport" in effect:
        effects.append(("teleport", effect["teleport"]))
        messages.append("✨ 이동합니다...")

    # 아이템 소모
    player.remove_item(item_id)

    return {
        "success": True,
        "item": item,
        "effects": effects,
        "message": "\n".join(messages),
    }


async def equip_item(player: Any, item_id: str) -> dict:
    """
    아이템 장착

    Returns:
        {
            "success": 성공 여부,
            "item": 장착한 아이템,
            "unequipped": 해제된 아이템 (있는 경우),
            "stat_change": 스탯 변화,
            "message": 결과 메시지,
        }
    """
    if item_id not in player.inventory:
        return {
            "success": False,
            "item": None,
            "unequipped": None,
            "stat_change": {},
            "message": "❌ 해당 아이템을 보유하고 있지 않습니다.",
        }

    item = await ItemRepository.get_by_id(item_id)
    if not item:
        return {
            "success": False,
            "item": None,
            "unequipped": None,
            "stat_change": {},
            "message": "❌ 존재하지 않는 아이템입니다.",
        }

    # 장착 가능 타입 확인
    equip_types = {
        ItemType.WEAPON: "weapon",
        ItemType.ARMOR: "armor",
        ItemType.HELMET: "helmet",
        ItemType.ACCESSORY: ["accessory1", "accessory2"],
    }

    if item.type not in equip_types:
        return {
            "success": False,
            "item": item,
            "unequipped": None,
            "stat_change": {},
            "message": f"❌ {item.name}은(는) 장착할 수 없는 아이템입니다.",
        }

    # 장착 슬롯 결정
    slots = equip_types[item.type]
    if isinstance(slots, list):
        # 장신구: 빈 슬롯 찾기
        slot = None
        for s in slots:
            if player.equipment.get(s) is None:
                slot = s
                break
        if slot is None:
            slot = slots[0]  # 없으면 첫 번째 슬롯에 덮어쓰기
    else:
        slot = slots

    # 기존 장비 해제
    unequipped = None
    unequipped_item = None
    old_item_id = player.equipment.get(slot)
    if old_item_id:
        unequipped_item = await ItemRepository.get_by_id(old_item_id)
        if unequipped_item:
            unequipped = unequipped_item
            # 기존 장비 스탯 제거
            player.atk -= unequipped_item.stat_atk
            player.def_ -= unequipped_item.stat_def
            player.max_hp -= unequipped_item.stat_hp
            player.max_mp -= unequipped_item.stat_mp

    # 새 장비 장착
    player.equipment[slot] = item_id

    # 새 장비 스탯 적용
    player.atk += item.stat_atk
    player.def_ += item.stat_def
    player.max_hp += item.stat_hp
    player.max_mp += item.stat_mp

    # HP/MP 조정 (최대치 초과 방지)
    if player.hp > player.max_hp:
        player.hp = player.max_hp
    if player.mp > player.max_mp:
        player.mp = player.max_mp

    # 스탯 변화 계산
    stat_change = {
        "atk": item.stat_atk - (unequipped_item.stat_atk if unequipped_item else 0),
        "def": item.stat_def - (unequipped_item.stat_def if unequipped_item else 0),
        "hp": item.stat_hp - (unequipped_item.stat_hp if unequipped_item else 0),
        "mp": item.stat_mp - (unequipped_item.stat_mp if unequipped_item else 0),
    }

    messages = [f"🛡️ {item.name} 장착!"]
    if unequipped:
        messages.append(f"   ({unequipped.name} 해제)")

    stat_msgs = []
    if stat_change["atk"] != 0:
        stat_msgs.append(f"ATK {'+' if stat_change['atk'] > 0 else ''}{stat_change['atk']}")
    if stat_change["def"] != 0:
        stat_msgs.append(f"DEF {'+' if stat_change['def'] > 0 else ''}{stat_change['def']}")
    if stat_change["hp"] != 0:
        stat_msgs.append(f"HP {'+' if stat_change['hp'] > 0 else ''}{stat_change['hp']}")
    if stat_change["mp"] != 0:
        stat_msgs.append(f"MP {'+' if stat_change['mp'] > 0 else ''}{stat_change['mp']}")

    if stat_msgs:
        messages.append(f"   스탯: {', '.join(stat_msgs)}")

    return {
        "success": True,
        "item": item,
        "unequipped": unequipped,
        "stat_change": stat_change,
        "message": "\n".join(messages),
        "curse": item.curse,  # v5.0 저주 정보
    }


async def unequip_item(player: Any, slot: str) -> dict:
    """
    아이템 장착 해제

    Args:
        slot: 장비 슬롯 (weapon/armor/helmet/accessory1/accessory2)

    Returns:
        {
            "success": 성공 여부,
            "item": 해제한 아이템,
            "message": 결과 메시지,
        }
    """
    valid_slots = ["weapon", "armor", "helmet", "accessory1", "accessory2"]
    if slot not in valid_slots:
        return {
            "success": False,
            "item": None,
            "message": f"❌ 잘못된 슬롯입니다. ({'/'.join(valid_slots)})",
        }

    item_id = player.equipment.get(slot)
    if not item_id:
        return {
            "success": False,
            "item": None,
            "message": f"❌ {slot} 슬롯에 장착된 아이템이 없습니다.",
        }

    item = await ItemRepository.get_by_id(item_id)
    if not item:
        return {
            "success": False,
            "item": None,
            "message": "❌ 아이템 정보를 찾을 수 없습니다.",
        }

    # 인벤토리 공간 확인
    if not player.can_add_item():
        return {
            "success": False,
            "item": item,
            "message": "❌ 인벤토리가 가득 차서 해제할 수 없습니다.",
        }

    # 장비 해제
    player.equipment[slot] = None

    # 스탯 제거
    player.atk -= item.stat_atk
    player.def_ -= item.stat_def
    player.max_hp -= item.stat_hp
    player.max_mp -= item.stat_mp

    # HP/MP 조정
    if player.hp > player.max_hp:
        player.hp = player.max_hp
    if player.mp > player.max_mp:
        player.mp = player.max_mp

    return {
        "success": True,
        "item": item,
        "message": f"🔓 {item.name} 장착 해제!",
    }


async def get_inventory_display(player: Any) -> dict:
    """
    인벤토리 표시용 데이터

    Returns:
        {
            "items": 아이템 목록 (상세 정보 포함),
            "equipment": 장착 장비 목록,
            "capacity": (현재/최대),
        }
    """
    items = []
    for item_id in player.inventory:
        item = await ItemRepository.get_by_id(item_id)
        if item:
            items.append({
                "id": item.id,
                "name": item.name,
                "type": item.type.value,
                "grade": item.grade.value,
                "description": item.description,
                "price": item.price,
                "curse": item.curse,  # v5.0 저주 정보
            })

    equipment = {}
    for slot, item_id in player.equipment.items():
        if item_id:
            item = await ItemRepository.get_by_id(item_id)
            if item:
                equipment[slot] = {
                    "id": item.id,
                    "name": item.name,
                    "grade": item.grade.value,  # v5.0 등급 추가
                    "stats": {
                        "atk": item.stat_atk,
                        "def": item.stat_def,
                        "hp": item.stat_hp,
                        "mp": item.stat_mp,
                    },
                    "curse": item.curse,  # v5.0 저주 정보
                }

    return {
        "items": items,
        "equipment": equipment,
        "capacity": (len(player.inventory), 20),  # MAX_INVENTORY_SIZE
    }
