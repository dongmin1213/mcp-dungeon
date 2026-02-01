"""메타 프로그레션 시스템"""
from models.profile import Profile
from models.meta import (
    UPGRADES, ACHIEVEMENTS, UNLOCKS,
    get_upgrade_by_id, get_achievement_by_id, get_unlock_by_id,
    Upgrade, Achievement
)


def get_upgrade_level(profile: Profile, upgrade_id: str) -> int:
    """업그레이드 현재 레벨 조회"""
    upgrade = get_upgrade_by_id(upgrade_id)
    if not upgrade:
        return 0
    return getattr(profile.upgrades, upgrade.stat_key, 0)


def can_purchase_upgrade(profile: Profile, upgrade_id: str) -> tuple[bool, str]:
    """업그레이드 구매 가능 여부 확인"""
    upgrade = get_upgrade_by_id(upgrade_id)
    if not upgrade:
        return False, "존재하지 않는 업그레이드입니다."

    current_level = get_upgrade_level(profile, upgrade_id)
    if current_level >= upgrade.max_level:
        return False, "이미 최대 레벨입니다."

    cost = upgrade.get_cost(current_level)
    if profile.souls < cost:
        return False, f"소울이 부족합니다. (필요: {cost}, 보유: {profile.souls})"

    return True, ""


def purchase_upgrade(profile: Profile, upgrade_id: str) -> tuple[bool, str, int]:
    """
    업그레이드 구매

    Returns:
        (성공여부, 메시지, 소비한 소울)
    """
    can, reason = can_purchase_upgrade(profile, upgrade_id)
    if not can:
        return False, reason, 0

    upgrade = get_upgrade_by_id(upgrade_id)
    current_level = get_upgrade_level(profile, upgrade_id)
    cost = upgrade.get_cost(current_level)

    # 소울 소비
    profile.spend_souls(cost)

    # 업그레이드 레벨 증가
    setattr(profile.upgrades, upgrade.stat_key, current_level + 1)

    new_level = current_level + 1
    return True, f"{upgrade.name} Lv.{new_level} 업그레이드 완료!", cost


def check_achievement_condition(profile: Profile, achievement: Achievement) -> bool:
    """업적 달성 조건 확인"""
    stats = profile.stats
    condition = achievement.condition_type
    value = achievement.condition_value

    if condition == "monsters_killed":
        return stats.total_monsters_killed >= value
    elif condition == "bosses_killed":
        return stats.total_bosses_killed >= value
    elif condition == "runs_completed":
        return stats.total_runs >= value
    elif condition == "highest_floor":
        return stats.highest_floor >= value
    elif condition == "highest_level":
        return stats.highest_level >= value
    elif condition == "gold_earned":
        return stats.total_gold_earned >= value
    elif condition == "souls_earned":
        return stats.total_souls_earned >= value
    elif condition == "victories":
        return stats.total_victories >= value
    elif condition == "fastest_clear":
        if stats.fastest_clear_time is None:
            return False
        return stats.fastest_clear_time <= value

    return False


def check_and_complete_achievements(profile: Profile) -> list[tuple[Achievement, str | int]]:
    """
    달성 가능한 모든 업적 확인 및 완료 처리

    Returns:
        완료된 업적과 보상 리스트
    """
    completed = []

    for achievement in ACHIEVEMENTS:
        # 이미 완료된 업적 스킵
        if achievement.id in profile.completed_achievements:
            continue

        # 조건 확인
        if not check_achievement_condition(profile, achievement):
            continue

        # 업적 완료
        profile.complete_achievement(achievement.id)

        # 보상 지급
        reward = apply_achievement_reward(profile, achievement)
        completed.append((achievement, reward))

    return completed


def apply_achievement_reward(profile: Profile, achievement: Achievement) -> str | int:
    """업적 보상 적용"""
    reward_type = achievement.reward_type
    reward_value = achievement.reward_value

    if reward_type == "souls":
        amount = int(reward_value)
        profile.add_souls(amount)
        return amount
    elif reward_type == "unlock_class":
        profile.unlock_class(str(reward_value))
        return reward_value
    elif reward_type == "unlock_item":
        profile.unlock_item(str(reward_value))
        return reward_value
    elif reward_type == "unlock_mode":
        profile.unlock_mode(str(reward_value))
        return reward_value

    return 0


def can_unlock(profile: Profile, unlock_id: str) -> tuple[bool, str]:
    """언락 가능 여부 확인"""
    unlock = get_unlock_by_id(unlock_id)
    if not unlock:
        return False, "존재하지 않는 언락입니다."

    # 이미 언락됨
    if unlock.type == "class" and unlock_id in profile.unlocked_classes:
        return False, "이미 해금되었습니다."
    if unlock.type == "mode" and unlock_id in profile.unlocked_modes:
        return False, "이미 해금되었습니다."
    if unlock.type == "item" and unlock_id in profile.unlocked_items:
        return False, "이미 해금되었습니다."

    # 조건 확인
    if unlock.requirement_type == "achievement":
        if unlock.requirement_value not in profile.completed_achievements:
            achievement = get_achievement_by_id(unlock.requirement_value)
            if achievement:
                return False, f"업적 '{achievement.name}'을 먼저 달성해야 합니다."
            return False, "필요한 업적을 달성하지 못했습니다."

    elif unlock.requirement_type == "stat":
        # format: "stat_name:value"
        parts = unlock.requirement_value.split(":")
        if len(parts) == 2:
            stat_name, required = parts[0], int(parts[1])
            current = getattr(profile.stats, f"total_{stat_name}", 0)
            if stat_name == "victories":
                current = profile.stats.total_victories
            elif stat_name == "runs_completed":
                current = profile.stats.total_runs
            if current < required:
                return False, f"{stat_name} {required} 이상 필요합니다. (현재: {current})"

    # 비용 확인
    if unlock.cost > 0 and profile.souls < unlock.cost:
        return False, f"소울이 부족합니다. (필요: {unlock.cost}, 보유: {profile.souls})"

    return True, ""


def perform_unlock(profile: Profile, unlock_id: str) -> tuple[bool, str]:
    """언락 수행"""
    can, reason = can_unlock(profile, unlock_id)
    if not can:
        return False, reason

    unlock = get_unlock_by_id(unlock_id)

    # 비용 지불
    if unlock.cost > 0:
        profile.spend_souls(unlock.cost)

    # 언락 적용
    if unlock.type == "class":
        profile.unlock_class(unlock_id)
        return True, f"직업 '{unlock.name}' 해금 완료!"
    elif unlock.type == "mode":
        profile.unlock_mode(unlock_id)
        return True, f"모드 '{unlock.name}' 해금 완료!"
    elif unlock.type == "item":
        profile.unlock_item(unlock_id)
        return True, f"아이템 '{unlock.name}' 해금 완료!"

    return False, "알 수 없는 언락 타입입니다."


def get_available_upgrades(profile: Profile) -> list[dict]:
    """구매 가능한 업그레이드 목록"""
    result = []
    for upgrade in UPGRADES:
        current_level = get_upgrade_level(profile, upgrade.id)
        cost = upgrade.get_cost(current_level)

        result.append({
            "id": upgrade.id,
            "name": upgrade.name,
            "description": upgrade.description,
            "current_level": current_level,
            "max_level": upgrade.max_level,
            "cost": cost if cost > 0 else "MAX",
            "can_purchase": cost > 0 and profile.souls >= cost,
        })
    return result


def get_achievement_progress(profile: Profile) -> list[dict]:
    """업적 진행 상황"""
    result = []
    for achievement in ACHIEVEMENTS:
        if achievement.hidden and achievement.id not in profile.completed_achievements:
            continue

        completed = achievement.id in profile.completed_achievements
        progress = get_achievement_progress_value(profile, achievement)

        result.append({
            "id": achievement.id,
            "name": achievement.name,
            "description": achievement.description,
            "category": achievement.category,
            "completed": completed,
            "progress": progress,
            "target": achievement.condition_value,
            "reward_type": achievement.reward_type,
            "reward_value": achievement.reward_value,
        })
    return result


def get_achievement_progress_value(profile: Profile, achievement: Achievement) -> int:
    """업적 진행도 값"""
    stats = profile.stats
    condition = achievement.condition_type

    if condition == "monsters_killed":
        return stats.total_monsters_killed
    elif condition == "bosses_killed":
        return stats.total_bosses_killed
    elif condition == "runs_completed":
        return stats.total_runs
    elif condition == "highest_floor":
        return stats.highest_floor
    elif condition == "highest_level":
        return stats.highest_level
    elif condition == "gold_earned":
        return stats.total_gold_earned
    elif condition == "souls_earned":
        return stats.total_souls_earned
    elif condition == "victories":
        return stats.total_victories
    elif condition == "fastest_clear":
        return stats.fastest_clear_time or 9999

    return 0


def get_unlock_status(profile: Profile) -> list[dict]:
    """언락 상태"""
    result = []
    for unlock in UNLOCKS:
        # 이미 언락됨
        is_unlocked = False
        if unlock.type == "class":
            is_unlocked = unlock.id in profile.unlocked_classes
        elif unlock.type == "mode":
            is_unlocked = unlock.id in profile.unlocked_modes
        elif unlock.type == "item":
            is_unlocked = unlock.id in profile.unlocked_items

        can, reason = can_unlock(profile, unlock.id)

        result.append({
            "id": unlock.id,
            "name": unlock.name,
            "type": unlock.type,
            "cost": unlock.cost,
            "is_unlocked": is_unlocked,
            "can_unlock": can and not is_unlocked,
            "requirement": reason if not is_unlocked and not can else None,
        })
    return result
