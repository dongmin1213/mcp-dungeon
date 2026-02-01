"""메타 프로그레션 MCP 도구"""
from database import get_db
from repository.profile_repo import ProfileRepository
from systems.meta import (
    get_available_upgrades,
    get_achievement_progress,
    get_unlock_status,
    purchase_upgrade,
    perform_unlock,
    check_and_complete_achievements,
)
from config import CLASS_NAMES


async def get_profile() -> str:
    """
    플레이어 프로필을 조회합니다.

    Returns:
        프로필 정보
    """
    async with get_db() as db:
        repo = ProfileRepository(db)
        profile = await repo.get_or_create()

    stats = profile.stats
    bonuses = profile.get_starting_bonuses()

    output = f"""
═══════════════════════════════════════════════════
  👤 프로필: {profile.name}
═══════════════════════════════════════════════════

  💠 보유 소울: {profile.souls:,}

───────────────────────────────────────────────────
  📊 통계
───────────────────────────────────────────────────
  총 플레이: {stats.total_runs}회
  클리어: {stats.total_victories}회 | 사망: {stats.total_deaths}회
  클리어율: {(stats.total_victories / stats.total_runs * 100) if stats.total_runs > 0 else 0:.1f}%

  최고 기록:
    • 최고 도달 층: {stats.highest_floor}층
    • 최고 레벨: Lv.{stats.highest_level}
    • 최단 클리어: {_format_time(stats.fastest_clear_time)}

  누적 기록:
    • 처치한 몬스터: {stats.total_monsters_killed:,}마리
    • 처치한 보스: {stats.total_bosses_killed}마리
    • 획득한 골드: {stats.total_gold_earned:,}G
    • 획득한 소울: {stats.total_souls_earned:,}
    • 총 플레이 시간: {_format_time(stats.total_play_time)}

───────────────────────────────────────────────────
  ⬆️ 영구 보너스 (현재 적용)
───────────────────────────────────────────────────
  • HP +{bonuses['hp']} | MP +{bonuses['mp']}
  • ATK +{bonuses['atk']} | DEF +{bonuses['def_']}
  • 크리티컬 +{bonuses['crit_chance']*100:.0f}%
  • 골드 획득 +{(bonuses['gold_mult']-1)*100:.0f}%
  • 경험치 획득 +{(bonuses['exp_mult']-1)*100:.0f}%
  • 시작 골드 +{bonuses['gold']}G

───────────────────────────────────────────────────
  🔓 해금된 직업: {', '.join([CLASS_NAMES.get(c, c) for c in profile.unlocked_classes])}
  🎮 해금된 모드: {', '.join(profile.unlocked_modes)}
  🏆 완료한 업적: {len(profile.completed_achievements)}개

═══════════════════════════════════════════════════
"""
    return output


async def get_souls() -> str:
    """
    소울 정보 및 사용처를 조회합니다.

    Returns:
        소울 정보
    """
    async with get_db() as db:
        repo = ProfileRepository(db)
        profile = await repo.get_or_create()

    upgrades = get_available_upgrades(profile)
    affordable = [u for u in upgrades if u["can_purchase"]]

    output = f"""
═══════════════════════════════════════════════════
  💠 소울
═══════════════════════════════════════════════════

  보유: {profile.souls:,} 소울

───────────────────────────────────────────────────
  구매 가능한 업그레이드 ({len(affordable)}개)
───────────────────────────────────────────────────
"""

    for u in upgrades:
        if u["current_level"] >= u["max_level"]:
            status = "✅ MAX"
        elif u["can_purchase"]:
            status = f"💠 {u['cost']}"
        else:
            status = f"🔒 {u['cost']}"

        output += f"  • {u['name']} [{u['current_level']}/{u['max_level']}] - {status}\n"
        output += f"    {u['description']}\n"

    output += """
───────────────────────────────────────────────────
  💡 'upgrade [업그레이드ID]'로 구매하세요
     예: upgrade max_hp
═══════════════════════════════════════════════════
"""
    return output


async def upgrade(upgrade_id: str) -> str:
    """
    소울을 사용하여 영구 업그레이드를 구매합니다.

    Args:
        upgrade_id: 업그레이드 ID (max_hp, max_mp, atk, def, crit, gold, exp, potion, starting_gold, soul)

    Returns:
        구매 결과
    """
    async with get_db() as db:
        repo = ProfileRepository(db)
        profile = await repo.get_or_create()

        success, message, cost = purchase_upgrade(profile, upgrade_id)

        if success:
            await repo.save(profile)

    if success:
        # 자동 저장
        from tools.save import auto_save
        await auto_save(f"소울 업그레이드: {upgrade_id}")

        return f"""
═══════════════════════════════════════════════════
  ✅ 업그레이드 완료!
═══════════════════════════════════════════════════

  {message}
  소비한 소울: 💠 {cost}
  남은 소울: 💠 {profile.souls:,}

  💾 자동 저장됨
═══════════════════════════════════════════════════
"""
    else:
        return f"""
═══════════════════════════════════════════════════
  ❌ 업그레이드 실패
═══════════════════════════════════════════════════

  {message}

═══════════════════════════════════════════════════
"""


async def unlock(unlock_id: str) -> str:
    """
    직업, 모드, 아이템을 해금합니다.

    Args:
        unlock_id: 해금할 대상 ID

    Returns:
        해금 결과
    """
    async with get_db() as db:
        repo = ProfileRepository(db)
        profile = await repo.get_or_create()

        success, message = perform_unlock(profile, unlock_id)

        if success:
            await repo.save(profile)

    if success:
        return f"""
═══════════════════════════════════════════════════
  🔓 해금 완료!
═══════════════════════════════════════════════════

  {message}
  남은 소울: 💠 {profile.souls:,}

═══════════════════════════════════════════════════
"""
    else:
        return f"""
═══════════════════════════════════════════════════
  ❌ 해금 실패
═══════════════════════════════════════════════════

  {message}

═══════════════════════════════════════════════════
"""


async def get_achievements() -> str:
    """
    업적 목록과 진행 상황을 조회합니다.

    Returns:
        업적 정보
    """
    async with get_db() as db:
        repo = ProfileRepository(db)
        profile = await repo.get_or_create()

    achievements = get_achievement_progress(profile)

    # 카테고리별 분류
    categories = {
        "combat": ("⚔️ 전투", []),
        "explore": ("🗺️ 탐험", []),
        "collect": ("💰 수집", []),
        "challenge": ("🏆 도전", []),
    }

    for a in achievements:
        cat = a["category"]
        if cat in categories:
            categories[cat][1].append(a)

    completed_count = len([a for a in achievements if a["completed"]])

    output = f"""
═══════════════════════════════════════════════════
  🏆 업적 ({completed_count}/{len(achievements)})
═══════════════════════════════════════════════════
"""

    for cat_id, (cat_name, cat_achievements) in categories.items():
        if not cat_achievements:
            continue

        cat_completed = len([a for a in cat_achievements if a["completed"]])
        output += f"\n───────────────────────────────────────────────────\n"
        output += f"  {cat_name} ({cat_completed}/{len(cat_achievements)})\n"
        output += f"───────────────────────────────────────────────────\n"

        for a in cat_achievements:
            if a["completed"]:
                status = "✅"
                progress = "완료"
            else:
                status = "⬜"
                progress = f"{a['progress']}/{a['target']}"

            reward = _format_reward(a["reward_type"], a["reward_value"])
            output += f"  {status} {a['name']}\n"
            output += f"     {a['description']}\n"
            output += f"     진행: {progress} | 보상: {reward}\n"

    output += "\n═══════════════════════════════════════════════════"
    return output


async def get_unlocks() -> str:
    """
    해금 가능한 콘텐츠 목록을 조회합니다.

    Returns:
        해금 정보
    """
    async with get_db() as db:
        repo = ProfileRepository(db)
        profile = await repo.get_or_create()

    unlocks = get_unlock_status(profile)

    # 타입별 분류
    types = {
        "class": ("⚔️ 직업", []),
        "mode": ("🎮 모드", []),
        "item": ("📦 아이템", []),
    }

    for u in unlocks:
        t = u["type"]
        if t in types:
            types[t][1].append(u)

    output = f"""
═══════════════════════════════════════════════════
  🔓 해금 콘텐츠
═══════════════════════════════════════════════════

  보유 소울: 💠 {profile.souls:,}
"""

    for type_id, (type_name, type_unlocks) in types.items():
        if not type_unlocks:
            continue

        output += f"\n───────────────────────────────────────────────────\n"
        output += f"  {type_name}\n"
        output += f"───────────────────────────────────────────────────\n"

        for u in type_unlocks:
            if u["is_unlocked"]:
                status = "✅ 해금됨"
            elif u["can_unlock"]:
                cost = f"💠 {u['cost']}" if u["cost"] > 0 else "무료"
                status = f"🔓 {cost}"
            else:
                status = f"🔒 {u['requirement']}"

            output += f"  • {u['name']} ({u['id']}) - {status}\n"

    output += """
───────────────────────────────────────────────────
  💡 'unlock [ID]'로 해금하세요
     예: unlock infinite
═══════════════════════════════════════════════════
"""
    return output


def _format_time(seconds: int | None) -> str:
    """시간 포맷팅"""
    if seconds is None:
        return "-"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}시간 {minutes}분"
    elif minutes > 0:
        return f"{minutes}분 {secs}초"
    else:
        return f"{secs}초"


def _format_reward(reward_type: str, reward_value) -> str:
    """보상 포맷팅"""
    if reward_type == "souls":
        return f"💠 {reward_value} 소울"
    elif reward_type == "unlock_class":
        return f"🔓 직업: {CLASS_NAMES.get(str(reward_value), reward_value)}"
    elif reward_type == "unlock_mode":
        return f"🔓 모드: {reward_value}"
    elif reward_type == "unlock_item":
        return f"🔓 아이템: {reward_value}"
    return str(reward_value)
