"""랭킹 시스템"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RankingEntry(BaseModel):
    """랭킹 엔트리"""
    id: Optional[int] = None
    profile_id: str
    profile_name: str
    class_id: str
    mode: str
    score: int
    floor: int
    level: int
    monsters_killed: int
    bosses_killed: int
    play_time: int
    victory: bool
    created_at: datetime


def calculate_score(
    victory: bool,
    floor: int,
    level: int,
    monsters_killed: int,
    bosses_killed: int,
    gold_earned: int,
    play_time: int,
    mode: str = "normal"
) -> int:
    """
    점수 계산

    공식:
    - 기본 점수 = 층 × 100 + 레벨 × 50
    - 전투 점수 = 몬스터 × 10 + 보스 × 100
    - 골드 점수 = 골드 / 10
    - 시간 보너스 = max(0, (3600 - 플레이시간) / 10) (1시간 이내 보너스)
    - 클리어 보너스 = 5000 (클리어 시)
    - 모드 배율 = normal: 1.0, hard: 1.5, hell: 2.0
    """
    base_score = floor * 100 + level * 50
    combat_score = monsters_killed * 10 + bosses_killed * 100
    gold_score = gold_earned // 10
    time_bonus = max(0, (3600 - play_time) // 10) if victory else 0
    clear_bonus = 5000 if victory else 0

    mode_mult = {"normal": 1.0, "hard": 1.5, "hell": 2.0, "infinite": 1.2}.get(mode, 1.0)

    total = int((base_score + combat_score + gold_score + time_bonus + clear_bonus) * mode_mult)
    return total


class RankingRepository:
    """랭킹 저장소"""

    def __init__(self, db):
        self.db = db

    async def add_entry(self, entry: RankingEntry) -> int:
        """랭킹 엔트리 추가. ID 반환"""
        cursor = await self.db.execute("""
            INSERT INTO rankings (
                profile_id, profile_name, class_id, mode, score,
                floor, level, monsters_killed, bosses_killed,
                play_time, victory, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.profile_id,
            entry.profile_name,
            entry.class_id,
            entry.mode,
            entry.score,
            entry.floor,
            entry.level,
            entry.monsters_killed,
            entry.bosses_killed,
            entry.play_time,
            entry.victory,
            entry.created_at.isoformat()
        ))
        await self.db.commit()
        return cursor.lastrowid

    async def get_top_rankings(
        self,
        mode: Optional[str] = None,
        limit: int = 10
    ) -> list[RankingEntry]:
        """상위 랭킹 조회"""
        if mode:
            cursor = await self.db.execute("""
                SELECT * FROM rankings
                WHERE mode = ?
                ORDER BY score DESC
                LIMIT ?
            """, (mode, limit))
        else:
            cursor = await self.db.execute("""
                SELECT * FROM rankings
                ORDER BY score DESC
                LIMIT ?
            """, (limit,))

        rows = await cursor.fetchall()
        return [self._row_to_entry(row) for row in rows]

    async def get_personal_rankings(
        self,
        profile_id: str,
        limit: int = 10
    ) -> list[RankingEntry]:
        """개인 랭킹 조회"""
        cursor = await self.db.execute("""
            SELECT * FROM rankings
            WHERE profile_id = ?
            ORDER BY score DESC
            LIMIT ?
        """, (profile_id, limit))

        rows = await cursor.fetchall()
        return [self._row_to_entry(row) for row in rows]

    async def get_rank(self, score: int, mode: Optional[str] = None) -> int:
        """특정 점수의 순위 조회"""
        if mode:
            cursor = await self.db.execute("""
                SELECT COUNT(*) FROM rankings
                WHERE mode = ? AND score > ?
            """, (mode, score))
        else:
            cursor = await self.db.execute("""
                SELECT COUNT(*) FROM rankings
                WHERE score > ?
            """, (score,))

        row = await cursor.fetchone()
        return row[0] + 1

    def _row_to_entry(self, row) -> RankingEntry:
        """DB 행을 엔트리로 변환"""
        return RankingEntry(
            id=row[0],
            profile_id=row[1],
            profile_name=row[2],
            class_id=row[3],
            mode=row[4],
            score=row[5],
            floor=row[6],
            level=row[7],
            monsters_killed=row[8],
            bosses_killed=row[9],
            play_time=row[10],
            victory=bool(row[11]),
            created_at=datetime.fromisoformat(row[12])
        )


async def create_ranking_table(db) -> None:
    """랭킹 테이블 생성"""
    await db.execute("""
        CREATE TABLE IF NOT EXISTS rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id TEXT NOT NULL,
            profile_name TEXT NOT NULL,
            class_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            score INTEGER NOT NULL,
            floor INTEGER NOT NULL,
            level INTEGER NOT NULL,
            monsters_killed INTEGER NOT NULL,
            bosses_killed INTEGER NOT NULL,
            play_time INTEGER NOT NULL,
            victory INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_rankings_score
        ON rankings (score DESC)
    """)
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_rankings_mode_score
        ON rankings (mode, score DESC)
    """)
    await db.commit()
