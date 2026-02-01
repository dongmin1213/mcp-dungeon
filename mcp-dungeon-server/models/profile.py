"""플레이어 프로필 모델 (영구 저장)"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProfileStats(BaseModel):
    """플레이 통계"""
    total_runs: int = 0              # 총 플레이 횟수
    total_victories: int = 0         # 클리어 횟수
    total_deaths: int = 0            # 사망 횟수
    total_monsters_killed: int = 0   # 처치한 몬스터 수
    total_bosses_killed: int = 0     # 처치한 보스 수
    total_gold_earned: int = 0       # 획득한 총 골드
    total_souls_earned: int = 0      # 획득한 총 소울
    highest_floor: int = 0           # 최고 도달 층
    highest_level: int = 0           # 최고 레벨
    fastest_clear_time: Optional[int] = None  # 최단 클리어 시간 (초)
    total_play_time: int = 0         # 총 플레이 시간 (초)

    def record_run(
        self,
        victory: bool,
        floor: int,
        level: int,
        monsters_killed: int,
        bosses_killed: int,
        gold_earned: int,
        souls_earned: int,
        play_time: int
    ) -> None:
        """런 결과 기록"""
        self.total_runs += 1
        if victory:
            self.total_victories += 1
            if self.fastest_clear_time is None or play_time < self.fastest_clear_time:
                self.fastest_clear_time = play_time
        else:
            self.total_deaths += 1

        self.total_monsters_killed += monsters_killed
        self.total_bosses_killed += bosses_killed
        self.total_gold_earned += gold_earned
        self.total_souls_earned += souls_earned
        self.total_play_time += play_time

        if floor > self.highest_floor:
            self.highest_floor = floor
        if level > self.highest_level:
            self.highest_level = level


class ProfileUpgrades(BaseModel):
    """영구 업그레이드 상태"""
    max_hp_bonus: int = 0        # 최대 HP 보너스 (레벨당 +5)
    max_mp_bonus: int = 0        # 최대 MP 보너스 (레벨당 +3)
    atk_bonus: int = 0           # 공격력 보너스 (레벨당 +1)
    def_bonus: int = 0           # 방어력 보너스 (레벨당 +1)
    crit_bonus: int = 0          # 크리티컬 확률 보너스 (레벨당 +1%)
    gold_bonus: int = 0          # 골드 획득 보너스 (레벨당 +5%)
    exp_bonus: int = 0           # 경험치 획득 보너스 (레벨당 +5%)
    potion_effect: int = 0       # 포션 효과 보너스 (레벨당 +10%)
    starting_gold: int = 0       # 시작 골드 (레벨당 +20)
    soul_bonus: int = 0          # 소울 획득 보너스 (레벨당 +5%)


class Profile(BaseModel):
    """플레이어 프로필"""
    id: str = "default"
    name: str = "모험가"
    created_at: datetime = Field(default_factory=datetime.now)
    last_played: datetime = Field(default_factory=datetime.now)

    # 소울 (메타 화폐)
    souls: int = 0

    # 통계
    stats: ProfileStats = Field(default_factory=ProfileStats)

    # 영구 업그레이드
    upgrades: ProfileUpgrades = Field(default_factory=ProfileUpgrades)

    # 언락 상태
    unlocked_classes: list[str] = Field(default_factory=lambda: ["warrior"])
    unlocked_items: list[str] = Field(default_factory=list)
    unlocked_modes: list[str] = Field(default_factory=lambda: ["normal"])

    # 업적
    completed_achievements: list[str] = Field(default_factory=list)

    def add_souls(self, amount: int) -> int:
        """소울 추가. 추가된 양 반환"""
        # 소울 보너스 적용
        bonus_mult = 1 + (self.upgrades.soul_bonus * 0.05)
        actual_amount = int(amount * bonus_mult)
        self.souls += actual_amount
        return actual_amount

    def spend_souls(self, amount: int) -> bool:
        """소울 소비. 성공 여부 반환"""
        if self.souls >= amount:
            self.souls -= amount
            return True
        return False

    def unlock_class(self, class_id: str) -> bool:
        """직업 언락. 성공 여부 반환"""
        if class_id not in self.unlocked_classes:
            self.unlocked_classes.append(class_id)
            return True
        return False

    def unlock_item(self, item_id: str) -> bool:
        """아이템 언락. 성공 여부 반환"""
        if item_id not in self.unlocked_items:
            self.unlocked_items.append(item_id)
            return True
        return False

    def unlock_mode(self, mode_id: str) -> bool:
        """모드 언락. 성공 여부 반환"""
        if mode_id not in self.unlocked_modes:
            self.unlocked_modes.append(mode_id)
            return True
        return False

    def complete_achievement(self, achievement_id: str) -> bool:
        """업적 완료. 성공 여부 반환"""
        if achievement_id not in self.completed_achievements:
            self.completed_achievements.append(achievement_id)
            return True
        return False

    def get_starting_bonuses(self) -> dict:
        """게임 시작 시 적용할 보너스"""
        return {
            "hp": self.upgrades.max_hp_bonus * 5,
            "mp": self.upgrades.max_mp_bonus * 3,
            "atk": self.upgrades.atk_bonus,
            "def_": self.upgrades.def_bonus,
            "crit_chance": self.upgrades.crit_bonus * 0.01,
            "gold": self.upgrades.starting_gold * 20,
            "gold_mult": 1 + (self.upgrades.gold_bonus * 0.05),
            "exp_mult": 1 + (self.upgrades.exp_bonus * 0.05),
            "potion_mult": 1 + (self.upgrades.potion_effect * 0.10),
        }
