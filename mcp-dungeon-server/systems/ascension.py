"""Phase 2: 승천 모드 시스템

승천 모드는 규칙 변경형 난이도 시스템입니다.
단순 숫자 뻥튀기가 아닌, 게임 규칙 자체를 변경합니다.
"""
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class AscensionModifier:
    """승천 효과 정의"""
    id: int
    name: str
    description: str
    modifier_type: str  # "stat", "rule", "spawn"
    effect: dict


# ============================================================
# 승천 단계 정의 (1~10)
# ============================================================
ASCENSION_LEVELS = {
    0: AscensionModifier(
        id=0,
        name="일반",
        description="기본 난이도",
        modifier_type="none",
        effect={}
    ),
    1: AscensionModifier(
        id=1,
        name="승천 1",
        description="엘리트 HP +20%",
        modifier_type="stat",
        effect={"elite_hp_mult": 1.2}
    ),
    2: AscensionModifier(
        id=2,
        name="승천 2",
        description="상점에서 회복 아이템 판매 안 함",
        modifier_type="rule",
        effect={"shop_no_potions": True}
    ),
    3: AscensionModifier(
        id=3,
        name="승천 3",
        description="함정 데미지 x1.5",
        modifier_type="stat",
        effect={"trap_damage_mult": 1.5}
    ),
    4: AscensionModifier(
        id=4,
        name="승천 4",
        description="첫 턴 적이 먼저 공격",
        modifier_type="rule",
        effect={"enemy_first_strike": True}
    ),
    5: AscensionModifier(
        id=5,
        name="승천 5",
        description="축복 선택지 2개로 감소",
        modifier_type="rule",
        effect={"blessing_choices": 2}
    ),
    6: AscensionModifier(
        id=6,
        name="승천 6",
        description="보스 HP +30%",
        modifier_type="stat",
        effect={"boss_hp_mult": 1.3}
    ),
    7: AscensionModifier(
        id=7,
        name="승천 7",
        description="휴식 회복량 -50%",
        modifier_type="stat",
        effect={"rest_heal_mult": 0.5}
    ),
    8: AscensionModifier(
        id=8,
        name="승천 8",
        description="보스 처치 전까지 층에서 도망 불가",
        modifier_type="rule",
        effect={"no_flee_until_boss": True}
    ),
    9: AscensionModifier(
        id=9,
        name="승천 9",
        description="엘리트 스킵 시 저주 아이템 획득",
        modifier_type="rule",
        effect={"elite_skip_curse": True}
    ),
    10: AscensionModifier(
        id=10,
        name="승천 10",
        description="히든 보스 '심연의 군주' 등장 (6층)",
        modifier_type="spawn",
        effect={"hidden_boss": "abyss_lord", "extra_floor": True}
    ),
}


def get_ascension_modifier(level: int) -> AscensionModifier:
    """승천 레벨에 해당하는 효과 반환"""
    return ASCENSION_LEVELS.get(level, ASCENSION_LEVELS[0])


def get_all_active_modifiers(level: int) -> list[AscensionModifier]:
    """
    해당 승천 레벨까지의 모든 활성 효과 반환

    승천 효과는 누적됩니다. 승천 5면 1~5의 효과가 모두 적용됩니다.
    """
    modifiers = []
    for i in range(1, level + 1):
        if i in ASCENSION_LEVELS:
            modifiers.append(ASCENSION_LEVELS[i])
    return modifiers


def get_combined_effects(level: int) -> dict:
    """
    해당 승천 레벨의 모든 효과를 합산한 딕셔너리 반환

    Returns:
        합산된 효과 딕셔너리
    """
    combined = {
        # 스탯 배율 (곱셈)
        "elite_hp_mult": 1.0,
        "boss_hp_mult": 1.0,
        "trap_damage_mult": 1.0,
        "rest_heal_mult": 1.0,

        # 규칙 변경 (불리언)
        "shop_no_potions": False,
        "enemy_first_strike": False,
        "no_flee_until_boss": False,
        "elite_skip_curse": False,

        # 숫자 변경
        "blessing_choices": 3,  # 기본 3개

        # 스폰 변경
        "hidden_boss": None,
        "extra_floor": False,
    }

    for modifier in get_all_active_modifiers(level):
        for key, value in modifier.effect.items():
            if key in combined:
                if isinstance(value, bool):
                    combined[key] = combined[key] or value
                elif isinstance(value, (int, float)) and key.endswith("_mult"):
                    combined[key] *= value
                else:
                    combined[key] = value
            else:
                combined[key] = value

    return combined


class AscensionManager:
    """승천 모드 관리자"""

    def __init__(self, level: int = 0):
        self.level = level
        self.effects = get_combined_effects(level)
        self.boss_killed_this_floor = False

    def get_elite_hp_modifier(self) -> float:
        """엘리트 HP 배율"""
        return self.effects.get("elite_hp_mult", 1.0)

    def get_boss_hp_modifier(self) -> float:
        """보스 HP 배율"""
        return self.effects.get("boss_hp_mult", 1.0)

    def get_trap_damage_modifier(self) -> float:
        """함정 데미지 배율"""
        return self.effects.get("trap_damage_mult", 1.0)

    def get_rest_heal_modifier(self) -> float:
        """휴식 회복 배율"""
        return self.effects.get("rest_heal_mult", 1.0)

    def is_shop_potions_disabled(self) -> bool:
        """상점 포션 판매 비활성화 여부"""
        return self.effects.get("shop_no_potions", False)

    def is_enemy_first_strike(self) -> bool:
        """적 선공 여부"""
        return self.effects.get("enemy_first_strike", False)

    def get_blessing_choices_count(self) -> int:
        """축복 선택지 개수"""
        return self.effects.get("blessing_choices", 3)

    def can_flee(self) -> bool:
        """도망 가능 여부"""
        if self.effects.get("no_flee_until_boss", False):
            return self.boss_killed_this_floor
        return True

    def on_boss_killed(self):
        """보스 처치 시 호출"""
        self.boss_killed_this_floor = True

    def on_floor_change(self):
        """층 이동 시 호출"""
        self.boss_killed_this_floor = False

    def should_give_curse_on_elite_skip(self) -> bool:
        """엘리트 스킵 시 저주 아이템 여부"""
        return self.effects.get("elite_skip_curse", False)

    def has_hidden_boss(self) -> bool:
        """히든 보스 존재 여부"""
        return self.effects.get("hidden_boss") is not None

    def get_hidden_boss_id(self) -> Optional[str]:
        """히든 보스 ID"""
        return self.effects.get("hidden_boss")

    def has_extra_floor(self) -> bool:
        """추가 층 존재 여부 (6층)"""
        return self.effects.get("extra_floor", False)

    def get_max_floor(self) -> int:
        """최대 층 수"""
        return 6 if self.has_extra_floor() else 5


def get_ascension_display(level: int) -> str:
    """승천 레벨 표시용 문자열"""
    if level == 0:
        return "일반"
    return f"승천 {level}"


def get_ascension_description(level: int) -> str:
    """승천 레벨 설명"""
    if level == 0:
        return "기본 난이도입니다."

    lines = [f"승천 {level} 효과:"]
    for modifier in get_all_active_modifiers(level):
        lines.append(f"  • {modifier.description}")
    return "\n".join(lines)


def format_ascension_selection() -> str:
    """승천 선택 UI"""
    lines = [
        "═══════════════════════════════════════════════════",
        "  ⚔️ 승천 모드 선택",
        "═══════════════════════════════════════════════════",
        "",
        "  승천은 누적 효과입니다. 높은 승천 = 더 많은 페널티",
        "",
    ]

    for level, modifier in ASCENSION_LEVELS.items():
        if level == 0:
            lines.append(f"  [{level}] {modifier.name} - {modifier.description}")
        else:
            effect_type = "📊" if modifier.modifier_type == "stat" else "📜"
            lines.append(f"  [{level}] {modifier.name} {effect_type}")
            lines.append(f"      {modifier.description}")

    lines.extend([
        "",
        "───────────────────────────────────────────────────",
        "  📊 = 숫자 변경  📜 = 규칙 변경",
        "═══════════════════════════════════════════════════",
    ])

    return "\n".join(lines)


# ============================================================
# 심연의 군주 (승천 10 히든 보스)
# ============================================================
ABYSS_LORD_DATA = {
    "id": "boss_abyss_lord",
    "name": "심연의 군주",
    "floor_min": 6,
    "floor_max": 6,
    "hp": 600,
    "atk": 75,
    "def": 15,
    "exp": 1000,
    "gold_min": 800,
    "gold_max": 1200,
    "souls": 300,
    "action_pattern": ["buff", "attack", "special", "attack", "charge", "heavy", "debuff", "heal", "special"],
    "element": "dark",
    "weaknesses": ["holy"],
    "resistances": ["physical", "fire", "ice", "dark", "poison"],
    "immunities": [],
    "skills": ["void_nova", "reality_tear", "soul_devour", "abyssal_summon", "final_darkness"],
    "pattern": {
        "phase1": {"hp_percent": 80, "action": "abyssal_summon"},
        "phase2": {"hp_percent": 50, "action": "reality_tear"},
        "phase3": {"hp_percent": 25, "action": "soul_devour"},
        "enrage": {"hp_percent": 10, "buff": {"atk_mult": 2.5, "def_mult": 0.5}},
    },
    "drops": [
        ("abyss_heart", 1.0),
        ("void_crown", 0.5),
        ("reality_fragment", 0.3),
    ],
}
