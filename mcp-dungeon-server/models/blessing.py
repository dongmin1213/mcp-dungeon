"""v5.0 축복 모델"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class BlessingRarity(str, Enum):
    COMMON = "common"       # 일반 (60%)
    UNCOMMON = "uncommon"   # 고급 (25%)
    RARE = "rare"           # 희귀 (12%)
    LEGENDARY = "legendary" # 전설 (3%)


class BlessingCategory(str, Enum):
    ATTACK = "attack"       # 공격
    DEFENSE = "defense"     # 방어
    UTILITY = "utility"     # 유틸리티
    SKILL = "skill"         # 스킬 관련


# 희귀도별 아이콘
RARITY_ICONS = {
    BlessingRarity.COMMON: "⚪",
    BlessingRarity.UNCOMMON: "🟢",
    BlessingRarity.RARE: "🔵",
    BlessingRarity.LEGENDARY: "🟡",
}

# 희귀도별 색상 이름
RARITY_NAMES = {
    BlessingRarity.COMMON: "일반",
    BlessingRarity.UNCOMMON: "고급",
    BlessingRarity.RARE: "희귀",
    BlessingRarity.LEGENDARY: "전설",
}


class Blessing(BaseModel):
    """축복 모델"""
    id: str
    name: str
    description: str
    category: BlessingCategory
    rarity: BlessingRarity
    effect: dict  # 효과 정의

    @property
    def icon(self) -> str:
        """희귀도 아이콘"""
        return RARITY_ICONS.get(self.rarity, "⚪")

    @property
    def rarity_name(self) -> str:
        """희귀도 이름"""
        return RARITY_NAMES.get(self.rarity, "일반")

    def get_display(self) -> str:
        """표시용 문자열"""
        return f"{self.icon} {self.name} ({self.rarity_name})"


class PlayerBlessings(BaseModel):
    """플레이어가 보유한 축복들"""
    blessings: list[Blessing] = []

    def add(self, blessing: Blessing) -> None:
        """축복 추가"""
        self.blessings.append(blessing)

    def get_stat_bonuses(self) -> dict:
        """모든 축복의 스탯 보너스 합산"""
        bonuses = {
            "atk": 0,
            "def": 0,
            "max_hp": 0,
            "max_mp": 0,
            "crit_chance": 0,
            "damage_mult": 1.0,
            "lifesteal": 0,
            "gold_mult": 1.0,
            "exp_mult": 1.0,
            "double_hit": 0,
            "execute_threshold": 0,
            "thorns": 0,
        }

        for blessing in self.blessings:
            effect = blessing.effect
            for key in bonuses:
                if key in effect:
                    if key.endswith("_mult"):
                        # 배율은 곱셈
                        bonuses[key] *= effect[key]
                    else:
                        # 나머지는 덧셈
                        bonuses[key] += effect[key]

        return bonuses

    def get_display(self) -> str:
        """보유 축복 표시"""
        if not self.blessings:
            return "없음"

        return ", ".join([b.name for b in self.blessings])

    def count_by_rarity(self) -> dict[str, int]:
        """희귀도별 개수"""
        counts = {r.value: 0 for r in BlessingRarity}
        for blessing in self.blessings:
            counts[blessing.rarity.value] += 1
        return counts
