"""v5.0 악마의 거래 시스템"""
import random
from typing import Any, Optional


async def process_devil_deal(player: Any, game_state: Any, effect: dict) -> dict:
    """
    악마의 거래 효과 처리

    Returns:
        {"success": bool, "message": str, "rewards": list}
    """
    if not effect.get("devil_deal"):
        return {"success": False, "message": "악마의 거래가 아닙니다.", "rewards": []}

    messages = ["😈 악마와의 거래가 성사되었다..."]
    rewards = []
    success = True

    # 대가 처리
    # 최대 HP 감소
    if "max_hp_cost" in effect:
        cost = effect["max_hp_cost"]
        player.max_hp -= cost
        if player.hp > player.max_hp:
            player.hp = player.max_hp
        messages.append(f"💀 최대 HP -{cost}")

    # HP 비율 소모
    if "hp_cost_percent" in effect:
        percent = effect["hp_cost_percent"]
        cost = int(player.hp * percent)
        player.hp -= cost
        if player.hp <= 0:
            player.hp = 1  # 최소 1 HP 보장
        messages.append(f"🩸 HP -{cost} ({percent*100:.0f}%)")

    # 골드 전부 소모
    if effect.get("gold_cost_all"):
        cost = player.gold
        player.gold = 0
        messages.append(f"💰 골드 -{cost} (전부)")

    # 소울 소모
    if "soul_cost" in effect:
        cost = effect["soul_cost"]
        if game_state.souls_earned >= cost:
            game_state.souls_earned -= cost
            messages.append(f"👻 소울 -{cost}")
        else:
            return {"success": False, "message": "소울이 부족합니다.", "rewards": []}

    # 소울 획득량 패널티 (이번 런)
    if "soul_penalty_run" in effect:
        penalty = effect["soul_penalty_run"]
        # game_state에 패널티 저장
        if not hasattr(game_state, "soul_penalty"):
            game_state.soul_penalty = 1.0
        game_state.soul_penalty *= penalty
        messages.append(f"👻 이번 런 소울 획득량 -{int((1-penalty)*100)}%")

    # 보상 처리
    # 스킬 획득
    if "grant_skill" in effect:
        skill_id = effect["grant_skill"]
        if skill_id not in player.skills:
            player.skills.append(skill_id)
            rewards.append(("skill", skill_id))
            messages.append(f"✨ 스킬 [영혼 수확] 획득!")
        else:
            # 이미 있으면 ATK 보너스로 대체
            player.atk += 5
            rewards.append(("atk", 5))
            messages.append(f"✨ (스킬 대신) ATK +5")

    # 저주받은 아이템 획득
    if effect.get("grant_cursed_item"):
        from repository.item_repo import ItemRepository
        item = await ItemRepository.get_cursed_item(game_state.floor)
        if item and player.can_add_item():
            player.add_item(item.id)
            rewards.append(("item", item.id))
            messages.append(f"💀 저주받은 아이템 [{item.name}] 획득!")
        else:
            # 대체 보상
            player.atk += 8
            rewards.append(("atk", 8))
            messages.append(f"✨ (아이템 대신) ATK +8")

    # 축복 획득
    if "grant_blessing_count" in effect:
        count = effect["grant_blessing_count"]
        from systems.blessing import generate_blessing_choices, apply_blessing
        for _ in range(count):
            blessings = generate_blessing_choices(
                player.blessings,
                count=1,
                floor=game_state.floor,
                force_rare=True  # 희귀 이상 강제
            )
            if blessings:
                blessing = blessings[0]
                result = apply_blessing(player, blessing)
                rewards.append(("blessing", blessing.name))
                messages.append(f"🎁 축복 [{blessing.name}] 획득!")

    # 전설 아이템 획득
    if effect.get("grant_legendary_item"):
        from repository.item_repo import ItemRepository
        item = await ItemRepository.get_random_by_grade(game_state.floor, "legendary")
        if item and player.can_add_item():
            # v5.0 포션 슬롯 제한 체크
            if game_state.is_potion(item.id) and not game_state.can_add_potion():
                player.atk += 10
                player.def_ += 5
                rewards.append(("atk", 10))
                rewards.append(("def", 5))
                messages.append(f"✨ (포션 슬롯 부족) ATK +10, DEF +5")
            else:
                player.add_item(item.id)
                rewards.append(("item", item.id))
                messages.append(f"🟣 전설 아이템 [{item.name}] 획득!")
        else:
            # 대체 보상
            player.atk += 10
            player.def_ += 5
            rewards.append(("atk", 10))
            rewards.append(("def", 5))
            messages.append(f"✨ (아이템 대신) ATK +10, DEF +5")

    # 영구 ATK 증가
    if "permanent_atk" in effect:
        bonus = effect["permanent_atk"]
        player.atk += bonus
        rewards.append(("atk", bonus))
        messages.append(f"⚔️ ATK +{bonus} 영구 증가!")

    # 영구 DEF 증가
    if "permanent_def" in effect:
        bonus = effect["permanent_def"]
        player.def_ += bonus
        rewards.append(("def", bonus))
        messages.append(f"🛡️ DEF +{bonus} 영구 증가!")

    # 저주 제거
    if effect.get("remove_curse"):
        removed = await remove_equipped_curse(player)
        if removed:
            rewards.append(("curse_removed", removed))
            messages.append(f"✨ 저주 [{removed}] 제거됨!")
        else:
            # 제거할 저주 없으면 보너스로 대체
            player.max_hp += 20
            player.hp += 20
            rewards.append(("max_hp", 20))
            messages.append(f"❤️ (저주 없음) 최대 HP +20")

    return {
        "success": success,
        "message": "\n".join(messages),
        "rewards": rewards
    }


async def remove_equipped_curse(player: Any) -> Optional[str]:
    """장착 중인 저주받은 아이템 중 하나 제거"""
    from repository.item_repo import ItemRepository

    for slot, item_id in player.equipment.items():
        if item_id:
            item = await ItemRepository.get_by_id(item_id)
            if item and item.is_cursed:
                # 저주 해제 (아이템은 유지, 저주만 제거)
                # 실제로는 아이템을 일반 버전으로 교체하거나 저주 효과만 무효화
                # 여기서는 아이템 제거로 단순화
                player.equipment[slot] = None
                # 스탯 제거
                player.atk -= item.stat_atk
                player.def_ -= item.stat_def
                player.max_hp -= item.stat_hp
                player.max_mp -= item.stat_mp
                if player.hp > player.max_hp:
                    player.hp = player.max_hp
                if player.mp > player.max_mp:
                    player.mp = player.max_mp
                return item.name

    return None


def format_devil_deal_ui(event: dict, player: Any) -> str:
    """악마의 거래 UI 포맷"""
    lines = [
        "═══════════════════════════════════════════════════",
        "  😈 악마의 거래",
        "═══════════════════════════════════════════════════",
        "",
        f"  \"{event['description']}\"",
        "",
        "  [거래 목록]",
        "  ┌─────────────────────────────────────────────┐",
    ]

    choices = event.get("choices", [])
    for i, choice in enumerate(choices, 1):
        text = choice.get("text", "???")
        desc = choice.get("description", "")

        # 조건 확인
        requires = choice.get("requires", {})
        can_choose = True
        req_note = ""

        if "gold" in requires and player.gold < requires["gold"]:
            can_choose = False
            req_note = f" (골드 부족: {player.gold}/{requires['gold']}G)"
        if "souls" in requires:
            # souls 확인 로직 필요
            req_note = f" (소울 필요: {requires['souls']})"

        if can_choose:
            lines.append(f"  │ [{i}] {text}")
            lines.append(f"  │     {desc}{req_note}")
        else:
            lines.append(f"  │ [{i}] {text} ❌")
            lines.append(f"  │     {desc}{req_note}")

        if i < len(choices):
            lines.append("  ├─────────────────────────────────────────────┤")

    lines.extend([
        "  └─────────────────────────────────────────────┘",
        "",
        f"  현재 상태: HP {player.hp}/{player.max_hp} | 골드 {player.gold}G",
        "",
        "═══════════════════════════════════════════════════",
    ])

    return "\n".join(lines)
