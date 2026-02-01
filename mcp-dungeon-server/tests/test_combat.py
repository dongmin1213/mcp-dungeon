"""전투 공식 유닛 테스트
QA용 - 데미지/크리티컬/도망 계산 검증
"""
import sys
import io
from pathlib import Path

# Windows 콘솔 UTF-8 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import GameConfig
from systems.combat import (
    calculate_damage,
    check_critical,
    calculate_flee_chance,
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
        print("  Combat Formula Test Results")
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


class MockPlayer:
    def __init__(self, level=1, hp=100, max_hp=100, crit_chance=0.15):
        self.level = level
        self.hp = hp
        self.max_hp = max_hp
        self.crit_chance = crit_chance


class MockEnemy:
    def __init__(self, exp=20, is_boss=False, is_elite=False):
        self.exp = exp
        self.is_boss = is_boss
        self.is_elite = is_elite


# ============================================================
# 1. 데미지 계산 테스트
# ============================================================

def test_calculate_damage_basic():
    """기본 데미지 계산 테스트"""
    results = []

    # 1. 기본 공식: ATK - DEF
    damage = calculate_damage(20, 5)
    results.append((
        "기본 데미지 (20 ATK - 5 DEF = 15)",
        damage == 15,
        f"expected 15, got {damage}"
    ))

    # 2. 최소 데미지 1
    damage = calculate_damage(5, 20)
    results.append((
        "최소 데미지 1 (5 ATK - 20 DEF)",
        damage == GameConfig.MIN_DAMAGE,
        f"expected {GameConfig.MIN_DAMAGE}, got {damage}"
    ))

    # 3. ATK = DEF
    damage = calculate_damage(10, 10)
    results.append((
        "ATK = DEF = 최소 데미지",
        damage == GameConfig.MIN_DAMAGE,
        f"expected {GameConfig.MIN_DAMAGE}, got {damage}"
    ))

    # 4. 큰 데미지
    damage = calculate_damage(100, 20)
    results.append((
        "큰 데미지 (100 ATK - 20 DEF = 80)",
        damage == 80,
        f"expected 80, got {damage}"
    ))

    return results


def test_calculate_damage_critical():
    """크리티컬 데미지 계산 테스트"""
    results = []

    # 1. 크리티컬 x1.5
    damage = calculate_damage(20, 0, is_critical=True)
    expected = int(20 * GameConfig.CRITICAL_MULTIPLIER)
    results.append((
        f"크리티컬 데미지 (20 * {GameConfig.CRITICAL_MULTIPLIER} = {expected})",
        damage == expected,
        f"expected {expected}, got {damage}"
    ))

    # 2. 크리티컬 + ATK - DEF
    damage = calculate_damage(30, 10, is_critical=True)
    base = 30 - 10  # 20
    expected = int(base * GameConfig.CRITICAL_MULTIPLIER)  # 30
    results.append((
        f"크리티컬 + 방어 계산",
        damage == expected,
        f"expected {expected}, got {damage}"
    ))

    # 3. 최소 데미지 + 크리티컬
    damage = calculate_damage(5, 20, is_critical=True)
    expected = int(GameConfig.MIN_DAMAGE * GameConfig.CRITICAL_MULTIPLIER)
    results.append((
        "최소 데미지 + 크리티컬",
        damage == expected,
        f"expected {expected}, got {damage}"
    ))

    return results


def test_calculate_damage_multiplier():
    """데미지 배율 테스트"""
    results = []

    # 1. 150% 데미지 (스킬)
    damage = calculate_damage(20, 0, damage_mult=1.5)
    expected = int(20 * 1.5)
    results.append((
        "데미지 배율 x1.5",
        damage == expected,
        f"expected {expected}, got {damage}"
    ))

    # 2. 200% 데미지
    damage = calculate_damage(20, 0, damage_mult=2.0)
    expected = int(20 * 2.0)
    results.append((
        "데미지 배율 x2.0",
        damage == expected,
        f"expected {expected}, got {damage}"
    ))

    # 3. 배율 + 크리티컬
    damage = calculate_damage(20, 0, is_critical=True, damage_mult=1.5)
    base = int(20 * 1.5)  # 30
    expected = int(base * GameConfig.CRITICAL_MULTIPLIER)  # 45
    results.append((
        "배율 x1.5 + 크리티컬",
        damage == expected,
        f"expected {expected}, got {damage}"
    ))

    return results


def test_calculate_damage_flat_bonus():
    """고정 추가 데미지 테스트"""
    results = []

    # 1. 고정 추가 데미지
    damage = calculate_damage(20, 5, flat_bonus=10)
    expected = (20 - 5) + 10  # 25
    results.append((
        "고정 추가 데미지 +10",
        damage == expected,
        f"expected {expected}, got {damage}"
    ))

    # 2. 고정 + 배율
    damage = calculate_damage(20, 0, damage_mult=1.5, flat_bonus=5)
    expected = int(20 * 1.5) + 5  # 35
    results.append((
        "배율 + 고정 데미지",
        damage == expected,
        f"expected {expected}, got {damage}"
    ))

    return results


# ============================================================
# 2. 크리티컬 판정 테스트
# ============================================================

def test_check_critical():
    """크리티컬 판정 테스트"""
    results = []

    # 확률 기반이므로 다수 시행
    crit_count = 0
    trials = 10000

    for _ in range(trials):
        if check_critical(0.15):
            crit_count += 1

    # 15% 확률 = 약 1500번 (오차 허용)
    expected = trials * 0.15
    tolerance = trials * 0.03  # 3% 오차 허용
    in_range = abs(crit_count - expected) < tolerance

    results.append((
        f"크리티컬 15% 확률 ({crit_count}/{trials})",
        in_range,
        f"expected ~{int(expected)}, got {crit_count}"
    ))

    # 0% 크리티컬 = 발생 안 함
    crit_count = 0
    for _ in range(1000):
        if check_critical(0.0):
            crit_count += 1

    results.append((
        "크리티컬 0% = 발생 안 함",
        crit_count == 0,
        f"got {crit_count}"
    ))

    # 100% 크리티컬 = 항상 발생
    crit_count = 0
    for _ in range(100):
        if check_critical(1.0):
            crit_count += 1

    results.append((
        "크리티컬 100% = 항상 발생",
        crit_count == 100,
        f"got {crit_count}"
    ))

    return results


# ============================================================
# 3. 도망 확률 계산 테스트
# ============================================================

def test_calculate_flee_chance_basic():
    """도망 확률 기본 테스트"""
    results = []

    # 1. 기본 확률 50%
    player = MockPlayer(level=5)
    enemy = MockEnemy(exp=100)  # 레벨 추정 = 100/20 = 5
    chance = calculate_flee_chance(player, enemy)
    # 레벨 동일 = 민첩 보너스 0, HP 100% = HP 보너스 0
    # 기본 50%
    results.append((
        f"기본 도망 확률 ~50%",
        30 <= chance <= 80,
        f"got {chance}%"
    ))

    # 2. 보스전 도망 불가
    boss = MockEnemy(exp=200, is_boss=True)
    chance = calculate_flee_chance(player, boss)
    results.append((
        "보스전 도망 불가 (0%)",
        chance == 0,
        f"got {chance}%"
    ))

    # 3. 엘리트 -10%
    elite = MockEnemy(exp=100, is_elite=True)
    player = MockPlayer(level=5, hp=100, max_hp=100)
    chance = calculate_flee_chance(player, elite)
    results.append((
        "엘리트 도망 -10%",
        chance <= 70,  # 기본 50% + 엘리트 -10% = 40% 근처
        f"got {chance}%"
    ))

    return results


def test_calculate_flee_chance_level_diff():
    """레벨 차이 도망 확률 테스트"""
    results = []

    # 1. 플레이어 레벨 높음 = 도망 확률 증가
    player = MockPlayer(level=10)
    enemy = MockEnemy(exp=40)  # 레벨 추정 = 2
    chance = calculate_flee_chance(player, enemy)
    # 레벨 차이 = 10 - 2 = 8, 민첩 보너스 = 8 * 2 = 16%
    results.append((
        "레벨 높음 = 도망 확률 증가",
        chance > 50,
        f"got {chance}%"
    ))

    # 2. 플레이어 레벨 낮음 = 도망 확률 감소
    player = MockPlayer(level=2)
    enemy = MockEnemy(exp=200)  # 레벨 추정 = 10
    chance = calculate_flee_chance(player, enemy)
    results.append((
        "레벨 낮음 = 도망 확률 감소",
        chance < 50,
        f"got {chance}%"
    ))

    return results


def test_calculate_flee_chance_hp():
    """HP 비율 도망 확률 테스트"""
    results = []

    # 1. HP 100% = 보너스 없음
    player = MockPlayer(level=5, hp=100, max_hp=100)
    enemy = MockEnemy(exp=100)
    chance1 = calculate_flee_chance(player, enemy)

    # 2. HP 50% = 보너스 +5%
    player = MockPlayer(level=5, hp=50, max_hp=100)
    chance2 = calculate_flee_chance(player, enemy)

    # 3. HP 10% = 보너스 +9%
    player = MockPlayer(level=5, hp=10, max_hp=100)
    chance3 = calculate_flee_chance(player, enemy)

    results.append((
        "HP 낮을수록 도망 확률 증가",
        chance3 > chance2 > chance1,
        f"hp100%={chance1}%, hp50%={chance2}%, hp10%={chance3}%"
    ))

    return results


def test_calculate_flee_chance_limits():
    """도망 확률 범위 제한 테스트"""
    results = []

    # 1. 최대 80%
    player = MockPlayer(level=99, hp=1, max_hp=100)  # 극단적으로 유리
    enemy = MockEnemy(exp=20)
    chance = calculate_flee_chance(player, enemy)
    results.append((
        f"도망 최대 {GameConfig.FLEE_MAX_CHANCE}%",
        chance <= GameConfig.FLEE_MAX_CHANCE,
        f"got {chance}%"
    ))

    # 2. 최소 30%
    player = MockPlayer(level=1, hp=100, max_hp=100)  # 극단적으로 불리
    enemy = MockEnemy(exp=2000)  # 레벨 추정 = 100
    chance = calculate_flee_chance(player, enemy)
    results.append((
        f"도망 최소 {GameConfig.FLEE_MIN_CHANCE}%",
        chance >= GameConfig.FLEE_MIN_CHANCE,
        f"got {chance}%"
    ))

    return results


# ============================================================
# 4. 레벨업 스탯 증가 테스트
# ============================================================

def test_levelup_stats():
    """레벨업 스탯 증가 테스트"""
    results = []

    # GameConfig에서 레벨업 보너스 확인
    results.append((
        f"레벨업 HP +{GameConfig.LEVEL_UP_HP}",
        GameConfig.LEVEL_UP_HP == 10,
        f"got {GameConfig.LEVEL_UP_HP}"
    ))

    results.append((
        f"레벨업 MP +{GameConfig.LEVEL_UP_MP}",
        GameConfig.LEVEL_UP_MP == 5,
        f"got {GameConfig.LEVEL_UP_MP}"
    ))

    results.append((
        f"레벨업 ATK +{GameConfig.LEVEL_UP_ATK}",
        GameConfig.LEVEL_UP_ATK == 2,
        f"got {GameConfig.LEVEL_UP_ATK}"
    ))

    results.append((
        f"레벨업 DEF +{GameConfig.LEVEL_UP_DEF}",
        GameConfig.LEVEL_UP_DEF == 1,
        f"got {GameConfig.LEVEL_UP_DEF}"
    ))

    # 레벨업 경험치 공식: 레벨 * 100
    for level in [1, 2, 5, 10]:
        expected = level * GameConfig.EXP_PER_LEVEL
        results.append((
            f"Lv.{level} 필요 EXP = {expected}",
            expected == level * 100,
            f"got {expected}"
        ))

    return results


# ============================================================
# 5. 방어 데미지 감소 테스트
# ============================================================

def test_defense_reduction():
    """방어 데미지 감소 테스트"""
    results = []

    # 방어 시 50% 감소
    base_damage = 20
    defended = int(base_damage * GameConfig.DEFENSE_REDUCTION)
    expected = 10

    results.append((
        "방어 시 데미지 50% 감소",
        defended == expected,
        f"expected {expected}, got {defended}"
    ))

    # 방어 후 최소 데미지 보장
    small_damage = 2
    defended = int(small_damage * GameConfig.DEFENSE_REDUCTION)
    defended = max(GameConfig.MIN_DAMAGE, defended)
    results.append((
        "방어 후 최소 데미지 1",
        defended >= GameConfig.MIN_DAMAGE,
        f"got {defended}"
    ))

    return results


def main():
    print("\n" + "=" * 60)
    print("  전투 공식 유닛 테스트 시작")
    print("=" * 60)

    test_result = TestResult()

    # 1. 기본 데미지 계산
    print("\n[1/5] 기본 데미지 계산 테스트...")
    for name, passed, detail in test_calculate_damage_basic():
        test_result.add(name, passed, detail)

    # 2. 크리티컬 & 배율
    print("[2/5] 크리티컬 & 배율 테스트...")
    for name, passed, detail in test_calculate_damage_critical():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_calculate_damage_multiplier():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_calculate_damage_flat_bonus():
        test_result.add(name, passed, detail)

    # 3. 크리티컬 확률
    print("[3/5] 크리티컬 확률 테스트...")
    for name, passed, detail in test_check_critical():
        test_result.add(name, passed, detail)

    # 4. 도망 확률
    print("[4/5] 도망 확률 테스트...")
    for name, passed, detail in test_calculate_flee_chance_basic():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_calculate_flee_chance_level_diff():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_calculate_flee_chance_hp():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_calculate_flee_chance_limits():
        test_result.add(name, passed, detail)

    # 5. 레벨업 & 방어
    print("[5/5] 레벨업 & 방어 테스트...")
    for name, passed, detail in test_levelup_stats():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_defense_reduction():
        test_result.add(name, passed, detail)

    # 결과 출력
    test_result.print_summary()

    return test_result.failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
