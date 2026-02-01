"""프로필 저장소"""
import json
from typing import Optional
from datetime import datetime
from models.profile import Profile, ProfileStats, ProfileUpgrades


class ProfileRepository:
    """프로필 CRUD 저장소"""

    def __init__(self, db):
        self.db = db

    async def get(self, profile_id: str = "default") -> Optional[Profile]:
        """프로필 조회"""
        cursor = await self.db.execute(
            "SELECT * FROM profiles WHERE id = ?",
            (profile_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None

        return Profile(
            id=row[0],
            name=row[1],
            created_at=datetime.fromisoformat(row[2]),
            last_played=datetime.fromisoformat(row[3]),
            souls=row[4],
            stats=ProfileStats(**json.loads(row[5])),
            upgrades=ProfileUpgrades(**json.loads(row[6])),
            unlocked_classes=json.loads(row[7]),
            unlocked_items=json.loads(row[8]),
            unlocked_modes=json.loads(row[9]),
            completed_achievements=json.loads(row[10]),
        )

    async def save(self, profile: Profile) -> None:
        """프로필 저장 (upsert)"""
        profile.last_played = datetime.now()

        await self.db.execute("""
            INSERT INTO profiles (
                id, name, created_at, last_played, souls,
                stats, upgrades, unlocked_classes, unlocked_items,
                unlocked_modes, completed_achievements
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                last_played = excluded.last_played,
                souls = excluded.souls,
                stats = excluded.stats,
                upgrades = excluded.upgrades,
                unlocked_classes = excluded.unlocked_classes,
                unlocked_items = excluded.unlocked_items,
                unlocked_modes = excluded.unlocked_modes,
                completed_achievements = excluded.completed_achievements
        """, (
            profile.id,
            profile.name,
            profile.created_at.isoformat(),
            profile.last_played.isoformat(),
            profile.souls,
            json.dumps(profile.stats.model_dump()),
            json.dumps(profile.upgrades.model_dump()),
            json.dumps(profile.unlocked_classes),
            json.dumps(profile.unlocked_items),
            json.dumps(profile.unlocked_modes),
            json.dumps(profile.completed_achievements),
        ))
        await self.db.commit()

    async def create_default(self) -> Profile:
        """기본 프로필 생성"""
        profile = Profile()
        await self.save(profile)
        return profile

    async def get_or_create(self, profile_id: str = "default") -> Profile:
        """프로필 조회 또는 생성"""
        profile = await self.get(profile_id)
        if not profile:
            profile = Profile(id=profile_id)
            await self.save(profile)
        return profile

    async def add_souls(self, profile_id: str, amount: int) -> int:
        """소울 추가. 실제 추가된 양 반환"""
        profile = await self.get_or_create(profile_id)
        actual = profile.add_souls(amount)
        await self.save(profile)
        return actual

    async def spend_souls(self, profile_id: str, amount: int) -> bool:
        """소울 소비. 성공 여부 반환"""
        profile = await self.get_or_create(profile_id)
        if profile.spend_souls(amount):
            await self.save(profile)
            return True
        return False

    async def record_run(
        self,
        profile_id: str,
        victory: bool,
        floor: int,
        level: int,
        monsters_killed: int,
        bosses_killed: int,
        gold_earned: int,
        souls_earned: int,
        play_time: int
    ) -> Profile:
        """런 결과 기록"""
        profile = await self.get_or_create(profile_id)
        profile.stats.record_run(
            victory=victory,
            floor=floor,
            level=level,
            monsters_killed=monsters_killed,
            bosses_killed=bosses_killed,
            gold_earned=gold_earned,
            souls_earned=souls_earned,
            play_time=play_time
        )
        profile.add_souls(souls_earned)
        await self.save(profile)
        return profile


async def create_profile_table(db) -> None:
    """프로필 테이블 생성"""
    await db.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_played TEXT NOT NULL,
            souls INTEGER DEFAULT 0,
            stats TEXT NOT NULL,
            upgrades TEXT NOT NULL,
            unlocked_classes TEXT NOT NULL,
            unlocked_items TEXT NOT NULL,
            unlocked_modes TEXT NOT NULL,
            completed_achievements TEXT NOT NULL
        )
    """)
    await db.commit()
