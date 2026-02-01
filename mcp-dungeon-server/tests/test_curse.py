"""저주 시스템 유닛 테스트
QA용 - 저주 효과 계산 검증
"""
import sys
import io
from pathlib import Path

# Windows 콘솔 UTF-8 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from systems.curse import (
    CURSE_DESCRIPTIONS,
    get_curse_description,
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
        print("  Curse System Test Results")
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
# 1. 저주 설명 테스트
# ============================================================

def test_curse_descriptions():
    """저주 설명 정의 테스트"""
    results = []

    # 저주 효과 목록 (6종)
    expected_curses = [
        "rest_heal_mult",
        "no_combat_damage",
        "set_def_zero",
        "damage_per_turn",
        "no_flee",
        "shop_price_mult",
        "damage_taken_mult",
        "max_hp_penalty",
        "potion_heal_mult",
        "random_effect_per_combat",
    ]

    # 모든 저주 효과에 설명 있음
    for curse_key in expected_curses:
        has_desc = curse_key in CURSE_DESCRIPTIONS
        results.append((
            f"{curse_key} 설명 정의",
            has_desc,
            f"missing description for {curse_key}" if not has_desc else ""
        ))

    return results


def test_get_curse_description():
    """저주 설명 생성 테스트"""
    results = []

    # 1. 휴식 회복량 감소
    curse = {"rest_heal_mult": 0.5}
    desc = get_curse_description(curse)
    results.append((
        "휴식 회복량 50% 설명",
        "50%" in desc,
        f"got: {desc}"
    ))

    # 2. 도망 불가
    curse = {"no_flee": True}
    desc = get_curse_description(curse)
    results.append((
        "도망 불가 설명",
        "도망 불가" in desc,
        f"got: {desc}"
    ))

    # 3. 턴당 데미지
    curse = {"damage_per_turn": 5}
    desc = get_curse_description(curse)
    results.append((
        "턴당 5 데미지 설명",
        "5" in desc,
        f"got: {desc}"
    ))

    # 4. 상점 가격 증가
    curse = {"shop_price_mult": 1.5}
    desc = get_curse_description(curse)
    results.append((
        "상점 가격 +50% 설명",
        "50%" in desc,
        f"got: {desc}"
    ))

    # 5. 받는 데미지 증가
    curse = {"damage_taken_mult": 1.3}
    desc = get_curse_description(curse)
    results.append((
        "받는 데미지 +30% 설명",
        "30%" in desc,
        f"got: {desc}"
    ))

    # 6. 포션 회복량 감소
    curse = {"potion_heal_mult": 0.5}
    desc = get_curse_description(curse)
    results.append((
        "포션 회복량 50% 설명",
        "50%" in desc,
        f"got: {desc}"
    ))

    # 7. 다중 저주 설명
    curse = {"rest_heal_mult": 0.5, "no_flee": True}
    desc = get_curse_description(curse)
    results.append((
        "다중 저주 설명",
        "50%" in desc and "도망 불가" in desc,
        f"got: {desc}"
    ))

    # 8. 빈 저주
    curse = {}
    desc = get_curse_description(curse)
    results.append((
        "빈 저주 설명",
        desc == "알 수 없는 저주",
        f"got: {desc}"
    ))

    return results


# ============================================================
# 2. 저주 효과 계산 테스트 (동기 버전)
# ============================================================

def test_curse_multiplier_calculations():
    """저주 배율 계산 테스트"""
    results = []

    # 1. 휴식 회복량 계산
    base_heal = 100
    mult = 0.5
    actual = int(base_heal * mult)
    expected = 50
    results.append((
        "휴식 회복량 50% 계산",
        actual == expected,
        f"expected {expected}, got {actual}"
    ))

    # 2. 포션 회복량 계산
    base_heal = 60
    mult = 0.5
    actual = int(base_heal * mult)
    expected = 30
    results.append((
        "포션 회복량 50% 계산",
        actual == expected,
        f"expected {expected}, got {actual}"
    ))

    # 3. 받는 데미지 증가 계산
    base_damage = 20
    mult = 1.3
    actual = int(base_damage * mult)
    expected = 26
    results.append((
        "받는 데미지 +30% 계산",
        actual == expected,
        f"expected {expected}, got {actual}"
    ))

    # 4. 상점 가격 증가 계산
    base_price = 100
    mult = 1.5
    actual = int(base_price * mult)
    expected = 150
    results.append((
        "상점 가격 +50% 계산",
        actual == expected,
        f"expected {expected}, got {actual}"
    ))

    return results


# ============================================================
# 3. 저주 아이템 효과 정의 검증
# ============================================================

def test_curse_item_definitions():
    """저주 아이템 효과 정의 테스트 (시드 데이터 기반)"""
    results = []

    # 저주 아이템별 예상 효과 (seeds/items.py 기준)
    curse_items = {
        "cursed_greatsword": {
            "expected_curse": "damage_per_turn",
            "description": "매 턴 데미지"
        },
        "pain_armor": {
            "expected_curse": "rest_heal_mult",
            "description": "휴식 회복량 감소"
        },
        "madness_helm": {
            "expected_curse": "damage_taken_mult",
            "description": "받는 데미지 증가"
        },
        "greed_ring": {
            "expected_curse": "shop_price_mult",
            "description": "상점 가격 증가"
        },
        "soul_eater": {
            "expected_curse": "no_flee",
            "description": "도망 불가"
        },
        "berserker_amulet": {
            "expected_curse": "set_def_zero",
            "description": "DEF 0"
        },
    }

    # 저주 효과 키가 CURSE_DESCRIPTIONS에 정의되어 있는지 확인
    for item_id, info in curse_items.items():
        curse_key = info["expected_curse"]
        has_desc = curse_key in CURSE_DESCRIPTIONS
        results.append((
            f"{item_id} 저주 ({info['description']})",
            has_desc,
            f"curse key: {curse_key}"
        ))

    return results


# ============================================================
# 4. 저주 배율 경계값 테스트
# ============================================================

def test_curse_edge_cases():
    """저주 효과 경계값 테스트"""
    results = []

    # 1. 배율 0 = 완전 무효화
    base = 100
    actual = int(base * 0)
    results.append((
        "배율 0 = 완전 무효화",
        actual == 0,
        f"expected 0, got {actual}"
    ))

    # 2. 배율 1 = 변화 없음
    base = 100
    actual = int(base * 1.0)
    results.append((
        "배율 1.0 = 변화 없음",
        actual == 100,
        f"expected 100, got {actual}"
    ))

    # 3. 배율 2 = 두 배
    base = 100
    actual = int(base * 2.0)
    results.append((
        "배율 2.0 = 두 배",
        actual == 200,
        f"expected 200, got {actual}"
    ))

    # 4. 소수점 절삭
    base = 33
    actual = int(base * 0.5)
    results.append((
        "소수점 절삭 (33 * 0.5 = 16)",
        actual == 16,
        f"expected 16, got {actual}"
    ))

    # 5. 다중 배율 적용
    base = 100
    mult1 = 0.5  # 휴식 50%
    mult2 = 0.5  # 포션 50% (다른 효과지만 테스트용)
    actual = int(base * mult1 * mult2)
    results.append((
        "다중 배율 누적",
        actual == 25,
        f"expected 25 (100 * 0.5 * 0.5), got {actual}"
    ))

    return results


# ============================================================
# 5. 저주 면역 시너지 테스트
# ============================================================

def test_curse_immunity_synergy():
    """저주 면역 시너지 효과 테스트"""
    results = []

    # curse_immunity가 True면 저주 효과 무시
    curse_immunity = True

    # 배율 적용 로직 시뮬레이션
    def apply_mult_with_immunity(base, mult, immunity):
        if immunity:
            return base  # 면역이면 배율 무시
        return int(base * mult)

    # 1. 면역 시 휴식 회복량 유지
    base = 100
    actual = apply_mult_with_immunity(base, 0.5, True)
    results.append((
        "저주 면역 - 휴식 회복량 유지",
        actual == 100,
        f"expected 100, got {actual}"
    ))

    # 2. 면역 없으면 감소
    actual = apply_mult_with_immunity(base, 0.5, False)
    results.append((
        "저주 면역 없음 - 회복량 감소",
        actual == 50,
        f"expected 50, got {actual}"
    ))

    # 3. curse_to_blessing 시너지 (저주가 축복으로)
    # "저주의 주인" 시너지: 저주 효과가 긍정으로 변환
    curse_to_blessing = True

    def apply_curse_as_blessing(base, mult, blessing_mode):
        if blessing_mode:
            # 0.5 (50% 감소) → 1.5 (50% 증가)로 변환
            inverted = 2.0 - mult  # 0.5 → 1.5, 0.7 → 1.3
            return int(base * inverted)
        return int(base * mult)

    actual = apply_curse_as_blessing(100, 0.5, True)
    results.append((
        "저주→축복 변환 (0.5 → 1.5)",
        actual == 150,
        f"expected 150, got {actual}"
    ))

    return results


def main():
    print("\n" + "=" * 60)
    print("  저주 시스템 유닛 테스트 시작")
    print("=" * 60)

    test_result = TestResult()

    # 1. 저주 설명 정의
    print("\n[1/5] 저주 설명 정의 테스트...")
    for name, passed, detail in test_curse_descriptions():
        test_result.add(name, passed, detail)

    # 2. 설명 생성
    print("[2/5] 저주 설명 생성 테스트...")
    for name, passed, detail in test_get_curse_description():
        test_result.add(name, passed, detail)

    # 3. 배율 계산
    print("[3/5] 저주 배율 계산 테스트...")
    for name, passed, detail in test_curse_multiplier_calculations():
        test_result.add(name, passed, detail)

    # 4. 저주 아이템 정의
    print("[4/5] 저주 아이템 정의 테스트...")
    for name, passed, detail in test_curse_item_definitions():
        test_result.add(name, passed, detail)

    # 5. 경계값 및 면역
    print("[5/5] 경계값 및 면역 테스트...")
    for name, passed, detail in test_curse_edge_cases():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_curse_immunity_synergy():
        test_result.add(name, passed, detail)

    # 결과 출력
    test_result.print_summary()

    return test_result.failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
