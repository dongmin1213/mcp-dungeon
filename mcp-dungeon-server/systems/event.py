"""이벤트 처리 시스템"""
import random
from typing import Any
from config import GameConfig
from repository.event_repo import EventRepository
from repository.item_repo import ItemRepository


async def process_trap(floor: int, player: Any, damage_mult: float = 1.0) -> dict:
    """
    함정 이벤트 처리

    Args:
        floor: 현재 층
        player: 플레이어
        damage_mult: Phase 2 승천 데미지 배율 (기본 1.0)

    Returns:
        {
            "event": 이벤트 정보,
            "damage": 받은 데미지,
            "effects": 추가 효과들,
            "message": 결과 메시지,
        }
    """
    # v4.0: 함정 데미지 배율 적용 (Phase 2: 승천 배율 추가 적용)
    trap_mult = GameConfig.TRAP_DAMAGE_MULTIPLIER * damage_mult

    event = await EventRepository.get_trap(floor)
    if not event:
        # 기본 함정 (v4.0: 배율 적용)
        damage = int(player.max_hp * 0.15 * trap_mult)
        player.take_damage(damage)
        return {
            "event": {"name": "함정", "description": "함정에 걸렸다!"},
            "damage": damage,
            "effects": [],
            "message": f"함정에 걸려 {damage} 데미지를 받았습니다!",
        }

    effect = event.get("effect", {})
    damage = 0
    effects = []
    messages = [event["description"]]

    # 퍼센트 데미지 (v4.0: 배율 적용)
    if "damage_percent" in effect:
        damage = int(player.max_hp * effect["damage_percent"] * trap_mult)
        player.take_damage(damage)
        messages.append(f"💔 {damage} 데미지!")

    # 고정 데미지 (v4.0: 배율 적용)
    if "damage_flat" in effect:
        flat_damage = int(effect["damage_flat"] * trap_mult)
        player.take_damage(flat_damage)
        damage += flat_damage
        messages.append(f"💔 {flat_damage} 데미지!")

    # 상태 이상
    if "poison" in effect:
        effects.append(("poison", effect["poison"]))
        messages.append("🤢 독에 걸렸습니다!")

    if "debuff" in effect:
        effects.append(("debuff", effect["debuff"]))
        messages.append("⬇️ 능력치가 감소했습니다!")

    return {
        "event": event,
        "damage": damage,
        "effects": effects,
        "message": "\n".join(messages),
    }


async def process_treasure(floor: int, player: Any) -> dict:
    """
    보물 이벤트 처리

    Returns:
        {
            "event": 이벤트 정보,
            "gold": 획득 골드,
            "items": 획득 아이템 리스트,
            "message": 결과 메시지,
        }
    """
    event = await EventRepository.get_treasure(floor)
    if not event:
        # 기본 보물
        gold = random.randint(20, 50) + floor * 10
        player.add_gold(gold)
        return {
            "event": {"name": "보물 상자", "description": "보물 상자를 발견했다!"},
            "gold": gold,
            "items": [],
            "message": f"💰 {gold} 골드를 획득했습니다!",
        }

    rewards = event.get("rewards", {})
    messages = [event["description"]]
    items = []

    # 골드
    gold_min = rewards.get("gold_min", 20)
    gold_max = rewards.get("gold_max", 50)
    gold = random.randint(gold_min, gold_max) + floor * 5
    player.add_gold(gold)
    messages.append(f"💰 {gold} 골드 획득!")

    # 아이템
    item_chance = rewards.get("item_chance", 0)
    rare_chance = rewards.get("rare_chance", 0)

    if random.random() < item_chance:
        item = await ItemRepository.get_treasure_item(floor, rare_chance)
        if item and player.can_add_item():
            # v5.0 포션 슬롯 제한 체크
            from state.game_state import GameState
            game = GameState.current()
            if game and game.is_potion(item.id) and not game.can_add_potion():
                messages.append(f"⚠️ 포션 슬롯 부족으로 {item.name}을 버렸습니다.")
            else:
                player.add_item(item.id)
                items.append(item)
                messages.append(f"🎁 {item.name} 획득!")

    return {
        "event": event,
        "gold": gold,
        "items": items,
        "message": "\n".join(messages),
    }


async def process_rest(floor: int, player: Any, choice_id: str) -> dict:
    """
    휴식 이벤트 처리

    Args:
        choice_id: 선택한 행동 ID

    Returns:
        {
            "event": 이벤트 정보,
            "choice": 선택한 행동,
            "effects": 적용된 효과,
            "message": 결과 메시지,
        }
    """
    event = await EventRepository.get_rest(floor)
    if not event or not event.get("choices"):
        # 기본 휴식
        heal = int(player.max_hp * 0.30)
        actual = player.heal(heal)
        return {
            "event": {"name": "휴식처", "description": "잠시 쉬어간다."},
            "choice": None,
            "effects": [("heal_hp", actual)],
            "message": f"❤️ HP가 {actual} 회복되었습니다!",
        }

    # 선택지 찾기
    choices = event.get("choices", [])
    choice = next((c for c in choices if c["id"] == choice_id), None)

    if not choice:
        return {
            "event": event,
            "choice": None,
            "effects": [],
            "message": "❌ 잘못된 선택입니다.",
        }

    effect = choice.get("effect", {})
    effects = []
    messages = [choice.get("description", "")]

    # HP 회복
    if "heal_percent" in effect:
        heal = int(player.max_hp * effect["heal_percent"])
        actual = player.heal(heal)
        effects.append(("heal_hp", actual))
        messages.append(f"❤️ HP +{actual}")

    # MP 회복
    if "heal_mp_percent" in effect:
        heal = int(player.max_mp * effect["heal_mp_percent"])
        actual = player.heal_mp(heal)
        effects.append(("heal_mp", actual))
        messages.append(f"💧 MP +{actual}")

    # 버프
    if "buff" in effect:
        effects.append(("buff", effect["buff"]))
        messages.append("⬆️ 버프 적용!")

    return {
        "event": event,
        "choice": choice,
        "effects": effects,
        "message": "\n".join(messages),
    }


async def process_mystery(floor: int, player: Any, choice_id: str) -> dict:
    """
    미스터리 이벤트 처리

    Returns:
        {
            "event": 이벤트 정보,
            "choice": 선택한 행동,
            "result": 랜덤 결과 (있는 경우),
            "effects": 적용된 효과,
            "message": 결과 메시지,
        }
    """
    event = await EventRepository.get_mystery(floor)
    if not event:
        return {
            "event": None,
            "choice": None,
            "result": None,
            "effects": [],
            "message": "❓ 아무 일도 일어나지 않았습니다.",
        }

    # 선택지 찾기
    choices = event.get("choices", [])
    choice = next((c for c in choices if c["id"] == choice_id), None)

    if not choice:
        return {
            "event": event,
            "choice": None,
            "result": None,
            "effects": [],
            "message": "❌ 잘못된 선택입니다.",
        }

    # 요구사항 확인
    requires = choice.get("requires", {})
    if requires.get("gold", 0) > player.gold:
        return {
            "event": event,
            "choice": choice,
            "result": None,
            "effects": [],
            "message": "❌ 골드가 부족합니다.",
        }

    effect = choice.get("effect", {})

    # 골드 소모
    if "cost_gold" in effect:
        player.spend_gold(effect["cost_gold"])

    # 랜덤 효과
    if "random" in effect:
        return await _process_random_effect(event, choice, effect["random"], player)

    # 일반 효과
    return _process_normal_effect(event, choice, effect, player)


async def _process_random_effect(event: dict, choice: dict, random_effects: list, player: Any) -> dict:
    """랜덤 효과 처리"""
    # 가중치 기반 랜덤 선택
    total_weight = sum(r.get("weight", 1) for r in random_effects)
    roll = random.uniform(0, total_weight)

    cumulative = 0
    selected = random_effects[0]
    for r in random_effects:
        cumulative += r.get("weight", 1)
        if roll <= cumulative:
            selected = r
            break

    result = selected.get("result", {})
    message = selected.get("message", "")
    effects = []

    # 결과 적용
    effects = _apply_effect(result, player)

    return {
        "event": event,
        "choice": choice,
        "result": selected,
        "effects": effects,
        "message": message,
    }


def _process_normal_effect(event: dict, choice: dict, effect: dict, player: Any) -> dict:
    """일반 효과 처리"""
    effects = _apply_effect(effect, player)
    message = choice.get("description", "")

    return {
        "event": event,
        "choice": choice,
        "result": None,
        "effects": effects,
        "message": message,
    }


def _apply_effect(effect: dict, player: Any) -> list:
    """효과 적용"""
    applied = []

    # HP 회복
    if "heal_hp" in effect:
        actual = player.heal(effect["heal_hp"])
        applied.append(("heal_hp", actual))

    if "heal_percent" in effect:
        heal = int(player.max_hp * effect["heal_percent"])
        actual = player.heal(heal)
        applied.append(("heal_hp", actual))

    # MP 회복
    if "heal_mp" in effect:
        actual = player.heal_mp(effect["heal_mp"])
        applied.append(("heal_mp", actual))

    if "heal_mp_percent" in effect:
        heal = int(player.max_mp * effect["heal_mp_percent"])
        actual = player.heal_mp(heal)
        applied.append(("heal_mp", actual))

    # 데미지
    if "damage_percent" in effect:
        damage = int(player.max_hp * effect["damage_percent"])
        player.take_damage(damage)
        applied.append(("damage", damage))

    # 골드
    if "gold" in effect:
        if effect["gold"] > 0:
            player.add_gold(effect["gold"])
        else:
            player.spend_gold(abs(effect["gold"]))
        applied.append(("gold", effect["gold"]))

    # 경험치
    if "exp" in effect:
        player.add_exp(effect["exp"])
        applied.append(("exp", effect["exp"]))

    # 버프/디버프
    if "buff" in effect:
        applied.append(("buff", effect["buff"]))

    if "debuff" in effect:
        applied.append(("debuff", effect["debuff"]))

    return applied
