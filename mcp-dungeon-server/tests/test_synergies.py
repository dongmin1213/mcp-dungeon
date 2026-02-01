"""시너지 시스템 유닛 테스트
QA용 - 실제 플레이 없이 시너지 검증
"""
import sys
import io
from pathlib import Path

# Windows 콘솔 UTF-8 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from seeds.synergies import (
    ALL_SYNERGIES,
    SET_SYNERGIES,
    ELEMENT_SYNERGIES,
    HIDDEN_SYNERGIES,
    get_synergy_by_id,
    get_hidden_synergies,
    get_visible_synergies,
)
from models.synergy import SynergyType
from systems.synergy import (
    apply_synergy_effects,
    get_synergy_bonus,
    has_synergy_effect,
    apply_execute,
    apply_lifesteal,
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
        print("  Synergy System Test Results")
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
# 1. 시너지 시드 데이터 테스트
# ============================================================

def test_synergy_definitions():
    """시너지 정의 테스트"""
    results = []

    # 1. 총 시너지 개수 확인 (10 세트 + 5 속성 + 3 숨겨진 = 18개)
    # 실제: SET_SYNERGIES 10개 + ELEMENT_SYNERGIES 5개 + HIDDEN_SYNERGIES 3개 = 18개
    expected_total = 10 + 5 + 3
    results.append((
        f"총 시너지 {expected_total}개",
        len(ALL_SYNERGIES) == expected_total,
        f"expected {expected_total}, got {len(ALL_SYNERGIES)}"
    ))

    # 2. 세트 시너지 10개
    results.append((
        "세트 시너지 10개",
        len(SET_SYNERGIES) == 10,
        f"expected 10, got {len(SET_SYNERGIES)}"
    ))

    # 3. 속성 시너지 5개
    results.append((
        "속성 시너지 5개",
        len(ELEMENT_SYNERGIES) == 5,
        f"expected 5, got {len(ELEMENT_SYNERGIES)}"
    ))

    # 4. 숨겨진 시너지 3개
    results.append((
        "숨겨진 시너지 3개",
        len(HIDDEN_SYNERGIES) == 3,
        f"expected 3, got {len(HIDDEN_SYNERGIES)}"
    ))

    # 5. 모든 시너지에 필수 필드 존재
    required_fields = ["id", "name", "description", "type", "effect"]
    for synergy in ALL_SYNERGIES:
        for field in required_fields:
            has_field = hasattr(synergy, field) and getattr(synergy, field) is not None
            if not has_field:
                results.append((f"{synergy.name} - {field} 필드", False, f"missing {field}"))
                break
        else:
            results.append((f"{synergy.name} - 필수 필드", True, ""))

    return results


def test_synergy_id_lookup():
    """ID로 시너지 조회 테스트"""
    results = []

    # 1. 세트 시너지 조회
    synergy = get_synergy_by_id("fire_master")
    results.append((
        "화염의 마스터 ID 조회",
        synergy is not None and synergy.name == "화염의 마스터",
        f"got {synergy}"
    ))

    # 2. 속성 시너지 조회
    synergy = get_synergy_by_id("fire_affinity")
    results.append((
        "화염 친화 ID 조회",
        synergy is not None and synergy.name == "화염 친화",
        f"got {synergy}"
    ))

    # 3. 숨겨진 시너지 조회
    synergy = get_synergy_by_id("curse_master")
    results.append((
        "저주의 주인 ID 조회",
        synergy is not None and synergy.name == "저주의 주인",
        f"got {synergy}"
    ))

    # 4. 존재하지 않는 ID
    synergy = get_synergy_by_id("nonexistent")
    results.append((
        "존재하지 않는 ID None",
        synergy is None,
        f"expected None, got {synergy}"
    ))

    return results


def test_hidden_visible_functions():
    """숨겨진/공개 시너지 분류 테스트"""
    results = []

    hidden = get_hidden_synergies()
    visible = get_visible_synergies()

    # 숨겨진 시너지 목록
    hidden_ids = {s.id for s in hidden}
    expected_hidden = {"vampire_lord", "shadow_walker", "fortune_seeker", "void_embrace",
                       "curse_bearer", "dungeon_master", "holy_blessing", "dark_pact",
                       "curse_master", "elemental_avatar", "immortal_tank"}

    results.append((
        "숨겨진 시너지 분류",
        len(hidden) > 0,
        f"hidden count: {len(hidden)}"
    ))

    results.append((
        "공개된 시너지 분류",
        len(visible) > 0,
        f"visible count: {len(visible)}"
    ))

    # 합계 = 전체
    results.append((
        "숨겨진 + 공개 = 전체",
        len(hidden) + len(visible) == len(ALL_SYNERGIES),
        f"{len(hidden)} + {len(visible)} = {len(ALL_SYNERGIES)}"
    ))

    return results


# ============================================================
# 2. 시너지 효과 계산 테스트
# ============================================================

def test_apply_synergy_effects():
    """시너지 효과 적용 테스트"""
    results = []

    # 1. 단일 시너지 적용
    fire_master = get_synergy_by_id("fire_master")
    effects = apply_synergy_effects(None, [fire_master])
    results.append((
        "화염의 마스터 fire_damage_mult",
        effects.get("fire_damage_mult") == 2.0,
        f"expected 2.0, got {effects.get('fire_damage_mult')}"
    ))
    results.append((
        "화염의 마스터 fire_immunity",
        effects.get("fire_immunity") is True,
        f"expected True, got {effects.get('fire_immunity')}"
    ))

    # 2. 다중 시너지 배율 곱셈
    fire_aff = get_synergy_by_id("fire_affinity")  # fire_damage_mult: 1.5
    effects = apply_synergy_effects(None, [fire_master, fire_aff])
    # 2.0 * 1.5 = 3.0
    results.append((
        "다중 시너지 배율 곱셈",
        effects.get("fire_damage_mult") == 3.0,
        f"expected 3.0 (2.0 * 1.5), got {effects.get('fire_damage_mult')}"
    ))

    # 3. 수치 합산
    warrior = get_synergy_by_id("warrior_spirit")  # atk: 8, def: 8
    crystal = get_synergy_by_id("crystal_resonance")  # def: 8
    effects = apply_synergy_effects(None, [warrior, crystal])
    results.append((
        "전사의 혼 atk +8",
        effects.get("atk") == 8,
        f"expected 8, got {effects.get('atk')}"
    ))
    # 전사의 혼(def:8) + 수정 공명(def:8) = 16
    results.append((
        "전사+수정 def 합산 16",
        effects.get("def") == 16,
        f"expected 16 (8+8), got {effects.get('def')}"
    ))

    # 4. bool 효과 OR
    curse_master = get_synergy_by_id("curse_master")
    effects = apply_synergy_effects(None, [curse_master])
    results.append((
        "저주의 주인 curse_to_blessing",
        effects.get("curse_to_blessing") is True,
        f"expected True, got {effects.get('curse_to_blessing')}"
    ))

    return results


def test_get_synergy_bonus():
    """특정 효과 보너스 조회 테스트"""
    results = []

    synergies = [
        get_synergy_by_id("fire_master"),      # fire_damage_mult: 2.0
        get_synergy_by_id("fire_affinity"),    # fire_damage_mult: 1.5
    ]

    # 배율 효과 조회
    bonus = get_synergy_bonus(synergies, "fire_damage_mult")
    # 곱셈: 2.0 * 1.5 = 3.0
    results.append((
        "fire_damage_mult 보너스 곱셈",
        bonus == 3.0,
        f"expected 3.0, got {bonus}"
    ))

    # 합산 효과 조회
    synergies2 = [
        get_synergy_by_id("warrior_spirit"),   # atk: 8
        get_synergy_by_id("void_embrace"),     # atk: 12
    ]
    bonus = get_synergy_bonus(synergies2, "atk")
    results.append((
        "atk 보너스 합산",
        bonus == 20,
        f"expected 20 (8+12), got {bonus}"
    ))

    return results


def test_has_synergy_effect():
    """효과 존재 확인 테스트"""
    results = []

    synergies = [get_synergy_by_id("fire_master")]

    results.append((
        "fire_immunity 존재",
        has_synergy_effect(synergies, "fire_immunity") is True,
        ""
    ))

    results.append((
        "ice_immunity 미존재",
        has_synergy_effect(synergies, "ice_immunity") is False,
        ""
    ))

    return results


# ============================================================
# 3. 시너지 전투 효과 테스트
# ============================================================

class MockEnemy:
    def __init__(self, hp=100, max_hp=100, is_boss=False):
        self.hp = hp
        self.max_hp = max_hp
        self.is_boss = is_boss
        self.name = "테스트 적"

    @property
    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)


class MockPlayer:
    def __init__(self, hp=100, max_hp=100):
        self.hp = hp
        self.max_hp = max_hp

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)


def test_apply_execute():
    """즉사 효과 테스트"""
    results = []

    # 1. HP 20% 이하 즉사
    enemy = MockEnemy(hp=15, max_hp=100)  # 15% HP
    executed, msg = apply_execute(enemy, 0.2)
    results.append((
        "HP 15% 적 즉사 (20% 임계)",
        executed is True and enemy.hp == 0,
        f"executed={executed}, hp={enemy.hp}"
    ))

    # 2. HP 25% - 즉사 안 됨
    enemy = MockEnemy(hp=25, max_hp=100)  # 25% HP
    executed, msg = apply_execute(enemy, 0.2)
    results.append((
        "HP 25% 적 즉사 안 됨",
        executed is False and enemy.hp == 25,
        f"executed={executed}, hp={enemy.hp}"
    ))

    # 3. 보스는 즉사 불가
    boss = MockEnemy(hp=10, max_hp=100, is_boss=True)
    executed, msg = apply_execute(boss, 0.2)
    results.append((
        "보스 즉사 불가",
        executed is False,
        f"executed={executed}"
    ))

    # 4. 임계값 0 = 즉사 없음
    enemy = MockEnemy(hp=1, max_hp=100)
    executed, msg = apply_execute(enemy, 0)
    results.append((
        "임계값 0 즉사 없음",
        executed is False,
        f"executed={executed}"
    ))

    return results


def test_apply_lifesteal():
    """흡혈 효과 테스트"""
    results = []

    # 1. 기본 흡혈 (20% 흡혈, 100 데미지 = 20 회복)
    player = MockPlayer(hp=50, max_hp=100)
    heal, msg = apply_lifesteal(player, 100, 0.2)
    results.append((
        "기본 흡혈 20%",
        heal == 20 and player.hp == 70,
        f"heal={heal}, hp={player.hp}"
    ))

    # 2. 흡혈 상한 (최대 HP의 30%)
    player = MockPlayer(hp=50, max_hp=100)
    heal, msg = apply_lifesteal(player, 200, 0.5)  # 50% 흡혈 = 100 회복 시도
    # 상한 = 100 * 0.3 = 30
    results.append((
        "흡혈 상한 30%",
        heal == 30,
        f"expected 30 (30% of 100), got {heal}"
    ))

    # 3. 0 데미지 = 흡혈 없음
    player = MockPlayer(hp=50, max_hp=100)
    heal, msg = apply_lifesteal(player, 0, 0.5)
    results.append((
        "0 데미지 흡혈 없음",
        heal == 0,
        f"heal={heal}"
    ))

    # 4. 0% 흡혈 = 회복 없음
    player = MockPlayer(hp=50, max_hp=100)
    heal, msg = apply_lifesteal(player, 100, 0)
    results.append((
        "0% 흡혈 없음",
        heal == 0,
        f"heal={heal}"
    ))

    return results


# ============================================================
# 4. 개별 시너지 효과 검증
# ============================================================

def test_individual_synergies():
    """개별 시너지 효과 정확성 검증"""
    results = []

    # 세트 시너지 검증
    synergy_checks = [
        ("fire_master", "fire_damage_mult", 2.0),
        ("vampire_lord", "lifesteal", 0.25),
        ("shadow_walker", "crit_bonus", 0.25),
        ("shadow_walker", "first_strike_mult", 2.0),
        ("fortune_seeker", "gold_mult", 2.0),
        ("fortune_seeker", "drop_mult", 3.0),
        ("arcane_master", "skill_damage_mult", 1.5),
        ("arcane_master", "mp_cost_reduction", 0.3),
        ("crystal_resonance", "magic_resist", 0.5),
        ("warrior_spirit", "counter_chance", 0.3),
        ("void_embrace", "execute_threshold", 0.2),
        ("void_embrace", "void_damage", 25),
        ("curse_bearer", "damage_mult", 1.5),
        ("curse_bearer", "curse_immunity", True),
        ("dungeon_master", "damage_mult", 1.5),
        ("dungeon_master", "damage_reduction", 0.2),
    ]

    for synergy_id, effect_key, expected in synergy_checks:
        synergy = get_synergy_by_id(synergy_id)
        if synergy:
            actual = synergy.effect.get(effect_key)
            passed = actual == expected
            results.append((
                f"{synergy.name} - {effect_key}",
                passed,
                f"expected {expected}, got {actual}"
            ))
        else:
            results.append((f"{synergy_id} 조회 실패", False, "synergy not found"))

    # 속성 시너지 검증
    element_checks = [
        ("fire_affinity", "burn_chance", 0.3),
        ("ice_affinity", "freeze_chance", 0.15),
        ("poison_mastery", "poison_damage_mult", 2.0),
        ("holy_blessing", "undead_damage_mult", 2.0),
        ("dark_pact", "soul_mult", 1.5),
    ]

    for synergy_id, effect_key, expected in element_checks:
        synergy = get_synergy_by_id(synergy_id)
        if synergy:
            actual = synergy.effect.get(effect_key)
            passed = actual == expected
            results.append((
                f"{synergy.name} - {effect_key}",
                passed,
                f"expected {expected}, got {actual}"
            ))

    # 숨겨진 시너지 검증
    hidden_checks = [
        ("curse_master", "curse_to_blessing", True),
        ("curse_master", "damage_mult", 2.0),
        ("elemental_avatar", "element_damage_mult", 2.5),
        ("elemental_avatar", "aura_damage", 10),
        ("immortal_tank", "lifesteal", 0.5),
        ("immortal_tank", "reflect_damage", 0.5),
        ("immortal_tank", "lifesteal_on_reflect", True),
    ]

    for synergy_id, effect_key, expected in hidden_checks:
        synergy = get_synergy_by_id(synergy_id)
        if synergy:
            actual = synergy.effect.get(effect_key)
            passed = actual == expected
            results.append((
                f"{synergy.name} - {effect_key}",
                passed,
                f"expected {expected}, got {actual}"
            ))

    return results


def test_synergy_types():
    """시너지 타입 검증"""
    results = []

    # 세트 시너지는 SET 타입
    for synergy in SET_SYNERGIES:
        results.append((
            f"{synergy.name} SET 타입",
            synergy.type == SynergyType.SET,
            f"got {synergy.type}"
        ))

    # 속성 시너지는 ELEMENT 타입
    for synergy in ELEMENT_SYNERGIES:
        results.append((
            f"{synergy.name} ELEMENT 타입",
            synergy.type == SynergyType.ELEMENT,
            f"got {synergy.type}"
        ))

    return results


def main():
    print("\n" + "=" * 60)
    print("  시너지 시스템 유닛 테스트 시작")
    print("=" * 60)

    test_result = TestResult()

    # 1. 시너지 정의
    print("\n[1/7] 시너지 정의 테스트...")
    for name, passed, detail in test_synergy_definitions():
        test_result.add(name, passed, detail)

    # 2. ID 조회
    print("[2/7] ID 조회 테스트...")
    for name, passed, detail in test_synergy_id_lookup():
        test_result.add(name, passed, detail)

    # 3. 숨겨진/공개 분류
    print("[3/7] 숨겨진/공개 분류 테스트...")
    for name, passed, detail in test_hidden_visible_functions():
        test_result.add(name, passed, detail)

    # 4. 효과 적용
    print("[4/7] 효과 적용 테스트...")
    for name, passed, detail in test_apply_synergy_effects():
        test_result.add(name, passed, detail)

    # 5. 보너스 조회
    print("[5/7] 보너스 조회 테스트...")
    for name, passed, detail in test_get_synergy_bonus():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_has_synergy_effect():
        test_result.add(name, passed, detail)

    # 6. 전투 효과
    print("[6/7] 전투 효과 테스트...")
    for name, passed, detail in test_apply_execute():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_apply_lifesteal():
        test_result.add(name, passed, detail)

    # 7. 개별 시너지 검증
    print("[7/7] 개별 시너지 검증...")
    for name, passed, detail in test_individual_synergies():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_synergy_types():
        test_result.add(name, passed, detail)

    # 결과 출력
    test_result.print_summary()

    return test_result.failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
