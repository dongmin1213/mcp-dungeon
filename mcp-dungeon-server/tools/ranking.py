"""랭킹 MCP 도구"""
from typing import Optional
from database import get_db
from systems.ranking import RankingRepository
from config import CLASS_NAMES


async def get_ranking(mode: Optional[str] = None) -> str:
    """
    랭킹을 조회합니다.

    Args:
        mode: 모드 필터 (normal, hard, hell, infinite, 또는 None=전체)

    Returns:
        랭킹 정보
    """
    async with get_db() as db:
        repo = RankingRepository(db)
        rankings = await repo.get_top_rankings(mode=mode, limit=10)

    mode_name = mode.upper() if mode else "전체"

    output = f"""
═══════════════════════════════════════════════════
  🏆 랭킹 ({mode_name})
═══════════════════════════════════════════════════
"""

    if not rankings:
        output += "\n  아직 기록이 없습니다.\n"
    else:
        output += "\n  순위 | 점수     | 이름           | 클리어 | 층  | 레벨\n"
        output += "  ─────┼──────────┼────────────────┼────────┼─────┼──────\n"

        for i, entry in enumerate(rankings, 1):
            rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f" {i}"
            clear = "✅" if entry.victory else "💀"
            class_icon = _get_class_icon(entry.class_id)

            output += f"  {rank_emoji:>4} | {entry.score:>8,} | {class_icon} {entry.profile_name:<10} | {clear}     | {entry.floor:>3} | {entry.level:>3}\n"

    output += """
───────────────────────────────────────────────────
  💡 'get_ranking hard'로 특정 모드 랭킹 조회
     'get_records'로 개인 기록 조회
═══════════════════════════════════════════════════
"""
    return output


async def get_records() -> str:
    """
    개인 플레이 기록을 조회합니다.

    Returns:
        개인 기록 정보
    """
    async with get_db() as db:
        repo = RankingRepository(db)
        records = await repo.get_personal_rankings("default", limit=10)

    output = """
═══════════════════════════════════════════════════
  📜 내 플레이 기록
═══════════════════════════════════════════════════
"""

    if not records:
        output += "\n  아직 기록이 없습니다.\n"
        output += "  게임을 플레이하면 기록이 저장됩니다.\n"
    else:
        for i, entry in enumerate(records, 1):
            clear = "✅ 클리어" if entry.victory else "💀 사망"
            class_name = CLASS_NAMES.get(entry.class_id, entry.class_id)
            time_str = _format_time(entry.play_time)
            date_str = entry.created_at.strftime("%m/%d %H:%M")

            output += f"""
  [{i}] {entry.score:,}점 - {clear}
      {class_name} Lv.{entry.level} | {entry.floor}층 | {entry.mode}
      몬스터: {entry.monsters_killed}마리 | 보스: {entry.bosses_killed}마리
      시간: {time_str} | {date_str}
"""

    output += """
═══════════════════════════════════════════════════
"""
    return output


def _get_class_icon(class_id: str) -> str:
    """직업 아이콘"""
    icons = {
        "warrior": "⚔️",
        "archer": "🏹",
        "mage": "🔮",
        "rogue": "🗡️",
        "paladin": "🛡️",
        "reaper": "💀",
    }
    return icons.get(class_id, "👤")


def _format_time(seconds: int) -> str:
    """시간 포맷팅"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}시간 {minutes}분"
    else:
        return f"{minutes}분"
