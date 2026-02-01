"""Phase 4: 보스 기믹 시스템

각 보스별 고유 기믹:
1. 슬라임 킹 - 분열 (HP 30% 이하 시 미니 슬라임 소환)
2. 여왕 거미 - 거미줄 + 새끼 소환
3. 오크 대족장 - 분노 스택 + 광폭화
4. 뱀파이어 로드 - 흡혈 + 박쥐 변신
5. 던전 마스터 - 3페이즈 전환
"""
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class GimmickType(str, Enum):
    """보스 기믹 타입"""
    SPLIT = "split"           # 슬라임 킹 - 분열
    WEB = "web"               # 여왕 거미 - 거미줄
    RAGE = "rage"             # 오크 대족장 - 분노
    VAMPIRE = "vampire"       # 뱀파이어 로드 - 흡혈/변신
    PHASE = "phase"           # 던전 마스터 - 페이즈 전환


@dataclass
class BossGimmickState:
    """보스 기믹 상태 추적"""
    # 슬라임 킹
    split_triggered: bool = False
    mini_slimes_alive: int = 0

    # 여왕 거미
    web_cooldown: int = 0
    spider_babies_alive: int = 0
    max_spider_babies: int = 3

    # 오크 대족장
    rage_stacks: int = 0
    max_rage_stacks: int = 10
    enraged: bool = False

    # 뱀파이어 로드
    bat_form: bool = False
    bat_form_turns: int = 0

    # 던전 마스터
    current_phase: int = 1
    phase_weaknesses: dict = field(default_factory=lambda: {
        1: "fire",      # 마법사 페이즈
        2: "ice",       # 전사 페이즈
        3: None         # 최종 페이즈 (약점 없음)
    })


# 보스별 기믹 매핑
BOSS_GIMMICKS = {
    "boss_slime_king": GimmickType.SPLIT,
    "boss_rat_king": None,  # 기본 패턴만
    "boss_giant_spider": GimmickType.WEB,
    "boss_skeleton_general": None,  # 기본 패턴만
    "boss_orc_warlord": GimmickType.RAGE,
    "boss_crystal_guardian": None,  # 기본 패턴만
    "boss_vampire_lord": GimmickType.VAMPIRE,
    "boss_demon_lord": None,  # 기본 패턴만
    "boss_lich_king": None,  # 기본 패턴만
    "boss_dungeon_master": GimmickType.PHASE,
}


def get_boss_gimmick(boss_id: str) -> Optional[GimmickType]:
    """보스 ID로 기믹 타입 조회"""
    return BOSS_GIMMICKS.get(boss_id)


def create_gimmick_state(boss: Any) -> Optional[BossGimmickState]:
    """보스 기믹 상태 생성"""
    gimmick = get_boss_gimmick(boss.id)
    if not gimmick:
        return None
    return BossGimmickState()


def process_gimmick_on_turn_start(
    boss: Any,
    player: Any,
    state: BossGimmickState,
    turn: int
) -> dict:
    """
    턴 시작 시 기믹 처리

    Returns:
        {
            "messages": list[str],
            "player_stunned": bool,
            "boss_healed": int,
            "summons": list[str],
        }
    """
    result = {
        "messages": [],
        "player_stunned": False,
        "boss_healed": 0,
        "summons": [],
    }

    gimmick = get_boss_gimmick(boss.id)
    if not gimmick:
        return result

    hp_ratio = boss.hp / boss.max_hp

    # 슬라임 킹 - 분열
    if gimmick == GimmickType.SPLIT:
        result.update(_process_slime_king(boss, state, hp_ratio))

    # 여왕 거미 - 거미줄
    elif gimmick == GimmickType.WEB:
        result.update(_process_spider_queen(boss, player, state, turn))

    # 오크 대족장 - 광폭화 체크
    elif gimmick == GimmickType.RAGE:
        result.update(_process_orc_warlord_enrage(boss, state, hp_ratio))

    # 뱀파이어 로드 - 박쥐 변신
    elif gimmick == GimmickType.VAMPIRE:
        result.update(_process_vampire_lord(boss, player, state, hp_ratio))

    # 던전 마스터 - 페이즈 전환
    elif gimmick == GimmickType.PHASE:
        result.update(_process_dungeon_master(boss, state, hp_ratio))

    return result


def process_gimmick_on_hit(
    boss: Any,
    player: Any,
    state: BossGimmickState,
    damage: int
) -> dict:
    """
    보스 피격 시 기믹 처리 (오크 대족장 분노)

    Returns:
        {
            "messages": list[str],
            "atk_bonus": float,
        }
    """
    result = {
        "messages": [],
        "atk_bonus": 0.0,
    }

    gimmick = get_boss_gimmick(boss.id)
    if gimmick != GimmickType.RAGE:
        return result

    # 오크 대족장 분노 스택
    if not state.enraged and state.rage_stacks < state.max_rage_stacks:
        state.rage_stacks += 1
        atk_bonus = 0.05 * state.rage_stacks
        result["atk_bonus"] = atk_bonus
        result["messages"].append(
            f"  😤 {boss.name}의 분노! ATK +{int(atk_bonus * 100)}% ({state.rage_stacks}/{state.max_rage_stacks})"
        )

    return result


def process_gimmick_on_attack(
    boss: Any,
    player: Any,
    state: BossGimmickState,
    damage: int
) -> dict:
    """
    보스 공격 시 기믹 처리 (뱀파이어 흡혈)

    Returns:
        {
            "messages": list[str],
            "healed": int,
            "evasion_chance": float,
            "damage_mult": float,
        }
    """
    result = {
        "messages": [],
        "healed": 0,
        "evasion_chance": 0.0,
        "damage_mult": 1.0,
    }

    gimmick = get_boss_gimmick(boss.id)

    # 뱀파이어 로드 - 흡혈
    if gimmick == GimmickType.VAMPIRE and not state.bat_form:
        heal = int(damage * 0.5)
        old_hp = boss.hp
        boss.hp = min(boss.max_hp, boss.hp + heal)
        actual_heal = boss.hp - old_hp
        if actual_heal > 0:
            result["healed"] = actual_heal
            result["messages"].append(f"  🧛 {boss.name}의 흡혈! HP +{actual_heal}")

    # 뱀파이어 박쥐 변신 - 회피율
    if gimmick == GimmickType.VAMPIRE and state.bat_form:
        result["evasion_chance"] = 0.8

    # 오크 대족장 - 분노 보너스
    if gimmick == GimmickType.RAGE:
        if state.enraged:
            result["damage_mult"] = 2.0
        else:
            result["damage_mult"] = 1.0 + (0.05 * state.rage_stacks)

    # 던전 마스터 페이즈별 데미지
    if gimmick == GimmickType.PHASE:
        if state.current_phase == 3:  # 최종 페이즈
            result["damage_mult"] = 1.5

    return result


def get_boss_weakness(boss: Any, state: Optional[BossGimmickState]) -> Optional[str]:
    """
    현재 상태에 따른 보스 약점 반환 (던전 마스터용)
    """
    gimmick = get_boss_gimmick(boss.id)
    if gimmick != GimmickType.PHASE or not state:
        return None

    return state.phase_weaknesses.get(state.current_phase)


def on_minion_killed(state: BossGimmickState, minion_type: str) -> None:
    """소환물 처치 시 처리"""
    if minion_type == "mini_slime":
        state.mini_slimes_alive = max(0, state.mini_slimes_alive - 1)
    elif minion_type == "spider_baby":
        state.spider_babies_alive = max(0, state.spider_babies_alive - 1)


# ============================================================
# 개별 보스 기믹 처리 함수
# ============================================================

def _process_slime_king(boss: Any, state: BossGimmickState, hp_ratio: float) -> dict:
    """슬라임 킹 기믹: 분열"""
    result = {
        "messages": [],
        "summons": [],
        "boss_healed": 0,
    }

    # HP 30% 이하에서 분열 (1회만)
    if hp_ratio <= 0.3 and not state.split_triggered:
        state.split_triggered = True
        state.mini_slimes_alive = 2
        result["summons"] = ["mini_slime", "mini_slime"]
        result["messages"].append(
            f"  💧 {boss.name}이(가) 분열! 미니 슬라임 2마리 소환!"
        )
        result["messages"].append(
            "  ⚠️ 미니 슬라임이 살아있으면 본체가 매턴 HP 10% 회복!"
        )

    # 미니 슬라임이 살아있으면 본체 회복
    if state.mini_slimes_alive > 0:
        heal = int(boss.max_hp * 0.1)
        old_hp = boss.hp
        boss.hp = min(boss.max_hp, boss.hp + heal)
        actual_heal = boss.hp - old_hp
        if actual_heal > 0:
            result["boss_healed"] = actual_heal
            result["messages"].append(
                f"  💚 미니 슬라임 흡수! {boss.name} HP +{actual_heal}"
            )

    return result


def _process_spider_queen(
    boss: Any,
    player: Any,
    state: BossGimmickState,
    turn: int
) -> dict:
    """여왕 거미 기믹: 거미줄 + 새끼 소환"""
    result = {
        "messages": [],
        "player_stunned": False,
        "summons": [],
    }

    # 매 3턴마다 거미줄
    if turn > 1 and (turn - 1) % 3 == 0:
        result["player_stunned"] = True
        result["messages"].append(
            f"  🕸️ {boss.name}의 거미줄! 다음 턴 행동 불가!"
        )

    # 새끼 거미 소환 (최대 3마리)
    if state.spider_babies_alive < state.max_spider_babies and turn % 2 == 0:
        state.spider_babies_alive += 1
        result["summons"].append("spider_baby")
        result["messages"].append(
            f"  🕷️ 새끼 거미 소환! ({state.spider_babies_alive}/{state.max_spider_babies})"
        )

    return result


def _process_orc_warlord_enrage(
    boss: Any,
    state: BossGimmickState,
    hp_ratio: float
) -> dict:
    """오크 대족장 기믹: 광폭화 체크"""
    result = {
        "messages": [],
    }

    # HP 50% 이하에서 광폭화
    if hp_ratio <= 0.5 and not state.enraged:
        state.enraged = True
        # ATK 2배, DEF 0
        boss.atk = boss.atk * 2
        old_def = boss.def_
        boss.def_ = 0
        result["messages"].append(
            f"  😡 {boss.name} 광폭화! ATK x2, DEF 0!"
        )
        result["messages"].append(
            "  ⚠️ 강해졌지만 방어력이 없습니다!"
        )

    return result


def _process_vampire_lord(
    boss: Any,
    player: Any,
    state: BossGimmickState,
    hp_ratio: float
) -> dict:
    """뱀파이어 로드 기믹: 박쥐 변신"""
    result = {
        "messages": [],
    }

    # 박쥐 변신 중이면 턴 카운트 감소
    if state.bat_form:
        state.bat_form_turns -= 1
        if state.bat_form_turns <= 0:
            state.bat_form = False
            result["messages"].append(
                f"  🧛 {boss.name}이(가) 인간 형태로 돌아왔다!"
            )
        else:
            result["messages"].append(
                f"  🦇 박쥐 변신 중! (남은 턴: {state.bat_form_turns}) - 회피 80%"
            )
        return result

    # HP 30% 이하에서 박쥐 변신 (변신 중이 아닐 때만)
    if hp_ratio <= 0.3 and not state.bat_form:
        state.bat_form = True
        state.bat_form_turns = 3
        result["messages"].append(
            f"  🦇 {boss.name}이(가) 박쥐 떼로 변신! 3턴간 회피 80%!"
        )
        result["messages"].append(
            "  💡 TIP: 변신 해제까지 기다리거나 광역기를 사용하세요!"
        )

    return result


def _process_dungeon_master(
    boss: Any,
    state: BossGimmickState,
    hp_ratio: float
) -> dict:
    """던전 마스터 기믹: 3페이즈 전환"""
    result = {
        "messages": [],
    }

    old_phase = state.current_phase

    # 페이즈 전환
    if hp_ratio <= 0.3 and state.current_phase < 3:
        state.current_phase = 3
    elif hp_ratio <= 0.7 and state.current_phase < 2:
        state.current_phase = 2

    if state.current_phase != old_phase:
        phase_info = {
            1: ("마법사", "fire", "원거리 공격"),
            2: ("전사", "ice", "근접 강타"),
            3: ("최종", None, "모든 패턴 사용"),
        }
        name, weakness, style = phase_info[state.current_phase]

        result["messages"].append(
            f"  💢 {boss.name} 페이즈 {state.current_phase}! [{name}]"
        )
        result["messages"].append(f"     전투 스타일: {style}")

        if weakness:
            result["messages"].append(f"     💡 약점: {weakness}")
        else:
            result["messages"].append("     ⚠️ 약점 없음! 최종 페이즈!")

        # 페이즈별 버프
        if state.current_phase == 2:
            boss.atk = int(boss.atk * 1.3)
            boss.def_ = int(boss.def_ * 1.5)
            result["messages"].append("     ATK +30%, DEF +50%")
        elif state.current_phase == 3:
            boss.atk = int(boss.atk * 1.5)
            result["messages"].append("     ATK +50%, 모든 속성 저항!")

    return result


def get_gimmick_display(boss: Any, state: Optional[BossGimmickState]) -> str:
    """현재 기믹 상태 표시"""
    if not state:
        return ""

    gimmick = get_boss_gimmick(boss.id)
    if not gimmick:
        return ""

    lines = []

    if gimmick == GimmickType.SPLIT:
        if state.mini_slimes_alive > 0:
            lines.append(f"  💧 미니 슬라임: {state.mini_slimes_alive}마리")

    elif gimmick == GimmickType.WEB:
        if state.spider_babies_alive > 0:
            lines.append(f"  🕷️ 새끼 거미: {state.spider_babies_alive}/{state.max_spider_babies}")

    elif gimmick == GimmickType.RAGE:
        if state.enraged:
            lines.append("  😡 광폭화! (ATK x2, DEF 0)")
        elif state.rage_stacks > 0:
            lines.append(f"  😤 분노: {state.rage_stacks}/{state.max_rage_stacks}")

    elif gimmick == GimmickType.VAMPIRE:
        if state.bat_form:
            lines.append(f"  🦇 박쥐 변신 ({state.bat_form_turns}턴)")

    elif gimmick == GimmickType.PHASE:
        phase_names = {1: "마법사", 2: "전사", 3: "최종"}
        weakness = state.phase_weaknesses.get(state.current_phase, "없음")
        lines.append(f"  📍 페이즈 {state.current_phase}: {phase_names[state.current_phase]}")
        if weakness:
            lines.append(f"     약점: {weakness}")

    return "\n".join(lines) if lines else ""
