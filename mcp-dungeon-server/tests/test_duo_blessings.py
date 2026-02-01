"""듀오 축복 유닛 테스트
QA용 - 실제 플레이 없이 듀오 축복 시스템 검증
"""
import sys
import io
from pathlib import Path

# Windows 콘솔 UTF-8 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataclasses import dataclass, field
from typing import List, Any
from seeds.duo_blessings import (
    DUO_BLESSINGS,
    get_duo_by_id,
    get_duo_by_blessings,
    get_potential_duo,
    check_active_duos,
)
from systems.blessing import (
    check_and_apply_duos,
    get_duo_combat_effects,
)


@dataclass
class MockBlessing:
    """테스트용 가짜 축복"""
    id: str
    name: str = ""


@dataclass
class MockPlayer:
    """테스트용 가짜 플레이어"""
    hp: int = 100
    max_hp: int = 100
    mp: int = 50
    max_mp: int = 50
    atk: int = 15
    def_: int = 5
    blessings: List[Any] = field(default_factory=list)


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
        print("  Duo Blessing Test Results")
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
# 1. 듀오 축복 시드 데이터 테스트
# ============================================================

def test_duo_blessing_definitions():
    """듀오 축복 정의 테스트"""
    results = []

    # 1. 듀오 10개 정의 확인
    results.append((
        "듀오 축복 10개 정의",
        len(DUO_BLESSINGS) == 10,
        f"expected 10, got {len(DUO_BLESSINGS)}"
    ))

    # 2. 모든 듀오에 필수 필드 존재
    required_fields = ["id", "name", "icon", "blessing_a", "blessing_b", "description", "effect"]
    for duo in DUO_BLESSINGS:
        for field in required_fields:
            has_field = hasattr(duo, field) and getattr(duo, field)
            if not has_field:
                results.append((f"{duo.name} - {field} 필드", False, f"missing {field}"))
                break
        else:
            results.append((f"{duo.name} - 필수 필드", True, ""))

    # 3. 각 듀오의 effect 딕셔너리 확인
    for duo in DUO_BLESSINGS:
        has_effect = isinstance(duo.effect, dict) and len(duo.effect) > 0
        results.append((f"{duo.name} - effect 타입", has_effect, f"effect={type(duo.effect)}"))

    return results


def test_get_duo_by_id():
    """ID로 듀오 찾기 테스트"""
    results = []

    # 1. 존재하는 듀오 ID
    duo = get_duo_by_id("blood_frenzy")
    results.append(("피의 광기 ID 조회", duo is not None and duo.name == "피의 광기", f"got {duo}"))

    duo = get_duo_by_id("archmage")
    results.append(("아크메이지 ID 조회", duo is not None and duo.name == "아크메이지", f"got {duo}"))

    # 2. 존재하지 않는 듀오 ID
    duo = get_duo_by_id("nonexistent")
    results.append(("존재하지 않는 ID", duo is None, f"expected None, got {duo}"))

    return results


def test_get_duo_by_blessings():
    """축복 쌍으로 듀오 찾기 테스트"""
    results = []

    # 1. 정방향 조합
    duo = get_duo_by_blessings("vampiric", "berserker")
    results.append((
        "피의 광기 정방향",
        duo is not None and duo.id == "blood_frenzy",
        f"got {duo.id if duo else None}"
    ))

    # 2. 역방향 조합 (순서 무관)
    duo = get_duo_by_blessings("berserker", "vampiric")
    results.append((
        "피의 광기 역방향",
        duo is not None and duo.id == "blood_frenzy",
        f"got {duo.id if duo else None}"
    ))

    # 3. 일치하지 않는 조합
    duo = get_duo_by_blessings("vampiric", "iron_wall")
    results.append((
        "불일치 조합 None",
        duo is None,
        f"expected None, got {duo}"
    ))

    return results


def test_get_potential_duo():
    """잠재적 듀오 힌트 테스트"""
    results = []

    # 1. 광전사 보유 + 흡혈자 선택 시 = 피의 광기 힌트
    owned = {"berserker"}
    potential = get_potential_duo("vampiric", owned)
    results.append((
        "흡혈자+광전사 힌트",
        potential is not None and potential.id == "blood_frenzy",
        f"got {potential.id if potential else None}"
    ))

    # 2. 마나샘 보유 + 주문증폭 선택 시 = 아크메이지 힌트
    owned = {"mana_well"}
    potential = get_potential_duo("spell_amp", owned)
    results.append((
        "주문증폭+마나샘 힌트",
        potential is not None and potential.id == "archmage",
        f"got {potential.id if potential else None}"
    ))

    # 3. 조합 불가능 축복
    owned = {"vampiric"}
    potential = get_potential_duo("lucky", owned)
    results.append((
        "조합 불가 None",
        potential is None,
        f"expected None, got {potential}"
    ))

    return results


def test_check_active_duos():
    """활성 듀오 확인 테스트"""
    results = []

    # 1. 듀오 1개 활성화
    owned = {"vampiric", "berserker"}
    active = check_active_duos(owned)
    results.append((
        "피의 광기 단일 활성",
        len(active) == 1 and active[0].id == "blood_frenzy",
        f"got {[d.id for d in active]}"
    ))

    # 2. 듀오 2개 활성화 (광전사 공유)
    owned = {"berserker", "vampiric", "thorns"}  # 피의광기 + 분노의화신
    active = check_active_duos(owned)
    duo_ids = {d.id for d in active}
    expected = {"blood_frenzy", "rage_incarnate"}
    results.append((
        "듀오 2개 동시 활성",
        duo_ids == expected,
        f"expected {expected}, got {duo_ids}"
    ))

    # 3. 듀오 3개 활성화
    owned = {"berserker", "vampiric", "iron_wall", "thorns"}
    # 피의광기 + 분노의화신 + 고슴도치 + 완전한전사
    active = check_active_duos(owned)
    duo_ids = {d.id for d in active}
    expected = {"blood_frenzy", "rage_incarnate", "hedgehog", "perfect_warrior"}
    results.append((
        "듀오 4개 동시 활성",
        duo_ids == expected,
        f"expected {expected}, got {duo_ids}"
    ))

    # 4. 듀오 없음
    owned = {"vampiric", "lucky"}  # 조합 불가
    active = check_active_duos(owned)
    results.append((
        "활성 듀오 없음",
        len(active) == 0,
        f"expected [], got {[d.id for d in active]}"
    ))

    return results


# ============================================================
# 2. 듀오 효과 적용 테스트
# ============================================================

def test_check_and_apply_duos():
    """플레이어 듀오 효과 적용 테스트"""
    results = []

    # 1. 피의 광기 적용
    player = MockPlayer()
    player.blessings = [MockBlessing("vampiric"), MockBlessing("berserker")]
    applied = check_and_apply_duos(player)
    results.append((
        "피의 광기 효과 적용",
        len(applied) == 1 and applied[0][0] == "피의 광기",
        f"got {applied}"
    ))

    # 2. 빈 축복 = 적용 없음
    player = MockPlayer()
    player.blessings = []
    applied = check_and_apply_duos(player)
    results.append((
        "빈 축복 적용 없음",
        len(applied) == 0,
        f"expected [], got {applied}"
    ))

    # 3. blessings 속성 없음 = 에러 없이 빈 결과
    player = MockPlayer()
    del player.blessings
    applied = check_and_apply_duos(player)
    results.append((
        "blessings 없음 안전 처리",
        applied == [],
        f"expected [], got {applied}"
    ))

    return results


def test_get_duo_combat_effects():
    """전투 효과 계산 테스트"""
    results = []

    # 1. 피의 광기 효과
    player = MockPlayer()
    player.blessings = [MockBlessing("vampiric"), MockBlessing("berserker")]
    effects = get_duo_combat_effects(player)
    results.append((
        "피의 광기 lifesteal_bonus",
        effects.get("lifesteal_bonus", 0) == 1.0,
        f"expected 1.0, got {effects.get('lifesteal_bonus')}"
    ))

    # 2. 아크메이지 효과
    player = MockPlayer()
    player.blessings = [MockBlessing("mana_well"), MockBlessing("spell_amp")]
    effects = get_duo_combat_effects(player)
    results.append((
        "아크메이지 skill_mp_cost_mult",
        effects.get("skill_mp_cost_mult", 1) == 0.5,
        f"expected 0.5, got {effects.get('skill_mp_cost_mult')}"
    ))
    results.append((
        "아크메이지 skill_damage_mult",
        effects.get("skill_damage_mult", 1) == 2.0,
        f"expected 2.0, got {effects.get('skill_damage_mult')}"
    ))

    # 3. 폭풍의 검 효과
    player = MockPlayer()
    player.blessings = [MockBlessing("swift"), MockBlessing("multi_strike")]
    effects = get_duo_combat_effects(player)
    results.append((
        "폭풍의 검 attack_hits",
        effects.get("attack_hits", 1) == 3,
        f"expected 3, got {effects.get('attack_hits')}"
    ))

    # 4. 고슴도치 효과
    player = MockPlayer()
    player.blessings = [MockBlessing("iron_wall"), MockBlessing("thorns")]
    effects = get_duo_combat_effects(player)
    results.append((
        "고슴도치 defend_full_reflect",
        effects.get("defend_full_reflect", False) is True,
        f"expected True, got {effects.get('defend_full_reflect')}"
    ))

    # 5. 황금 손 효과
    player = MockPlayer()
    player.blessings = [MockBlessing("lucky"), MockBlessing("merchant")]
    effects = get_duo_combat_effects(player)
    results.append((
        "황금 손 gold_mult",
        effects.get("gold_mult", 1) == 3.0,
        f"expected 3.0, got {effects.get('gold_mult')}"
    ))
    results.append((
        "황금 손 shop_discount",
        effects.get("shop_discount", 0) == 0.5,
        f"expected 0.5, got {effects.get('shop_discount')}"
    ))

    # 6. 불멸의 투사 효과
    player = MockPlayer()
    player.blessings = [MockBlessing("tenacity"), MockBlessing("regeneration")]
    effects = get_duo_combat_effects(player)
    results.append((
        "불멸의 투사 death_save",
        effects.get("death_save", 0) == 1,
        f"expected 1, got {effects.get('death_save')}"
    ))
    results.append((
        "불멸의 투사 hp_regen_percent",
        effects.get("hp_regen_percent", 0) == 0.05,
        f"expected 0.05, got {effects.get('hp_regen_percent')}"
    ))

    # 7. 마나 폭주 효과
    player = MockPlayer()
    player.blessings = [MockBlessing("mana_well"), MockBlessing("regeneration")]
    effects = get_duo_combat_effects(player)
    results.append((
        "마나 폭주 full_mp_damage_bonus",
        effects.get("full_mp_damage_bonus", 0) == 0.5,
        f"expected 0.5, got {effects.get('full_mp_damage_bonus')}"
    ))
    results.append((
        "마나 폭주 mp_regen_percent",
        effects.get("mp_regen_percent", 0) == 0.1,
        f"expected 0.1, got {effects.get('mp_regen_percent')}"
    ))

    # 8. 암살자의 낙인 효과
    player = MockPlayer()
    player.blessings = [MockBlessing("executioner"), MockBlessing("poison_master")]
    effects = get_duo_combat_effects(player)
    results.append((
        "암살자의 낙인 poison_execute",
        effects.get("poison_execute_threshold", 0) == 0.3,
        f"expected 0.3, got {effects.get('poison_execute_threshold')}"
    ))

    # 9. 분노의 화신 효과
    player = MockPlayer()
    player.blessings = [MockBlessing("berserker"), MockBlessing("thorns")]
    effects = get_duo_combat_effects(player)
    results.append((
        "분노의 화신 hit_to_atk",
        effects.get("hit_to_atk", 0) == 0.1,
        f"expected 0.1, got {effects.get('hit_to_atk')}"
    ))
    results.append((
        "분노의 화신 max_rage_stacks",
        effects.get("max_rage_stacks", 0) == 5,
        f"expected 5, got {effects.get('max_rage_stacks')}"
    ))

    # 10. 완전한 전사 효과
    player = MockPlayer()
    player.blessings = [MockBlessing("iron_wall"), MockBlessing("berserker")]
    effects = get_duo_combat_effects(player)
    results.append((
        "완전한 전사 sync_atk_def",
        effects.get("sync_atk_def", False) is True,
        f"expected True, got {effects.get('sync_atk_def')}"
    ))

    return results


def test_multiple_duos_combined():
    """다중 듀오 효과 합산 테스트"""
    results = []

    # 광전사 + 철벽 + 가시 = 고슴도치 + 분노의화신 + 완전한전사
    player = MockPlayer()
    player.blessings = [
        MockBlessing("berserker"),
        MockBlessing("iron_wall"),
        MockBlessing("thorns"),
    ]
    effects = get_duo_combat_effects(player)

    # 고슴도치 효과
    results.append((
        "다중 듀오 defend_full_reflect",
        effects.get("defend_full_reflect", False) is True,
        f"got {effects.get('defend_full_reflect')}"
    ))

    # 분노의 화신 효과
    results.append((
        "다중 듀오 hit_to_atk",
        effects.get("hit_to_atk", 0) == 0.1,
        f"got {effects.get('hit_to_atk')}"
    ))

    # 완전한 전사 효과
    results.append((
        "다중 듀오 sync_atk_def",
        effects.get("sync_atk_def", False) is True,
        f"got {effects.get('sync_atk_def')}"
    ))

    return results


# ============================================================
# 3. 엣지 케이스 테스트
# ============================================================

def test_edge_cases():
    """엣지 케이스 테스트"""
    results = []

    # 1. 축복 1개만 보유
    player = MockPlayer()
    player.blessings = [MockBlessing("vampiric")]
    effects = get_duo_combat_effects(player)
    # 기본값 확인
    results.append((
        "축복 1개 - 기본값",
        effects.get("lifesteal_bonus", 0) == 0.0,
        f"expected 0.0, got {effects.get('lifesteal_bonus')}"
    ))

    # 2. 동일 축복 2개 (버그 방지)
    player = MockPlayer()
    player.blessings = [MockBlessing("vampiric"), MockBlessing("vampiric")]
    effects = get_duo_combat_effects(player)
    results.append((
        "동일 축복 중복 - 듀오 없음",
        effects.get("lifesteal_bonus", 0) == 0.0,
        f"expected 0.0, got {effects.get('lifesteal_bonus')}"
    ))

    # 3. 마나샘 공유 듀오 (아크메이지 + 마나폭주)
    player = MockPlayer()
    player.blessings = [
        MockBlessing("mana_well"),
        MockBlessing("spell_amp"),
        MockBlessing("regeneration"),
    ]
    effects = get_duo_combat_effects(player)
    # 아크메이지: skill_damage_mult 2.0
    # 마나폭주: mp_regen_percent 0.1
    results.append((
        "마나샘 공유 - 아크메이지",
        effects.get("skill_damage_mult", 1) == 2.0,
        f"expected 2.0, got {effects.get('skill_damage_mult')}"
    ))
    results.append((
        "마나샘 공유 - 마나폭주",
        effects.get("mp_regen_percent", 0) == 0.1,
        f"expected 0.1, got {effects.get('mp_regen_percent')}"
    ))

    return results


def main():
    print("\n" + "=" * 60)
    print("  듀오 축복 유닛 테스트 시작")
    print("=" * 60)

    test_result = TestResult()

    # 1. 듀오 축복 정의
    print("\n[1/8] 듀오 축복 정의 테스트...")
    for name, passed, detail in test_duo_blessing_definitions():
        test_result.add(name, passed, detail)

    # 2. ID 조회
    print("[2/8] ID 조회 테스트...")
    for name, passed, detail in test_get_duo_by_id():
        test_result.add(name, passed, detail)

    # 3. 축복 쌍 조회
    print("[3/8] 축복 쌍 조회 테스트...")
    for name, passed, detail in test_get_duo_by_blessings():
        test_result.add(name, passed, detail)

    # 4. 잠재적 듀오 힌트
    print("[4/8] 잠재적 듀오 힌트 테스트...")
    for name, passed, detail in test_get_potential_duo():
        test_result.add(name, passed, detail)

    # 5. 활성 듀오 확인
    print("[5/8] 활성 듀오 확인 테스트...")
    for name, passed, detail in test_check_active_duos():
        test_result.add(name, passed, detail)

    # 6. 플레이어 듀오 적용
    print("[6/8] 플레이어 듀오 적용 테스트...")
    for name, passed, detail in test_check_and_apply_duos():
        test_result.add(name, passed, detail)

    # 7. 전투 효과 계산
    print("[7/8] 전투 효과 계산 테스트...")
    for name, passed, detail in test_get_duo_combat_effects():
        test_result.add(name, passed, detail)

    # 8. 다중 듀오 합산
    print("[8/8] 다중 듀오 및 엣지 케이스 테스트...")
    for name, passed, detail in test_multiple_duos_combined():
        test_result.add(name, passed, detail)
    for name, passed, detail in test_edge_cases():
        test_result.add(name, passed, detail)

    # 결과 출력
    test_result.print_summary()

    return test_result.failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
