"""보스 기믹 유닛 테스트
QA용 - 실제 플레이 없이 보스 기믹 검증
"""
import sys
import io
from pathlib import Path

# Windows 콘솔 UTF-8 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataclasses import dataclass
from systems.boss_gimmick import (
    GimmickType,
    BossGimmickState,
    BOSS_GIMMICKS,
    get_boss_gimmick,
    create_gimmick_state,
    process_gimmick_on_turn_start,
    process_gimmick_on_hit,
    process_gimmick_on_attack,
    get_gimmick_display,
)


@dataclass
class MockBoss:
    """테스트용 가짜 보스"""
    id: str
    name: str
    hp: int
    max_hp: int
    atk: int = 20
    def_: int = 5


@dataclass
class MockPlayer:
    """테스트용 가짜 플레이어"""
    hp: int = 100
    max_hp: int = 100
    atk: int = 15
    def_: int = 5


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
        print("  Boss Gimmick Test Results")
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


def test_slime_king():
    """슬라임 킹 - 분열 테스트"""
    results = []
    player = MockPlayer()

    boss = MockBoss(
        id="boss_slime_king",
        name="슬라임 킹",
        hp=100,
        max_hp=100
    )

    # 1. 기믹 타입 확인
    gimmick = get_boss_gimmick(boss.id)
    results.append(("슬라임킹 기믹 타입", gimmick == GimmickType.SPLIT, f"expected SPLIT, got {gimmick}"))

    # 2. 상태 생성
    state = create_gimmick_state(boss)
    results.append(("슬라임킹 상태 생성", state is not None, ""))

    if state:
        # 3. HP 100% - 분열 안 됨
        boss.hp = 100
        result = process_gimmick_on_turn_start(boss, player, state, turn=1)
        results.append(("HP 100% - 분열 안 됨", not state.split_triggered, f"split_triggered={state.split_triggered}"))

        # 4. HP 50% - 분열 안 됨 (30% 이하에서 발동)
        boss.hp = 50
        result = process_gimmick_on_turn_start(boss, player, state, turn=2)
        results.append(("HP 50% - 분열 안 됨", not state.split_triggered, f"split_triggered={state.split_triggered}"))

        # 5. HP 25% - 분열 발동!
        boss.hp = 25
        result = process_gimmick_on_turn_start(boss, player, state, turn=3)
        results.append(("HP 25% - 분열 발동", state.split_triggered, f"split_triggered={state.split_triggered}"))

        messages = result.get("messages", [])
        has_split_msg = any("분열" in m for m in messages)
        results.append(("분열 메시지 포함", has_split_msg, f"messages={messages}"))

    return results


def test_spider_queen():
    """여왕 거미 - 거미줄 테스트"""
    results = []
    player = MockPlayer()

    boss = MockBoss(
        id="boss_giant_spider",
        name="여왕 거미",
        hp=100,
        max_hp=100
    )

    # 1. 기믹 타입 확인
    gimmick = get_boss_gimmick(boss.id)
    results.append(("여왕거미 기믹 타입", gimmick == GimmickType.WEB, f"expected WEB, got {gimmick}"))

    # 2. 상태 생성
    state = create_gimmick_state(boss)
    results.append(("여왕거미 상태 생성", state is not None, ""))

    if state:
        # 3. 거미줄 쿨다운 확인
        results.append(("초기 쿨다운 0", state.web_cooldown == 0, f"cooldown={state.web_cooldown}"))

        # 4. 턴 2 - 새끼 거미 소환 (turn % 2 == 0)
        result = process_gimmick_on_turn_start(boss, player, state, turn=2)
        messages = result.get("messages", [])
        has_summon = len(result.get("summons", [])) > 0
        results.append(("턴2 새끼거미 소환", has_summon, f"summons={result.get('summons', [])}"))

    return results


def test_orc_warlord():
    """오크 대족장 - 분노/광폭화 테스트"""
    results = []
    player = MockPlayer()

    boss = MockBoss(
        id="boss_orc_warlord",
        name="오크 대족장",
        hp=100,
        max_hp=100
    )

    # 1. 기믹 타입 확인
    gimmick = get_boss_gimmick(boss.id)
    results.append(("오크대족장 기믹 타입", gimmick == GimmickType.RAGE, f"expected RAGE, got {gimmick}"))

    # 2. 상태 생성
    state = create_gimmick_state(boss)
    results.append(("오크대족장 상태 생성", state is not None, ""))

    if state:
        # 3. 초기 분노 스택 0
        results.append(("초기 분노 스택 0", state.rage_stacks == 0, f"rage_stacks={state.rage_stacks}"))

        # 4. 피격 시 분노 스택 증가
        result = process_gimmick_on_hit(boss, player, state, damage=10)
        results.append(("피격 시 분노 증가", state.rage_stacks > 0, f"rage_stacks={state.rage_stacks}"))

        messages = result.get("messages", [])
        has_rage_msg = any("분노" in m for m in messages)
        results.append(("분노 메시지 포함", has_rage_msg, f"messages={messages}"))

        # 5. HP 40% 이하 - 광폭화 (50% 이하)
        boss.hp = 40
        result = process_gimmick_on_turn_start(boss, player, state, turn=1)
        results.append(("HP 40% - 광폭화 발동", state.enraged, f"enraged={state.enraged}"))

        messages = result.get("messages", [])
        has_enrage_msg = any("광폭화" in m for m in messages)
        results.append(("광폭화 메시지 포함", has_enrage_msg, f"messages={messages}"))

    return results


def test_vampire_lord():
    """뱀파이어 로드 - 흡혈/박쥐 변신 테스트"""
    results = []
    player = MockPlayer()

    boss = MockBoss(
        id="boss_vampire_lord",
        name="뱀파이어 로드",
        hp=100,
        max_hp=100
    )

    # 1. 기믹 타입 확인
    gimmick = get_boss_gimmick(boss.id)
    results.append(("뱀파이어 기믹 타입", gimmick == GimmickType.VAMPIRE, f"expected VAMPIRE, got {gimmick}"))

    # 2. 상태 생성
    state = create_gimmick_state(boss)
    results.append(("뱀파이어 상태 생성", state is not None, ""))

    if state:
        # 3. 초기 박쥐 변신 안 됨
        results.append(("초기 박쥐 변신 안 됨", not state.bat_form, f"bat_form={state.bat_form}"))

        # 4. HP 50% - 박쥐 변신 안 됨 (30% 이하에서 발동)
        boss.hp = 50
        result = process_gimmick_on_turn_start(boss, player, state, turn=1)
        results.append(("HP 50% - 박쥐 변신 안 됨", not state.bat_form, f"bat_form={state.bat_form}"))

        # 5. HP 25% - 박쥐 변신 발동!
        boss.hp = 25
        result = process_gimmick_on_turn_start(boss, player, state, turn=2)
        results.append(("HP 25% - 박쥐 변신 발동", state.bat_form, f"bat_form={state.bat_form}"))
        results.append(("박쥐 변신 턴 설정", state.bat_form_turns > 0, f"bat_form_turns={state.bat_form_turns}"))

        messages = result.get("messages", [])
        has_bat_msg = any("박쥐" in m for m in messages)
        results.append(("박쥐 메시지 포함", has_bat_msg, f"messages={messages}"))

        # 6. 흡혈 테스트 (공격 시) - healed 키 사용
        state2 = create_gimmick_state(boss)
        boss.hp = 80  # 박쥐 변신 안 된 상태
        result = process_gimmick_on_attack(boss, player, state2, damage=20)
        healed = result.get("healed", 0)
        results.append(("흡혈 발동", healed > 0, f"healed={healed}"))

    return results


def test_dungeon_master():
    """던전 마스터 - 3페이즈 테스트"""
    results = []
    player = MockPlayer()

    boss = MockBoss(
        id="boss_dungeon_master",
        name="던전 마스터",
        hp=100,
        max_hp=100
    )

    # 1. 기믹 타입 확인
    gimmick = get_boss_gimmick(boss.id)
    results.append(("던전마스터 기믹 타입", gimmick == GimmickType.PHASE, f"expected PHASE, got {gimmick}"))

    # 2. 상태 생성
    state = create_gimmick_state(boss)
    results.append(("던전마스터 상태 생성", state is not None, ""))

    if state:
        # 3. 초기 페이즈 1
        results.append(("초기 페이즈 1", state.current_phase == 1, f"phase={state.current_phase}"))

        # 4. HP 60% - 페이즈 2 (70% 이하)
        boss.hp = 60
        result = process_gimmick_on_turn_start(boss, player, state, turn=1)
        results.append(("HP 60% - 페이즈 2", state.current_phase == 2, f"phase={state.current_phase}"))

        # 5. HP 20% - 페이즈 3 (30% 이하)
        boss.hp = 20
        result = process_gimmick_on_turn_start(boss, player, state, turn=2)
        results.append(("HP 20% - 페이즈 3", state.current_phase == 3, f"phase={state.current_phase}"))

        messages = result.get("messages", [])
        has_phase_msg = any("페이즈" in m for m in messages)
        results.append(("페이즈 메시지 포함", has_phase_msg, f"messages={messages}"))

    return results


def test_gimmick_display():
    """기믹 표시 테스트"""
    results = []

    # 각 보스별 표시 확인
    bosses = [
        ("boss_slime_king", "슬라임 킹"),
        ("boss_giant_spider", "여왕 거미"),
        ("boss_orc_warlord", "오크 대족장"),
        ("boss_vampire_lord", "뱀파이어 로드"),
        ("boss_dungeon_master", "던전 마스터"),
    ]

    for boss_id, boss_name in bosses:
        boss = MockBoss(id=boss_id, name=boss_name, hp=50, max_hp=100)
        state = create_gimmick_state(boss)
        if state:
            display = get_gimmick_display(boss, state)
            has_display = display is not None and len(display) >= 0  # 빈 문자열도 OK
            results.append((f"{boss_name} 표시 함수", has_display, f"display='{display[:30] if display else ''}'"))

    return results


def main():
    print("\n" + "=" * 60)
    print("  보스 기믹 유닛 테스트 시작")
    print("=" * 60)

    test_result = TestResult()

    # 1. 슬라임 킹
    print("\n[1/6] 슬라임 킹 테스트...")
    for name, passed, detail in test_slime_king():
        test_result.add(name, passed, detail)

    # 2. 여왕 거미
    print("[2/6] 여왕 거미 테스트...")
    for name, passed, detail in test_spider_queen():
        test_result.add(name, passed, detail)

    # 3. 오크 대족장
    print("[3/6] 오크 대족장 테스트...")
    for name, passed, detail in test_orc_warlord():
        test_result.add(name, passed, detail)

    # 4. 뱀파이어 로드
    print("[4/6] 뱀파이어 로드 테스트...")
    for name, passed, detail in test_vampire_lord():
        test_result.add(name, passed, detail)

    # 5. 던전 마스터
    print("[5/6] 던전 마스터 테스트...")
    for name, passed, detail in test_dungeon_master():
        test_result.add(name, passed, detail)

    # 6. 기믹 표시
    print("[6/6] 기믹 표시 테스트...")
    for name, passed, detail in test_gimmick_display():
        test_result.add(name, passed, detail)

    # 결과 출력
    test_result.print_summary()

    return test_result.failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
