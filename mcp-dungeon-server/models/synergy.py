"""v5.0 시너지 모델 (Phase 1A 확장)"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class SynergyType(str, Enum):
    """시너지 타입"""
    SET = "set"  # 세트 효과 (특정 아이템 조합)
    ELEMENT = "element"  # 속성 시너지
    CATEGORY = "category"  # 카테고리 시너지 (같은 종류 아이템)


class Synergy(BaseModel):
    """시너지 정의"""
    id: str
    name: str
    description: str
    type: SynergyType

    # 필요 조건
    required_items: list[str] = []  # 필요 아이템 ID
    required_count: int = 2  # 필요 개수
    required_category: Optional[str] = None  # 카테고리 (fire, poison, etc.)

    # 효과
    effect: dict = {}  # {"atk": 5, "damage_mult": 1.2, ...}

    # 발견 여부
    hidden: bool = True  # 숨겨진 시너지 여부

    @property
    def effect_text(self) -> str:
        """효과 텍스트"""
        parts = []

        # 기본 스탯
        if "atk" in self.effect:
            parts.append(f"ATK +{self.effect['atk']}")
        if "def" in self.effect:
            parts.append(f"DEF +{self.effect['def']}")
        if "max_hp" in self.effect:
            parts.append(f"최대 HP +{self.effect['max_hp']}")
        if "max_mp" in self.effect:
            parts.append(f"최대 MP +{self.effect['max_mp']}")
        if "all_stats" in self.effect:
            parts.append(f"모든 스탯 +{self.effect['all_stats']}")

        # 데미지 배율
        if "damage_mult" in self.effect:
            bonus = int((self.effect['damage_mult'] - 1) * 100)
            parts.append(f"데미지 +{bonus}%")
        if "skill_damage_mult" in self.effect:
            bonus = int((self.effect['skill_damage_mult'] - 1) * 100)
            parts.append(f"스킬 데미지 +{bonus}%")

        # 속성 데미지
        if "fire_damage_mult" in self.effect:
            bonus = int((self.effect['fire_damage_mult'] - 1) * 100)
            parts.append(f"화염 데미지 +{bonus}%")
        if "ice_damage_mult" in self.effect:
            bonus = int((self.effect['ice_damage_mult'] - 1) * 100)
            parts.append(f"냉기 데미지 +{bonus}%")
        if "poison_damage_mult" in self.effect:
            bonus = int((self.effect['poison_damage_mult'] - 1) * 100)
            parts.append(f"독 데미지 +{bonus}%")
        if "element_damage_mult" in self.effect:
            bonus = int((self.effect['element_damage_mult'] - 1) * 100)
            parts.append(f"속성 데미지 +{bonus}%")

        # 고정 속성 데미지
        if "void_damage" in self.effect:
            parts.append(f"공허 데미지 +{self.effect['void_damage']}")
        if "aura_damage" in self.effect:
            parts.append(f"오라 데미지 {self.effect['aura_damage']}/턴")

        # 흡혈
        if "lifesteal" in self.effect:
            parts.append(f"흡혈 +{int(self.effect['lifesteal'] * 100)}%")
        if "lifesteal_on_low_hp" in self.effect:
            parts.append(f"저HP 시 흡혈 {self.effect['lifesteal_on_low_hp']}배")
        if "lifesteal_on_reflect" in self.effect:
            parts.append("반사 데미지 흡혈")

        # 크리티컬
        if "crit_bonus" in self.effect:
            parts.append(f"크리티컬 +{int(self.effect['crit_bonus'] * 100)}%")

        # 골드/드롭
        if "gold_mult" in self.effect:
            bonus = int((self.effect['gold_mult'] - 1) * 100)
            parts.append(f"골드 +{bonus}%")
        if "drop_mult" in self.effect:
            bonus = int((self.effect['drop_mult'] - 1) * 100)
            parts.append(f"드롭률 +{bonus}%")
        if "exp_mult" in self.effect:
            bonus = int((self.effect['exp_mult'] - 1) * 100)
            parts.append(f"경험치 +{bonus}%")
        if "soul_mult" in self.effect:
            bonus = int((self.effect['soul_mult'] - 1) * 100)
            parts.append(f"소울 +{bonus}%")

        # 방어/감소
        if "damage_reduction" in self.effect:
            parts.append(f"피해 감소 {int(self.effect['damage_reduction'] * 100)}%")
        if "magic_resist" in self.effect:
            parts.append(f"마법 저항 {int(self.effect['magic_resist'] * 100)}%")

        # 반사/반격
        if "reflect_damage" in self.effect:
            parts.append(f"반사 데미지 {int(self.effect['reflect_damage'] * 100)}%")
        if "reflect_magic" in self.effect:
            parts.append(f"마법 반사 {int(self.effect['reflect_magic'] * 100)}%")
        if "counter_chance" in self.effect:
            parts.append(f"반격 확률 {int(self.effect['counter_chance'] * 100)}%")

        # 면역
        if self.effect.get("fire_immunity"):
            parts.append("🔥 화염 면역")
        if self.effect.get("void_immunity"):
            parts.append("🌀 공허 면역")
        if self.effect.get("element_immunity"):
            parts.append("✨ 속성 면역")
        if self.effect.get("curse_immunity"):
            parts.append("💀 저주 면역")

        # 특수 효과
        if self.effect.get("ignore_fire_resist"):
            parts.append("적 화염 저항 무시")
        if self.effect.get("execute_threshold"):
            threshold = int(self.effect['execute_threshold'] * 100)
            parts.append(f"HP {threshold}% 이하 즉사")
        if self.effect.get("first_strike_mult"):
            mult = self.effect['first_strike_mult']
            parts.append(f"첫 공격 {mult}배")
        if self.effect.get("stealth"):
            parts.append("🥷 은신")
        if self.effect.get("taunt"):
            parts.append("🛡️ 도발")
        if self.effect.get("curse_to_blessing"):
            parts.append("⚡ 저주→축복 변환!")

        # MP 관련
        if "mp_regen" in self.effect:
            parts.append(f"MP 회복 +{self.effect['mp_regen']}/턴")
        if "mp_cost_reduction" in self.effect:
            parts.append(f"MP 소모 -{int(self.effect['mp_cost_reduction'] * 100)}%")

        # 회복
        if "heal_bonus" in self.effect:
            parts.append(f"회복량 +{int(self.effect['heal_bonus'] * 100)}%")

        # 상태이상
        if "burn_chance" in self.effect:
            parts.append(f"화상 확률 {int(self.effect['burn_chance'] * 100)}%")
        if "freeze_chance" in self.effect:
            parts.append(f"빙결 확률 {int(self.effect['freeze_chance'] * 100)}%")
        if "poison_stack" in self.effect:
            parts.append(f"독 중첩 {self.effect['poison_stack']}회")

        return ", ".join(parts) if parts else "???"

    @property
    def is_powerful(self) -> bool:
        """강력한 시너지인지 (사기 빌드 여부)"""
        powerful_effects = [
            "curse_immunity", "curse_to_blessing", "execute_threshold",
            "lifesteal_on_reflect", "element_immunity", "void_immunity",
            "first_strike_mult", "stealth"
        ]
        return any(self.effect.get(e) for e in powerful_effects)


class PlayerSynergies:
    """플레이어 활성 시너지 관리"""

    def __init__(self):
        self.active: list[Synergy] = []  # 활성화된 시너지
        self.discovered: set[str] = set()  # 발견한 시너지 ID

    def add(self, synergy: Synergy) -> None:
        if synergy not in self.active:
            self.active.append(synergy)
            self.discovered.add(synergy.id)

    def remove(self, synergy_id: str) -> None:
        self.active = [s for s in self.active if s.id != synergy_id]

    def has(self, synergy_id: str) -> bool:
        return any(s.id == synergy_id for s in self.active)

    def has_effect(self, effect_name: str) -> bool:
        """특정 효과가 있는지 확인"""
        return any(effect_name in s.effect for s in self.active)

    def get_effect(self, effect_name: str) -> any:
        """특정 효과 값 반환 (첫 번째 발견된 것)"""
        for synergy in self.active:
            if effect_name in synergy.effect:
                return synergy.effect[effect_name]
        return None

    def get_total_effect(self, effect_name: str) -> float:
        """모든 활성 시너지의 특정 효과 합산"""
        total = 0
        for synergy in self.active:
            if effect_name in synergy.effect:
                value = synergy.effect[effect_name]
                if effect_name.endswith("_mult"):
                    # 배율은 곱셈
                    total = total * value if total else value
                else:
                    total += value
        return total

    def get_damage_mult(self) -> float:
        """총 데미지 배율"""
        mult = 1.0
        for synergy in self.active:
            if "damage_mult" in synergy.effect:
                mult *= synergy.effect["damage_mult"]
        return mult

    def get_lifesteal(self, hp_ratio: float = 1.0) -> float:
        """총 흡혈률 (HP 비율 고려)"""
        total = 0.0
        for synergy in self.active:
            if "lifesteal" in synergy.effect:
                base = synergy.effect["lifesteal"]
                # 저HP 시 흡혈 배율 적용
                threshold = synergy.effect.get("lifesteal_threshold", 0)
                multiplier = synergy.effect.get("lifesteal_on_low_hp", 1.0)
                if threshold > 0 and hp_ratio <= threshold:
                    base *= multiplier
                total += base
        return total

    def has_curse_immunity(self) -> bool:
        """저주 면역 여부"""
        return any(s.effect.get("curse_immunity") for s in self.active)

    def has_curse_to_blessing(self) -> bool:
        """저주→축복 변환 여부"""
        return any(s.effect.get("curse_to_blessing") for s in self.active)

    def get_execute_threshold(self) -> float:
        """즉사 임계값 (0이면 없음)"""
        for synergy in self.active:
            if "execute_threshold" in synergy.effect:
                return synergy.effect["execute_threshold"]
        return 0.0

    def get_counter_chance(self) -> float:
        """반격 확률"""
        total = 0.0
        for synergy in self.active:
            if "counter_chance" in synergy.effect:
                total += synergy.effect["counter_chance"]
        return min(1.0, total)

    def get_reflect_damage(self) -> float:
        """반사 데미지 비율"""
        total = 0.0
        for synergy in self.active:
            if "reflect_damage" in synergy.effect:
                total += synergy.effect["reflect_damage"]
        return total

    def has_lifesteal_on_reflect(self) -> bool:
        """반사 데미지 흡혈 여부"""
        return any(s.effect.get("lifesteal_on_reflect") for s in self.active)

    def get_first_strike_mult(self) -> float:
        """첫 공격 배율"""
        for synergy in self.active:
            if "first_strike_mult" in synergy.effect:
                return synergy.effect["first_strike_mult"]
        return 1.0

    def has_stealth(self) -> bool:
        """은신 여부"""
        return any(s.effect.get("stealth") for s in self.active)
