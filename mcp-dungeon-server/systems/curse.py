"""v5.0 저주 시스템"""
from typing import Any, Optional
import random


# 저주 효과 설명
CURSE_DESCRIPTIONS = {
    "rest_heal_mult": "휴식 회복량 {value:.0%}",
    "no_combat_damage": "비전투 이동 시 {value} 데미지",
    "set_def_zero": "DEF가 0이 됨",
    "damage_per_turn": "매 턴 {value} 데미지",
    "no_flee": "도망 불가",
    "shop_price_mult": "상점 가격 +{extra:.0%}",
    "damage_taken_mult": "받는 데미지 +{extra:.0%}",
    "max_hp_penalty": "최대 HP -{value}",
    "potion_heal_mult": "포션 회복량 {value:.0%}",
    "random_effect_per_combat": "전투마다 효과 변동",
}


def get_player_curses(player: Any) -> list[dict]:
    """플레이어가 장착한 아이템의 저주 효과 목록"""
    from repository.item_repo import ItemRepository
    import asyncio

    curses = []

    # 동기 함수에서 비동기 호출을 위한 처리
    async def _get_curses():
        for slot, item_id in player.equipment.items():
            if item_id:
                item = await ItemRepository.get_by_id(item_id)
                if item and item.curse:
                    curses.append({
                        "item_id": item_id,
                        "item_name": item.name,
                        "curse": item.curse
                    })
        return curses

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 이미 실행 중인 루프에서는 직접 반환할 수 없음
            # 대신 저장된 정보 사용
            return curses
        return loop.run_until_complete(_get_curses())
    except RuntimeError:
        return curses


async def get_player_curses_async(player: Any) -> list[dict]:
    """플레이어가 장착한 아이템의 저주 효과 목록 (비동기)"""
    from repository.item_repo import ItemRepository

    curses = []

    for slot, item_id in player.equipment.items():
        if item_id:
            item = await ItemRepository.get_by_id(item_id)
            if item and item.curse:
                curses.append({
                    "item_id": item_id,
                    "item_name": item.name,
                    "curse": item.curse
                })

    return curses


async def get_curse_effect(player: Any, effect_name: str) -> Optional[Any]:
    """특정 저주 효과 값 반환"""
    curses = await get_player_curses_async(player)

    for curse_info in curses:
        curse = curse_info["curse"]
        if effect_name in curse:
            return curse[effect_name]

    return None


async def has_curse(player: Any, effect_name: str) -> bool:
    """특정 저주가 있는지 확인"""
    return await get_curse_effect(player, effect_name) is not None


async def apply_rest_heal_curse(player: Any, base_heal: int) -> int:
    """휴식 회복량에 저주 적용"""
    mult = await get_curse_effect(player, "rest_heal_mult")
    if mult is not None:
        return int(base_heal * mult)
    return base_heal


async def apply_potion_heal_curse(player: Any, base_heal: int) -> int:
    """포션 회복량에 저주 적용"""
    mult = await get_curse_effect(player, "potion_heal_mult")
    if mult is not None:
        return int(base_heal * mult)
    return base_heal


async def apply_damage_taken_curse(player: Any, base_damage: int) -> int:
    """받는 데미지에 저주 적용"""
    mult = await get_curse_effect(player, "damage_taken_mult")
    if mult is not None:
        return int(base_damage * mult)
    return base_damage


async def apply_shop_price_curse(player: Any, base_price: int) -> int:
    """상점 가격에 저주 적용"""
    mult = await get_curse_effect(player, "shop_price_mult")
    if mult is not None:
        return int(base_price * mult)
    return base_price


async def check_no_flee_curse(player: Any) -> bool:
    """도망 불가 저주 확인"""
    return await has_curse(player, "no_flee")


async def check_def_zero_curse(player: Any) -> bool:
    """DEF 0 저주 확인"""
    return await has_curse(player, "set_def_zero")


async def apply_turn_damage_curse(player: Any) -> tuple[int, str]:
    """턴당 데미지 저주 적용. (데미지, 메시지) 반환"""
    damage = await get_curse_effect(player, "damage_per_turn")
    if damage:
        actual = player.take_damage(damage)
        return actual, f"💀 저주로 인해 {actual} 데미지!"
    return 0, ""


async def apply_no_combat_damage_curse(player: Any) -> tuple[int, str]:
    """비전투 이동 시 데미지 저주 적용"""
    damage = await get_curse_effect(player, "no_combat_damage")
    if damage:
        actual = player.take_damage(damage)
        return actual, f"💀 갈증의 검이 피를 원합니다! {actual} 데미지!"
    return 0, ""


def get_curse_description(curse: dict) -> str:
    """저주 효과 설명 생성"""
    descriptions = []

    for key, value in curse.items():
        if key in CURSE_DESCRIPTIONS:
            template = CURSE_DESCRIPTIONS[key]
            if "{extra:.0%}" in template:
                # 배율 표시 (1.5 -> +50%)
                descriptions.append(template.format(extra=value - 1))
            elif "{value:.0%}" in template:
                # 배율 표시
                descriptions.append(template.format(value=value))
            elif "{value}" in template:
                descriptions.append(template.format(value=value))
            else:
                descriptions.append(template)

    return ", ".join(descriptions) if descriptions else "알 수 없는 저주"


async def apply_berserk_effect(player: Any) -> tuple[int, bool]:
    """광전사 효과 적용 (HP 30% 이하시 ATK +50%)"""
    curses = await get_player_curses_async(player)

    for curse_info in curses:
        effect = None
        # curse가 아닌 effect에서 berserk 확인
        from repository.item_repo import ItemRepository
        item = await ItemRepository.get_by_id(curse_info["item_id"])
        if item and item.effect and item.effect.get("berserk"):
            if player.hp <= player.max_hp * 0.3:
                bonus = int(player.atk * 0.5)
                return bonus, True

    return 0, False
