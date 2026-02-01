"""스킬 Repository"""
import json
from typing import Optional
from repository.database import Database


class SkillData:
    """스킬 데이터"""
    def __init__(self, row: dict):
        self.id: str = row["id"]
        self.name: str = row["name"]
        self.description: str = row["description"]
        self.type: str = row["type"]  # attack, buff, debuff, heal
        self.mp_cost: int = row["mp_cost"]
        self.cooldown: int = row["cooldown"]
        self.unlock_level: int = row["unlock_level"]
        self.effect: dict = json.loads(row["effect"]) if row["effect"] else {}
        self.classes: list[str] = json.loads(row["classes"]) if row["classes"] else []
        # v5.0 속성 시스템
        self.element: str | None = row.get("element")

    def get_icon(self) -> str:
        """스킬 타입 아이콘 (v5.0: 속성 아이콘 우선)"""
        # 속성이 있으면 속성 아이콘 사용
        if self.element:
            from systems.element import ELEMENT_ICONS
            return ELEMENT_ICONS.get(self.element, "✨")

        icons = {
            "attack": "⚔️",
            "buff": "⬆️",
            "debuff": "⬇️",
            "heal": "💚",
        }
        return icons.get(self.type, "✨")


class SkillRepository:
    """스킬 데이터 조회"""

    @staticmethod
    async def get_by_id(skill_id: str) -> Optional[SkillData]:
        """ID로 스킬 조회"""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM skills WHERE id = ?",
            (skill_id,)
        )
        row = await cursor.fetchone()
        return SkillData(dict(row)) if row else None

    @staticmethod
    async def get_by_class(class_type: str) -> list[SkillData]:
        """직업별 스킬 목록 (레벨순 정렬)"""
        db = await Database.connect()
        cursor = await db.execute(
            """
            SELECT * FROM skills
            WHERE classes LIKE ?
            ORDER BY unlock_level ASC
            """,
            (f'%"{class_type}"%',)
        )
        rows = await cursor.fetchall()
        return [SkillData(dict(row)) for row in rows]

    @staticmethod
    async def get_unlockable_skills(class_type: str, level: int) -> list[SkillData]:
        """특정 레벨에 해금되는 스킬 목록"""
        db = await Database.connect()
        cursor = await db.execute(
            """
            SELECT * FROM skills
            WHERE classes LIKE ?
            AND unlock_level = ?
            """,
            (f'%"{class_type}"%', level)
        )
        rows = await cursor.fetchall()
        return [SkillData(dict(row)) for row in rows]

    @staticmethod
    async def get_all_class_skills(class_type: str, max_level: int) -> list[SkillData]:
        """특정 레벨까지 해금된 모든 스킬"""
        db = await Database.connect()
        cursor = await db.execute(
            """
            SELECT * FROM skills
            WHERE classes LIKE ?
            AND unlock_level <= ?
            ORDER BY unlock_level ASC
            """,
            (f'%"{class_type}"%', max_level)
        )
        rows = await cursor.fetchall()
        return [SkillData(dict(row)) for row in rows]

    @staticmethod
    async def get_multiple(skill_ids: list[str]) -> list[SkillData]:
        """여러 스킬 한번에 조회"""
        if not skill_ids:
            return []

        db = await Database.connect()
        placeholders = ",".join(["?" for _ in skill_ids])
        cursor = await db.execute(
            f"SELECT * FROM skills WHERE id IN ({placeholders})",
            skill_ids
        )
        rows = await cursor.fetchall()
        return [SkillData(dict(row)) for row in rows]
