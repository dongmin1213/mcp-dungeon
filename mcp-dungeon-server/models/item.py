"""아이템 모델"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ItemType(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    HELMET = "helmet"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    SPECIAL = "special"


class ItemGrade(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"
    CURSED = "cursed"  # v5.0 저주받은 아이템


# 등급별 아이콘
GRADE_ICONS = {
    ItemGrade.COMMON: "⚪",
    ItemGrade.UNCOMMON: "🟢",
    ItemGrade.RARE: "🔵",
    ItemGrade.LEGENDARY: "🟣",
    ItemGrade.CURSED: "💀",  # v5.0
}


class Item(BaseModel):
    """아이템"""
    id: str
    name: str
    type: ItemType
    grade: ItemGrade
    description: str
    price: int

    stat_atk: int = 0
    stat_def: int = 0
    stat_hp: int = 0
    stat_mp: int = 0

    effect: Optional[dict] = None  # 특수 효과 (JSON)
    curse: Optional[dict] = None  # v5.0 저주 효과 (JSON)

    @property
    def grade_icon(self) -> str:
        """등급 아이콘"""
        return GRADE_ICONS.get(self.grade, "⚪")

    @property
    def sell_price(self) -> int:
        """판매 가격 (구매가의 40%)"""
        return int(self.price * 0.4)

    @property
    def is_equipment(self) -> bool:
        """장비 아이템 여부"""
        return self.type in [
            ItemType.WEAPON,
            ItemType.ARMOR,
            ItemType.HELMET,
            ItemType.ACCESSORY,
        ]

    @property
    def is_consumable(self) -> bool:
        """소비 아이템 여부"""
        return self.type == ItemType.CONSUMABLE

    @property
    def is_cursed(self) -> bool:
        """v5.0 저주받은 아이템 여부"""
        return self.curse is not None or self.grade == ItemGrade.CURSED

    @classmethod
    def from_db_row(cls, row: dict) -> "Item":
        """DB 행에서 Item 생성"""
        import json
        return cls(
            id=row["id"],
            name=row["name"],
            type=ItemType(row["type"]),
            grade=ItemGrade(row["grade"]),
            description=row["description"],
            price=row["price"],
            stat_atk=row.get("stat_atk", 0) or 0,
            stat_def=row.get("stat_def", 0) or 0,
            stat_hp=row.get("stat_hp", 0) or 0,
            stat_mp=row.get("stat_mp", 0) or 0,
            effect=json.loads(row["effect"]) if row.get("effect") else None,
            curse=json.loads(row["curse"]) if row.get("curse") else None,
        )
