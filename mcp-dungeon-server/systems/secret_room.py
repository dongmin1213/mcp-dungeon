"""v5.0 비밀 방 시스템"""
from typing import Any, Optional
from enum import Enum


class SecretRoomType(str, Enum):
    """비밀 방 종류"""
    SURVIVOR = "survivor"  # 생존자의 방 (HP 10% 이하로 층 클리어)
    PACIFIST = "pacifist"  # 평화주의자의 방 (전투 0회로 보스방 도달)
    EXPLORER = "explorer"  # 탐험가의 방 (모든 방 탐험)
    LUCKY = "lucky"  # 행운의 방 (20% 확률)
    HOARDER = "hoarder"  # 수집가의 방 (인벤토리 80% 이상)


# 비밀 방 보상
SECRET_ROOM_REWARDS = {
    SecretRoomType.SURVIVOR: {
        "name": "생존자의 방",
        "description": "극한의 생존자에게 주어지는 보상",
        "full_heal": True,
        "bonus_gold": 200,
        "item_grade": "rare"
    },
    SecretRoomType.PACIFIST: {
        "name": "평화주의자의 방",
        "description": "피를 묻히지 않은 자에게 주어지는 보상",
        "full_heal": True,
        "bonus_exp": 150,
        "special_item": "peace_amulet"  # 특수 아이템 (없으면 대체)
    },
    SecretRoomType.EXPLORER: {
        "name": "탐험가의 방",
        "description": "모든 것을 찾아낸 자에게 주어지는 보상",
        "bonus_gold": 300,
        "bonus_souls": 30,
        "item_grade": "legendary"
    },
    SecretRoomType.LUCKY: {
        "name": "행운의 방",
        "description": "행운이 따르는 자에게...",
        "random_blessing": True,
        "bonus_gold": 100
    },
    SecretRoomType.HOARDER: {
        "name": "수집가의 방",
        "description": "많이 모은 자에게 더 많은 것을...",
        "bonus_gold": 500,
        "inventory_upgrade": 5  # 인벤토리 +5칸 (미구현시 골드 대체)
    },
}


async def check_secret_room_conditions(game_state: Any) -> Optional[SecretRoomType]:
    """
    비밀 방 조건 확인

    Returns:
        충족된 비밀 방 타입 (없으면 None)
    """
    import random

    player = game_state.player
    dungeon = game_state.dungeon

    # 1. 생존자 조건: HP 10% 이하
    if player.hp <= player.max_hp * 0.1:
        return SecretRoomType.SURVIVOR

    # 2. 평화주의자 조건: 이번 층 전투 0회
    if getattr(game_state, 'floor_combats', 0) == 0:
        return SecretRoomType.PACIFIST

    # 3. 탐험가 조건: 모든 방 방문
    all_visited = True
    for row in dungeon.rooms:
        for room in row:
            if room.can_enter and not room.visited:
                all_visited = False
                break
    if all_visited:
        return SecretRoomType.EXPLORER

    # 4. 수집가 조건: 인벤토리 80% 이상
    if len(player.inventory) >= 16:  # 20 * 0.8
        return SecretRoomType.HOARDER

    # 5. 행운의 방: 20% 확률
    if random.random() < 0.20:
        return SecretRoomType.LUCKY

    return None


async def enter_secret_room(game_state: Any, room_type: SecretRoomType) -> dict:
    """
    비밀 방 입장 처리

    Returns:
        {"success": bool, "message": str, "rewards": dict}
    """
    from repository.item_repo import ItemRepository
    from systems.blessing import generate_blessing_choices, apply_blessing

    player = game_state.player
    rewards = SECRET_ROOM_REWARDS.get(room_type, {})

    messages = [
        "═══════════════════════════════════════════════════",
        f"  ★ 비밀 방 발견! - {rewards.get('name', '???')}",
        "═══════════════════════════════════════════════════",
        "",
        f"  {rewards.get('description', '')}",
        "",
    ]

    result_rewards = {}

    # 전체 회복
    if rewards.get("full_heal"):
        player.hp = player.max_hp
        player.mp = player.max_mp
        messages.append("  ✨ HP/MP가 전부 회복되었습니다!")
        result_rewards["full_heal"] = True

    # 골드 보너스
    if rewards.get("bonus_gold"):
        gold = rewards["bonus_gold"]
        player.add_gold(gold)
        messages.append(f"  💰 +{gold}G 획득!")
        result_rewards["gold"] = gold

    # 경험치 보너스
    if rewards.get("bonus_exp"):
        exp = rewards["bonus_exp"]
        level_ups = player.add_exp(exp)
        messages.append(f"  ⭐ +{exp} 경험치!")
        if level_ups:
            messages.append(f"  🎉 레벨 업! Lv.{player.level}")
        result_rewards["exp"] = exp

    # 소울 보너스
    if rewards.get("bonus_souls"):
        souls = rewards["bonus_souls"]
        game_state.souls_earned += souls
        messages.append(f"  👻 +{souls} 소울!")
        result_rewards["souls"] = souls

    # 아이템 등급
    if rewards.get("item_grade"):
        grade = rewards["item_grade"]
        item = await ItemRepository.get_random_by_grade(game_state.floor, grade)
        if item and player.can_add_item():
            # v5.0 포션 슬롯 제한 체크
            from state.game_state import GameState
            gs = GameState.current()
            if gs and gs.is_potion(item.id) and not gs.can_add_potion():
                messages.append(f"  ⚠️ 포션 슬롯 부족으로 {item.name}을 버렸습니다.")
            else:
                player.add_item(item.id)
                messages.append(f"  🎁 {item.grade_icon} {item.name} 획득!")
                result_rewards["item"] = item.id

    # 랜덤 축복
    if rewards.get("random_blessing"):
        from models.blessing import PlayerBlessings
        blessings = generate_blessing_choices(
            player.blessings if hasattr(player, 'blessings') else [],
            count=1,
            floor=game_state.floor
        )
        if blessings:
            blessing = blessings[0]
            apply_blessing(player, blessing)
            messages.append(f"  🎁 축복 [{blessing.name}] 획득!")
            result_rewards["blessing"] = blessing.name

    messages.extend([
        "",
        "═══════════════════════════════════════════════════",
    ])

    return {
        "success": True,
        "message": "\n".join(messages),
        "rewards": result_rewards
    }


def get_secret_room_hint(room_type: SecretRoomType) -> str:
    """비밀 방 힌트"""
    hints = {
        SecretRoomType.SURVIVOR: "죽음의 문턱에서 살아남으면...",
        SecretRoomType.PACIFIST: "전투를 피해 보스에게 도달하면...",
        SecretRoomType.EXPLORER: "모든 구석을 탐험하면...",
        SecretRoomType.LUCKY: "행운은 준비된 자에게...",
        SecretRoomType.HOARDER: "많이 모으면 더 많은 것을...",
    }
    return hints.get(room_type, "???")
