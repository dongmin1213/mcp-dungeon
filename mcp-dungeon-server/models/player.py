"""플레이어 모델"""
from pydantic import BaseModel, Field
from typing import Optional, Any

# v6.6: 직업 데이터는 seeds/classes.py에서 import (Single Source of Truth)
from seeds.classes import CLASS_STATS, CLASS_NAMES

# v6.6: 게임 설정은 config.py에서 import (중복 제거)
from config import GameConfig


class Player(BaseModel):
    """플레이어 캐릭터"""
    name: str
    class_type: str
    level: int = 1
    exp: int = 0

    hp: int
    max_hp: int
    mp: int
    max_mp: int
    atk: int
    def_: int  # 'def'는 예약어

    gold: int = 0
    inventory: list[str] = Field(default_factory=list)  # item_ids
    equipment: dict[str, Optional[str]] = Field(default_factory=lambda: {
        "weapon": None,
        "armor": None,
        "helmet": None,
        "accessory1": None,
        "accessory2": None,
    })
    skills: list[str] = Field(default_factory=list)  # skill_ids

    # v5.0 축복 시스템
    blessings: list[Any] = Field(default_factory=list)  # Blessing objects

    crit_chance: float = 0.15

    @classmethod
    def create(cls, name: str, class_type: str, upgrades: dict | None = None) -> "Player":
        """새 플레이어 생성"""
        if class_type not in CLASS_STATS:
            raise ValueError(f"존재하지 않는 직업: {class_type}")

        upgrades = upgrades or {}
        base = CLASS_STATS[class_type]

        # 영구 업그레이드 적용
        hp_bonus = upgrades.get("hp", 0) * 5
        atk_bonus = upgrades.get("atk", 0) * 2
        def_bonus = upgrades.get("def", 0) * 1

        return cls(
            name=name,
            class_type=class_type,
            hp=base["hp"] + hp_bonus,
            max_hp=base["hp"] + hp_bonus,
            mp=base["mp"],
            max_mp=base["mp"],
            atk=base["atk"] + atk_bonus,
            def_=base["def_"] + def_bonus,
        )

    @property
    def class_name(self) -> str:
        """직업 한글명"""
        return CLASS_NAMES.get(self.class_type, "???")

    @property
    def exp_to_next(self) -> int:
        """다음 레벨까지 필요 경험치"""
        return self.level * GameConfig.EXP_PER_LEVEL

    @property
    def is_alive(self) -> bool:
        """생존 여부"""
        return self.hp > 0

    def take_damage(self, damage: int) -> int:
        """데미지를 받음. 실제 받은 데미지 반환"""
        actual_damage = max(GameConfig.MIN_DAMAGE, damage)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def heal(self, amount: int) -> int:
        """HP 회복. 실제 회복량 반환"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def heal_mp(self, amount: int) -> int:
        """MP 회복. 실제 회복량 반환"""
        old_mp = self.mp
        self.mp = min(self.max_mp, self.mp + amount)
        return self.mp - old_mp

    def add_exp(self, amount: int) -> list[dict]:
        """
        경험치 추가. 레벨업 정보 반환

        Returns:
            [{"level": int, "new_skills": list[str]}]
        """
        self.exp += amount
        leveled_up = []

        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            level_info = self._level_up()
            leveled_up.append(level_info)

        return leveled_up

    def _level_up(self) -> dict:
        """레벨업 처리. 레벨업 정보 반환"""
        self.level += 1
        self.max_hp += GameConfig.LEVEL_UP_HP
        self.max_mp += GameConfig.LEVEL_UP_MP
        self.atk += GameConfig.LEVEL_UP_ATK
        self.def_ += GameConfig.LEVEL_UP_DEF

        # 전체 회복
        self.hp = self.max_hp
        self.mp = self.max_mp

        return {
            "level": self.level,
            "new_skills": []  # 나중에 스킬 시스템에서 채움
        }

    def use_mp(self, amount: int) -> bool:
        """MP 사용. 성공 여부 반환"""
        if self.mp < amount:
            return False
        self.mp -= amount
        return True

    def add_gold(self, amount: int) -> int:
        """골드 추가. 최종 골드 반환"""
        self.gold = min(GameConfig.MAX_GOLD, self.gold + amount)
        return self.gold

    def spend_gold(self, amount: int) -> bool:
        """골드 사용. 성공 여부 반환"""
        if self.gold < amount:
            return False
        self.gold -= amount
        return True

    def can_add_item(self) -> bool:
        """인벤토리에 아이템 추가 가능 여부"""
        return len(self.inventory) < GameConfig.MAX_INVENTORY_SIZE

    def add_item(self, item_id: str) -> bool:
        """아이템 추가. 성공 여부 반환"""
        if not self.can_add_item():
            return False
        self.inventory.append(item_id)
        return True

    def remove_item(self, item_id: str) -> bool:
        """아이템 제거. 성공 여부 반환"""
        if item_id not in self.inventory:
            return False
        self.inventory.remove(item_id)
        return True
