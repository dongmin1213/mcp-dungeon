"""상태 이상 모델"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class StatusType(str, Enum):
    """상태 이상 종류"""
    # 디버프 (피해)
    POISON = "poison"       # 독: 매턴 고정 데미지
    BURN = "burn"           # 화상: 매턴 고정 데미지
    FREEZE = "freeze"       # 빙결: 행동 불가
    STUN = "stun"           # 기절: 행동 불가

    # 디버프 (스탯)
    DEF_DOWN = "def_down"   # 방어력 감소
    ATK_DOWN = "atk_down"   # 공격력 감소

    # 버프 (스탯)
    ATK_UP = "atk_up"       # 공격력 증가
    DEF_UP = "def_up"       # 방어력 증가
    EVASION = "evasion"     # 회피율 증가
    DAMAGE_REDUCTION = "damage_reduction"  # 데미지 감소

    # 특수 버프
    MANA_SHIELD = "mana_shield"     # 마나 실드
    REFLECT = "reflect"             # 데미지 반사
    NEXT_CRIT = "next_crit"         # 다음 공격 크리티컬
    CRIT_BONUS = "crit_bonus"       # 크리티컬 확률 증가

    # 특수 디버프
    DEATH_MARK = "death_mark"       # 죽음의 표식


class StatusEffect(BaseModel):
    """상태 이상 효과"""
    type: StatusType
    duration: int           # 남은 턴 수
    value: float = 0        # 효과 값 (데미지, 배율 등)
    source: str = ""        # 효과 발생 원인 (스킬명)

    @property
    def is_debuff(self) -> bool:
        """디버프 여부"""
        return self.type in [
            StatusType.POISON, StatusType.BURN, StatusType.FREEZE,
            StatusType.STUN, StatusType.DEF_DOWN, StatusType.ATK_DOWN,
            StatusType.DEATH_MARK
        ]

    @property
    def is_cc(self) -> bool:
        """행동 불가 여부"""
        return self.type in [StatusType.FREEZE, StatusType.STUN]

    @property
    def is_dot(self) -> bool:
        """도트 데미지 여부"""
        return self.type in [StatusType.POISON, StatusType.BURN]

    def tick(self) -> int:
        """턴 경과. 도트 데미지 반환"""
        damage = 0
        if self.is_dot:
            damage = int(self.value)
        self.duration -= 1
        return damage

    @property
    def is_expired(self) -> bool:
        """만료 여부"""
        return self.duration <= 0

    def get_icon(self) -> str:
        """상태 아이콘"""
        icons = {
            StatusType.POISON: "🟢",
            StatusType.BURN: "🔥",
            StatusType.FREEZE: "🧊",
            StatusType.STUN: "💫",
            StatusType.DEF_DOWN: "🔽",
            StatusType.ATK_DOWN: "⬇️",
            StatusType.ATK_UP: "⬆️",
            StatusType.DEF_UP: "🔼",
            StatusType.EVASION: "💨",
            StatusType.DAMAGE_REDUCTION: "🛡️",
            StatusType.MANA_SHIELD: "🔮",
            StatusType.REFLECT: "🪞",
            StatusType.NEXT_CRIT: "💥",
            StatusType.CRIT_BONUS: "🎯",
            StatusType.DEATH_MARK: "💀",
        }
        return icons.get(self.type, "❓")

    def get_name(self) -> str:
        """상태 이름"""
        names = {
            StatusType.POISON: "독",
            StatusType.BURN: "화상",
            StatusType.FREEZE: "빙결",
            StatusType.STUN: "기절",
            StatusType.DEF_DOWN: "방어력 감소",
            StatusType.ATK_DOWN: "공격력 감소",
            StatusType.ATK_UP: "공격력 증가",
            StatusType.DEF_UP: "방어력 증가",
            StatusType.EVASION: "회피",
            StatusType.DAMAGE_REDUCTION: "데미지 감소",
            StatusType.MANA_SHIELD: "마나 실드",
            StatusType.REFLECT: "반사",
            StatusType.NEXT_CRIT: "확정 크리티컬",
            StatusType.CRIT_BONUS: "크리티컬 증가",
            StatusType.DEATH_MARK: "죽음의 표식",
        }
        return names.get(self.type, "알 수 없음")


class StatusManager:
    """상태 이상 관리자"""

    def __init__(self):
        self.effects: list[StatusEffect] = []

    def add_effect(self, effect: StatusEffect) -> bool:
        """상태 이상 추가. 같은 타입이면 갱신"""
        # 같은 타입 효과 찾기
        for existing in self.effects:
            if existing.type == effect.type:
                # 더 긴 지속시간으로 갱신
                if effect.duration > existing.duration:
                    existing.duration = effect.duration
                # 더 강한 효과로 갱신
                if effect.value > existing.value:
                    existing.value = effect.value
                return False  # 갱신됨

        self.effects.append(effect)
        return True  # 새로 추가됨

    def remove_effect(self, effect_type: StatusType) -> bool:
        """상태 이상 제거"""
        for i, effect in enumerate(self.effects):
            if effect.type == effect_type:
                self.effects.pop(i)
                return True
        return False

    def has_effect(self, effect_type: StatusType) -> bool:
        """특정 상태 이상 보유 여부"""
        return any(e.type == effect_type for e in self.effects)

    def get_effect(self, effect_type: StatusType) -> Optional[StatusEffect]:
        """특정 상태 이상 가져오기"""
        for effect in self.effects:
            if effect.type == effect_type:
                return effect
        return None

    def is_cc(self) -> bool:
        """행동 불가 상태인지"""
        return any(e.is_cc for e in self.effects)

    def process_turn_start(self) -> dict:
        """
        턴 시작 시 처리

        Returns:
            {
                "dot_damage": int,  # 도트 데미지 총합
                "messages": list[str],  # 메시지들
                "can_act": bool,  # 행동 가능 여부
            }
        """
        result = {
            "dot_damage": 0,
            "messages": [],
            "can_act": True,
        }

        expired = []

        for effect in self.effects:
            # 도트 데미지
            if effect.is_dot:
                damage = effect.tick()
                result["dot_damage"] += damage
                result["messages"].append(
                    f"{effect.get_icon()} {effect.get_name()}으로 {damage} 데미지!"
                )

            # CC 효과
            if effect.is_cc:
                result["can_act"] = False
                result["messages"].append(
                    f"{effect.get_icon()} {effect.get_name()} 상태로 행동 불가!"
                )
                effect.duration -= 1

            # 만료 확인
            if effect.is_expired:
                expired.append(effect)

        # 만료된 효과 제거
        for effect in expired:
            self.effects.remove(effect)
            result["messages"].append(
                f"{effect.get_icon()} {effect.get_name()} 효과가 해제되었습니다."
            )

        return result

    def process_turn_end(self) -> list[str]:
        """턴 종료 시 처리 (버프/디버프 지속시간 감소)"""
        messages = []
        expired = []

        for effect in self.effects:
            # 도트/CC가 아닌 효과들 지속시간 감소
            if not effect.is_dot and not effect.is_cc:
                effect.duration -= 1

            if effect.is_expired:
                expired.append(effect)

        for effect in expired:
            self.effects.remove(effect)
            messages.append(
                f"{effect.get_icon()} {effect.get_name()} 효과가 해제되었습니다."
            )

        return messages

    def get_atk_modifier(self) -> float:
        """공격력 배율 (합산)"""
        modifier = 1.0
        for effect in self.effects:
            if effect.type == StatusType.ATK_UP:
                modifier *= (1 + effect.value)
            elif effect.type == StatusType.ATK_DOWN:
                modifier *= effect.value
        return modifier

    def get_def_modifier(self) -> float:
        """방어력 배율 (합산)"""
        modifier = 1.0
        for effect in self.effects:
            if effect.type == StatusType.DEF_UP:
                modifier *= (1 + effect.value)
            elif effect.type == StatusType.DEF_DOWN:
                modifier *= effect.value
        return modifier

    def get_damage_reduction(self) -> float:
        """데미지 감소율"""
        reduction = 0
        for effect in self.effects:
            if effect.type == StatusType.DAMAGE_REDUCTION:
                reduction += effect.value
        return min(0.9, reduction)  # 최대 90%

    def get_evasion_bonus(self) -> float:
        """회피율 보너스"""
        bonus = 0
        for effect in self.effects:
            if effect.type == StatusType.EVASION:
                bonus += effect.value
        return bonus

    def get_crit_bonus(self) -> float:
        """크리티컬 보너스"""
        bonus = 0
        for effect in self.effects:
            if effect.type == StatusType.CRIT_BONUS:
                bonus += effect.value
        return bonus

    def has_guaranteed_crit(self) -> bool:
        """확정 크리티컬 여부"""
        return self.has_effect(StatusType.NEXT_CRIT)

    def consume_guaranteed_crit(self) -> bool:
        """확정 크리티컬 소모"""
        return self.remove_effect(StatusType.NEXT_CRIT)

    def get_mana_shield_ratio(self) -> float:
        """마나 실드 비율"""
        effect = self.get_effect(StatusType.MANA_SHIELD)
        return effect.value if effect else 0

    def get_reflect_ratio(self) -> float:
        """반사 비율"""
        effect = self.get_effect(StatusType.REFLECT)
        return effect.value if effect else 0

    def has_poison(self) -> bool:
        """Phase 3: 독 상태 여부 (암살자의 낙인 듀오용)"""
        return self.has_effect(StatusType.POISON)

    def get_status_display(self) -> str:
        """상태 이상 표시 문자열"""
        if not self.effects:
            return ""

        parts = []
        for effect in self.effects:
            parts.append(f"{effect.get_icon()}{effect.duration}")

        return " ".join(parts)

    def clear(self) -> None:
        """모든 상태 이상 제거"""
        self.effects.clear()

    def clear_debuffs(self) -> int:
        """디버프만 제거. 제거된 개수 반환"""
        count = 0
        self.effects = [e for e in self.effects if not e.is_debuff or not (count := count + 1)]
        return count
