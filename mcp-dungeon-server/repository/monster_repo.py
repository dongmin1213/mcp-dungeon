"""몬스터 Repository"""
import json
import random
from typing import Optional
from repository.database import Database
from models.monster import Monster, MonsterType


class MonsterRepository:
    """몬스터 데이터 조회"""

    @staticmethod
    async def get_by_id(monster_id: str) -> Optional[Monster]:
        """ID로 몬스터 조회"""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM monsters WHERE id = ?", (monster_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return MonsterRepository._row_to_monster(dict(row))

    @staticmethod
    async def get_for_floor(floor: int, monster_type: str = "normal") -> list[dict]:
        """해당 층에 등장하는 몬스터 목록"""
        db = await Database.connect()
        cursor = await db.execute("""
            SELECT * FROM monsters
            WHERE floor_min <= ? AND floor_max >= ? AND type = ?
        """, (floor, floor, monster_type))
        return [dict(row) for row in await cursor.fetchall()]

    @staticmethod
    async def get_random_for_floor(floor: int, monster_type: str = "normal") -> Optional[Monster]:
        """해당 층의 랜덤 몬스터"""
        monsters = await MonsterRepository.get_for_floor(floor, monster_type)
        if not monsters:
            return None
        chosen = random.choice(monsters)
        return MonsterRepository._row_to_monster(chosen)

    @staticmethod
    async def get_boss_for_floor(floor: int) -> Optional[Monster]:
        """해당 층의 보스"""
        db = await Database.connect()
        cursor = await db.execute("""
            SELECT * FROM monsters
            WHERE floor_min <= ? AND floor_max >= ? AND type = 'boss'
            ORDER BY floor_min DESC
            LIMIT 1
        """, (floor, floor))
        row = await cursor.fetchone()
        if not row:
            return None
        return MonsterRepository._row_to_monster(dict(row))

    @staticmethod
    async def get_elite_for_floor(floor: int) -> Optional[Monster]:
        """해당 층의 엘리트 (랜덤)"""
        return await MonsterRepository.get_random_for_floor(floor, "elite")

    @staticmethod
    async def get_drops(monster_id: str) -> list[dict]:
        """몬스터 드롭 아이템 목록"""
        db = await Database.connect()
        cursor = await db.execute("""
            SELECT md.item_id, md.drop_chance, md.min_quantity, md.max_quantity,
                   i.name as item_name, i.grade as item_grade
            FROM monster_drops md
            JOIN items i ON md.item_id = i.id
            WHERE md.monster_id = ?
        """, (monster_id,))
        return [dict(row) for row in await cursor.fetchall()]

    @staticmethod
    async def roll_drops(monster_id: str, luck_bonus: float = 0.0) -> list[dict]:
        """드롭 판정 (행운 보정 적용)"""
        drops = await MonsterRepository.get_drops(monster_id)
        result = []

        for drop in drops:
            # 행운 보정
            adjusted_chance = min(1.0, drop["drop_chance"] * (1 + luck_bonus))
            if random.random() < adjusted_chance:
                quantity = random.randint(
                    drop.get("min_quantity", 1),
                    drop.get("max_quantity", 1)
                )
                result.append({
                    "item_id": drop["item_id"],
                    "item_name": drop["item_name"],
                    "quantity": quantity,
                })

        return result

    @staticmethod
    def _row_to_monster(row: dict) -> Monster:
        """DB row -> Monster 객체"""
        m_type = MonsterType(row["type"])
        skills = json.loads(row.get("skills") or "[]")
        pattern = json.loads(row.get("pattern") or "null")

        return Monster(
            id=row["id"],
            name=row["name"],
            type=m_type,
            hp=row["hp"],
            max_hp=row["hp"],
            atk=row["atk"],
            def_=row["def"],
            exp=row["exp"],
            gold_min=row["gold_min"],
            gold_max=row["gold_max"],
            souls=row["souls"],
            skills=skills,
            pattern=pattern,
        )
