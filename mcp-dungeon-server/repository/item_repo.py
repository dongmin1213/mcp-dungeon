"""아이템 Repository"""
import json
import random
from typing import Optional
from repository.database import Database
from models.item import Item, ItemType, ItemGrade


class ItemRepository:
    """아이템 데이터 조회"""

    @staticmethod
    async def get_by_id(item_id: str) -> Optional[Item]:
        """ID로 아이템 조회"""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return ItemRepository._row_to_item(dict(row))

    @staticmethod
    async def get_for_floor(floor: int, item_type: str = None) -> list[Item]:
        """해당 층에서 등장하는 아이템 목록"""
        db = await Database.connect()
        query = """
            SELECT * FROM items
            WHERE floor_min <= ? AND floor_max >= ?
        """
        params = [floor, floor]

        if item_type:
            query += " AND type = ?"
            params.append(item_type)

        cursor = await db.execute(query, params)
        return [ItemRepository._row_to_item(dict(row)) for row in await cursor.fetchall()]

    @staticmethod
    async def get_shop_items(floor: int, count: int = 5) -> list[Item]:
        """상점 아이템 (랜덤 선택)"""
        db = await Database.connect()
        # 소비 아이템 2-3개 + 장비 2-3개
        consumables = await ItemRepository.get_for_floor(floor, "consumable")
        equipment_types = ["weapon", "armor", "helmet", "accessory"]

        equipment = []
        for eq_type in equipment_types:
            items = await ItemRepository.get_for_floor(floor, eq_type)
            equipment.extend(items)

        # 랜덤 선택
        shop_items = []

        # 소비 아이템 2-3개
        if consumables:
            sample_count = min(random.randint(2, 3), len(consumables))
            shop_items.extend(random.sample(consumables, sample_count))

        # 장비 2-3개
        if equipment:
            sample_count = min(random.randint(2, 3), len(equipment))
            shop_items.extend(random.sample(equipment, sample_count))

        return shop_items[:count]

    @staticmethod
    async def get_random_by_grade(floor: int, grade: str = None) -> Optional[Item]:
        """등급별 랜덤 아이템"""
        db = await Database.connect()
        query = """
            SELECT * FROM items
            WHERE floor_min <= ? AND floor_max >= ?
            AND type != 'special'
        """
        params = [floor, floor]

        if grade:
            query += " AND grade = ?"
            params.append(grade)

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        if not rows:
            return None

        chosen = random.choice(rows)
        return ItemRepository._row_to_item(dict(chosen))

    @staticmethod
    async def get_treasure_item(floor: int, rare_chance: float = 0.2) -> Optional[Item]:
        """보물 상자 아이템"""
        # 희귀 확률 판정
        if random.random() < rare_chance:
            grade = random.choice(["rare", "legendary"])
        else:
            grade = random.choice(["common", "uncommon"])

        return await ItemRepository.get_random_by_grade(floor, grade)

    @staticmethod
    async def get_cursed_item(floor: int) -> Optional[Item]:
        """v5.0 저주받은 아이템 랜덤 획득"""
        db = await Database.connect()
        cursor = await db.execute("""
            SELECT * FROM items
            WHERE grade = 'cursed'
            AND floor_min <= ? AND floor_max >= ?
        """, (floor, floor))
        rows = await cursor.fetchall()
        if not rows:
            return None
        return ItemRepository._row_to_item(dict(random.choice(rows)))

    @staticmethod
    def _row_to_item(row: dict) -> Item:
        """DB row -> Item 객체"""
        effect = json.loads(row.get("effect") or "null")
        curse = json.loads(row.get("curse") or "null")

        return Item(
            id=row["id"],
            name=row["name"],
            type=ItemType(row["type"]),
            grade=ItemGrade(row["grade"]),
            description=row["description"],
            price=row["price"],
            stat_atk=row.get("stat_atk", 0),
            stat_def=row.get("stat_def", 0),
            stat_hp=row.get("stat_hp", 0),
            stat_mp=row.get("stat_mp", 0),
            effect=effect,
            curse=curse,
        )
