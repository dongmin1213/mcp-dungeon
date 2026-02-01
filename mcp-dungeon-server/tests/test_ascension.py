"""승천 모드 유닛 테스트
QA용 - 승천 규칙 검증
"""
import sys
import io
from pathlib import Path

# Windows 콘솔 UTF-8 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from systems.ascension import (
    ASCENSION_LEVELS,
    AscensionModifier,
    AscensionManager,
    get_ascension_modifier,
    get_all_active_modifiers,
    get_combined_effects,
    get_ascension_display,
    get_ascension_description,
)


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def add(self, name: str, passed: bool, detail: str = ""):
        self.results.append((name, passed, detail))
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def print_summary(self):
        print("\n" + "=" * 60)
        print("  Ascension Mode Test Results")
        print("=" * 60)

        for name, passed, detail in self.results:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} | {name}")
            if detail and not passed:
                print(f"          -> {detail}")

        print("-" * 60)
        total = self.passed + self.failed
        print(f"  Total: {total} | PASS: {self.passed} | FAIL: {self.failed}")
        print("=" * 60)


# ============================================================
# 1. 승천 레벨 정의 테스트
# ============================================================

def test_ascension_definitions():
    """승천 레벨 정의 테스트"""
    results = []

    # 1. 11개 레벨 정의 (0~10)
    results.append((
        "11개 레벨 정의 (0~10)",
        len(ASCENSION_LEVELS) == 11,
        f"expected 11, got {len(ASCENSION_LEVELS)}"
    ))

    # 2. 모든 레벨에 필수 필드
    for level, modifier in ASCENSION_LEVELS.items():
        has_fields = (
            hasattr(modifier, "id") and
            hasattr(modifier, "name") and
            hasattr(modifier, "description") and
            hasattr(modifier, "modifier_type") and
            hasattr(modifier, "effect")
        )
        results.append((
            f"승천 {level} 필수 필드",
            has_fields,
            f"level {level}"
        ))

    return results


def test_individual_ascension_levels():
    """개별 승천 레벨 효과 테스트"""
    results = []

    # 각 레벨별 예상 효과
    expected = {
        0: {"type": "none", "effects": {}},
        1: {"type": "stat", "effects": {"elite_hp_mult": 1.2}},
        2: {"type": "rule", "effects": {"shop_no_potions": True}},
        3: {"type": "stat", "effects": {"trap_damage_mult": 1.5}},
        4: {"type": "rule", "effects": {"enemy_first_strike": True}},
        5: {"type": "rule", "effects": {"blessing_choices": 2}},
        6: {"type": "stat", "effects": {"boss_hp_mult": 1.3}},
        7: {"type": "stat", "effects": {"rest_heal_mult": 0.5}},
        8: {"type": "rule", "effects": {"no_flee_until_boss": True}},
        9: {"type": "rule", "effects": {"elite_skip_curse": True}},
        10: {"type": "spawn", "effects": {"hidden_boss": "abyss_lord", "extra_floor": True}},
    }

    for level, exp in expected.items():
        modifier = ASCENSION_LEVELS.get(level)
        if modifier:
            # 타입 확인
            type_match = modifier.modifier_type == exp["type"]
            results.append((
                f"승천 {level} 타입 '{exp['type']}'",
                type_match,
                f"expected {exp['type']}, got {modifier.modifier_type}"
            ))

            # 효과 확인
            for key, value in exp["effects"].items():
                actual = modifier.effect.get(key)
                results.append((
                    f"승천 {level} {key}={value}",
                    actual == value,
                    f"expected {value}, got {actual}"
                ))
        else:
            results.append((f"승천 {level} 정의 누락", False, ""))

    return results


# ============================================================
# 2. 승천 효과 누적 테스트
# ============================================================

def test_get_all_active_modifiers():
    """활성 효과 누적 테스트"""
    results = []

    # 승천 0 = 효과 없음
    modifiers = get_all_active_modifiers(0)
    results.append((
        "승천 0 = 활성 효과 없음",
        len(modifiers) == 0,
        f"expected 0, got {len(modifiers)}"
    ))

    # 승천 1 = 1개 효과
    modifiers = get_all_active_modifiers(1)
    results.append((
        "승천 1 = 1개 효과",
        len(modifiers) == 1,
        f"expected 1, got {len(modifiers)}"
    ))

    # 승천 5 = 5개 효과 (1~5)
    modifiers = get_all_active_modifiers(5)
    results.append((
        "승천 5 = 5개 효과",
        len(modifiers) == 5,
        f"expected 5, got {len(modifiers)}"
    ))

    # 승천 10 = 10개 효과 (1~10)
    modifiers = get_all_active_modifiers(10)
    results.append((
        "승천 10 = 10개 효과",
        len(modifiers) == 10,
        f"expected 10, got {len(modifiers)}"
    ))

    return results


def test_get_combined_effects():
    """효과 합산 테스트"""
    results = []

    # 승천 0 = 기본값
    effects = get_combined_effects(0)
    results.append((
        "승천 0 elite_hp_mult=1.0",
        effects.get("elite_hp_mult") == 1.0,
        f"got {effects.get('elite_hp_mult')}"
    ))
    results.append((
        "승천 0 shop_no_potions=False",
        effects.get("shop_no_potions") is False,
        f"got {effects.get('shop_no_potions')}"
    ))
    results.append((
        "승천 0 blessing_choices=3",
        effects.get("blessing_choices") == 3,
        f"got {effects.get('blessing_choices')}"
    ))

    # 승천 1 = 엘리트 HP +20%
    effects = get_combined_effects(1)
    results.append((
        "승천 1 elite_hp_mult=1.2",
        effects.get("elite_hp_mult") == 1.2,
        f"got {effects.get('elite_hp_mult')}"
    ))

    # 승천 2 = 상점 포션 비활성
    effects = get_combined_effects(2)
    results.append((
        "승천 2 shop_no_potions=True",
        effects.get("shop_no_potions") is True,
        f"got {effects.get('shop_no_potions')}"
    ))

    # 승천 5 = 축복 선택지 2개
    effects = get_combined_effects(5)
    results.append((
        "승천 5 blessing_choices=2",
        effects.get("blessing_choices") == 2,
        f"got {effects.get('blessing_choices')}"
    ))

    # 승천 6 = 보스 HP +30%
    effects = get_combined_effects(6)
    results.append((
        "승천 6 boss_hp_mult=1.3",
        effects.get("boss_hp_mult") == 1.3,
        f"got {effects.get('boss_hp_mult')}"
    ))

    # 승천 10 = 히든 보스 + 추가 층
    effects = get_combined_effects(10)
    results.append((
        "승천 10 hidden_boss=abyss_lord",
        effects.get("hidden_boss") == "abyss_lord",
        f"got {effects.get('hidden_boss')}"
    ))
    results.append((
        "승천 10 extra_floor=True",
        effects.get("extra_floor") is True,
        f"got {effects.get('extra_floor')}"
    ))

    return results


# ============================================================
# 3. AscensionManager 테스트
# ============================================================

def test_ascension_manager():
    """AscensionManager 클래스 테스트"""
    results = []

    # 승천 0 매니저
    mgr = AscensionManager(0)
    results.append((
        "Manager 승천 0 생성",
        mgr.level == 0,
        f"level={mgr.level}"
    ))
    results.append((
        "Manager get_elite_hp_modifier=1.0",
        mgr.get_elite_hp_modifier() == 1.0,
        f"got {mgr.get_elite_hp_modifier()}"
    ))
    results.append((
        "Manager is_shop_potions_disabled=False",
        mgr.is_shop_potions_disabled() is False,
        f"got {mgr.is_shop_potions_disabled()}"
    ))
    results.append((
        "Manager get_blessing_choices_count=3",
        mgr.get_blessing_choices_count() == 3,
        f"got {mgr.get_blessing_choices_count()}"
    ))

    # 승천 5 매니저
    mgr = AscensionManager(5)
    results.append((
        "Manager 승천 5 축복 2개",
        mgr.get_blessing_choices_count() == 2,
        f"got {mgr.get_blessing_choices_count()}"
    ))
    results.append((
        "Manager 승천 5 적 선공",
        mgr.is_enemy_first_strike() is True,
        f"got {mgr.is_enemy_first_strike()}"
    ))

    # 승천 10 매니저
    mgr = AscensionManager(10)
    results.append((
        "Manager 승천 10 히든 보스",
        mgr.has_hidden_boss() is True,
        f"got {mgr.has_hidden_boss()}"
    ))
    results.append((
        "Manager 승천 10 히든 보스 ID",
        mgr.get_hidden_boss_id() == "abyss_lord",
        f"got {mgr.get_hidden_boss_id()}"
    ))
    results.append((
        "Manager 승천 10 추가 층",
        mgr.has_extra_floor() is True,
        f"got {mgr.has_extra_floor()}"
    ))
    results.append((
        "Manager 승천 10 최대 층 6",
        mgr.get_max_floor() == 6,
        f"got {mgr.get_max_floor()}"
    ))

    return results


def test_ascension_manager_flee():
    """도망 제한 테스트 (승천 8)"""
    results = []

    # 승천 0 = 도망 가능
    mgr = AscensionManager(0)
    results.append((
        "승천 0 도망 가능",
        mgr.can_flee() is True,
        ""
    ))

    # 승천 8 = 보스 처치 전 도망 불가
    mgr = AscensionManager(8)
    results.append((
        "승천 8 보스 처치 전 도망 불가",
        mgr.can_flee() is False,
        f"boss_killed={mgr.boss_killed_this_floor}"
    ))

    # 보스 처치 후 도망 가능
    mgr.on_boss_killed()
    results.append((
        "승천 8 보스 처치 후 도망 가능",
        mgr.can_flee() is True,
        f"boss_killed={mgr.boss_killed_this_floor}"
    ))

    # 층 이동 시 리셋
    mgr.on_floor_change()
    results.append((
        "승천 8 층 이동 후 도망 불가",
        mgr.can_flee() is False,
        f"boss_killed={mgr.boss_killed_this_floor}"
    ))

    return results


# ============================================================
# 4. 표시 함수 테스트
# ============================================================

def test_display_functions():
    """표시 함수 테스트"""
    results = []

    # get_ascension_display
    results.append((
        "승천 0 표시 = '일반'",
        get_ascension_display(0) == "일반",
        f"got {get_ascension_display(0)}"
    ))
    results.append((
        "승천 5 표시 = '승천 5'",
        get_ascension_display(5) == "승천 5",
        f"got {get_ascension_display(5)}"
    ))

    # get_ascension_description
    desc = get_ascension_description(0)
    results.append((
        "승천 0 설명 = 기본",
        "기본" in desc,
        f"got {desc}"
    ))

    desc = get_ascension_description(5)
    results.append((
        "승천 5 설명 포함 '축복'",
        "축복" in desc,
        f"got {desc}"
    ))

    # 누적 설명 확인
    desc = get_ascension_description(10)
    # 10개 효과가 모두 포함되어야 함
    results.append((
        "승천 10 설명 항목 10개",
        desc.count("•") == 10,
        f"bullet count: {desc.count('•')}"
    ))

    return results


# ============================================================
# 5. 배율 계산 테스트
# ============================================================

def test_stat_multipliers():
    """스탯 배율 계산 테스트"""
    results = []

    # 엘리트 HP 배율 (승천 1: 1.2)
    mgr = AscensionManager(1)
    base_hp = 100
    modified_hp = int(base_hp * mgr.get_elite_hp_modifier())
    results.append((
        "엘리트 HP 120%",
        modified_hp == 120,
        f"expected 120, got {modified_hp}"
    ))

    # 보스 HP 배율 (승천 6: 1.3)
    mgr = AscensionManager(6)
    base_hp = 200
    modified_hp = int(base_hp * mgr.get_boss_hp_modifier())
    results.append((
        "보스 HP 130%",
        modified_hp == 260,
        f"expected 260, got {modified_hp}"
    ))

    # 함정 데미지 배율 (승천 3: 1.5)
    mgr = AscensionManager(3)
    base_damage = 20
    modified_damage = int(base_damage * mgr.get_trap_damage_modifier())
    results.append((
        "함정 데미지 150%",
        modified_damage == 30,
        f"expected 30, got {modified_damage}"
    ))

    # 휴식 회복 배율 (승천 7: 0.5)
    mgr = AscensionManager(7)
    base_heal = 50
    modified_heal = int(base_heal * mgr.get_rest_heal_modifier())
    results.append((
        "휴식 회복 50%",
        modified_heal == 25,
        f"expected 25, got {modified_heal}"
    ))

    return results


def main():
    print("\n" + "=" * 60)
    print("  승천 모드 유닛 테스트 시작")
    print("=" * 60)

    test_result = TestResult()

    # 1. 승천 정의
    print("\n[1/5] 승천 정의 테스트...")
    for name, passed, detail in test_ascension_definitions():
        test_result.add(name, passed, detail)

    # 2. 개별 레벨 효과
    print("[2/5] 개별 레벨 효과 테스트...")
    for name, passed, detail in test_individual_ascension_levels():
        test_result.add(name, passed, detail)

    # 3. 효과 누적
    print("[3/5] 효과 누적 테스트...")
    for name, passed, detail in test_get_all_active_modifiers():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_get_combined_effects():
        test_result.add(name, passed, detail)

    # 4. AscensionManager
    print("[4/5] AscensionManager 테스트...")
    for name, passed, detail in test_ascension_manager():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_ascension_manager_flee():
        test_result.add(name, passed, detail)

    # 5. 표시 함수 & 배율 계산
    print("[5/5] 표시 함수 & 배율 계산 테스트...")
    for name, passed, detail in test_display_functions():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_stat_multipliers():
        test_result.add(name, passed, detail)

    # 결과 출력
    test_result.print_summary()

    return test_result.failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
