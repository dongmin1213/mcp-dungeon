"""v5.0 콤보 시스템 (Phase 1B: 콤보 체인 + 궁극기)"""
from typing import Any, Optional

# ============================================================
# 콤보 정의
# 연속으로 특정 스킬을 사용하면 보너스 효과 발동
# ============================================================
COMBOS = {
    # ===== 마법사 콤보 =====
    "fire_storm": {
        "name": "화염 폭풍",
        "icon": "🔥🔥",
        "sequence": ["fireball", "fireball"],  # 파이어볼 2연속
        "effect": {"damage_mult": 1.5},  # 2번째 150% 데미지
        "message": "🔥🔥 화염 폭풍! 콤보 발동!",
    },
    "ice_fire": {
        "name": "증기 폭발",
        "icon": "💨",
        "sequence": ["fireball", "ice_lance"],  # 파이어볼 → 얼음창
        "effect": {"bonus_damage": 20, "stun_chance": 0.5},
        "message": "💨 증기 폭발! 추가 데미지 + 기절 확률!",
    },
    "absolute_zero": {
        "name": "절대 영도",
        "icon": "🧊🧊",
        "sequence": ["ice_lance", "ice_lance"],  # 얼음창 2연속
        "effect": {"freeze_guaranteed": True},  # 확정 빙결
        "message": "🧊🧊 절대 영도! 확정 빙결!",
    },

    # ===== 전사 콤보 =====
    "double_strike": {
        "name": "연속 강타",
        "icon": "⚔️⚔️",
        "sequence": ["power_strike", "power_strike"],
        "effect": {"damage_mult": 1.3},  # 2번째 130%
        "message": "⚔️⚔️ 연속 강타! 콤보 발동!",
    },
    "war_combo": {
        "name": "전사의 분노",
        "icon": "💪⚔️",
        "sequence": ["war_cry", "power_strike"],  # 버프 → 공격
        "effect": {"damage_mult": 1.5, "guaranteed_crit": True},
        "message": "💪⚔️ 전사의 분노! 강화된 크리티컬!",
    },

    # ===== 궁수 콤보 =====
    "arrow_rain": {
        "name": "화살비",
        "icon": "🏹🏹",
        "sequence": ["multi_shot", "multi_shot"],
        "effect": {"hits_bonus": 2},  # 추가 2회 공격
        "message": "🏹🏹 화살비! 추가 공격!",
    },
    "sniper": {
        "name": "저격수",
        "icon": "🎯🎯",
        "sequence": ["precise_shot", "precise_shot"],
        "effect": {"damage_mult": 1.8},  # 2번째 180%
        "message": "🎯🎯 저격수! 치명적인 정밀 사격!",
    },

    # ===== 도적 콤보 =====
    "poison_master": {
        "name": "독 전문가",
        "icon": "🟢🟢🟢",
        "sequence": ["poison_blade", "poison_blade", "poison_blade"],  # 3연속 독
        "effect": {"execute_threshold": 0.2},  # HP 20% 이하 즉사
        "message": "🟢🟢🟢 독살! HP 20% 이하 즉사!",
    },
    "assassin": {
        "name": "암살자",
        "icon": "🗡️💀",
        "sequence": ["shadow_step", "backstab"],  # 그림자 걸음 → 백스탭
        "effect": {"damage_mult": 2.5},  # 250% 데미지
        "message": "🗡️💀 암살! 치명적 일격!",
    },

    # ===== 성기사 콤보 =====
    "divine_wrath": {
        "name": "신의 분노",
        "icon": "✨✨",
        "sequence": ["holy_strike", "smite"],
        "effect": {"damage_mult": 1.5, "heal_percent": 0.1},
        "message": "✨✨ 신의 분노! 데미지 + 회복!",
    },

    # ===== 사신 콤보 =====
    "death_combo": {
        "name": "죽음의 연쇄",
        "icon": "💀💀",
        "sequence": ["death_mark", "soul_reap"],
        "effect": {"lifesteal_bonus": 0.3},  # 추가 30% 흡혈
        "message": "💀💀 죽음의 연쇄! 강화된 흡혈!",
    },
    "reaper_combo": {
        "name": "사신의 완성",
        "icon": "💀⚰️",
        "sequence": ["death_mark", "grim_harvest"],
        "effect": {"execute_threshold_bonus": 0.1},  # 즉사 조건 +10%
        "message": "💀⚰️ 사신의 완성! 즉사 조건 완화!",
    },
}

# ============================================================
# Phase 1B: 콤보 체인 보상 (연속 콤보 시)
# ============================================================
COMBO_CHAIN_REWARDS = {
    1: {  # 첫 콤보
        "message": "🔗 콤보 1회!",
        "reward_type": "damage",  # 데미지 배율
        "value": 1.0,  # 기본 (추가 보너스 없음)
    },
    2: {  # 2연속 콤보
        "message": "🔗🔗 콤보 2연속! MP 전회복!",
        "reward_type": "mp_restore",  # MP 회복
        "value": 1.0,  # 100% 회복
    },
    3: {  # 3연속 콤보
        "message": "🔗🔗🔗 콤보 3연속! 궁극기 게이지 충전!",
        "reward_type": "ultimate",  # 궁극기 충전
        "value": 1.0,  # 게이지 완충
    },
}

# 궁극기 효과 (전체 적 현재 HP 50% 데미지)
ULTIMATE_SKILL = {
    "name": "궁극기: 멸절의 일격",
    "icon": "⚡💥",
    "damage_ratio": 0.5,  # 적 현재 HP의 50%
    "message": "⚡💥 궁극기 발동! 멸절의 일격!",
}


def check_combo(skill_history: list[str]) -> Optional[dict]:
    """
    스킬 기록에서 콤보 체크

    Args:
        skill_history: 최근 사용한 스킬 ID 리스트

    Returns:
        콤보 데이터 or None
    """
    if not skill_history:
        return None

    # 긴 콤보부터 체크 (3연속 → 2연속)
    for combo_id, combo in sorted(
        COMBOS.items(),
        key=lambda x: len(x[1]["sequence"]),
        reverse=True
    ):
        sequence = combo["sequence"]
        seq_len = len(sequence)

        if len(skill_history) >= seq_len:
            # 마지막 N개 스킬이 시퀀스와 일치하는지 확인
            recent = skill_history[-seq_len:]
            if recent == sequence:
                return {
                    "id": combo_id,
                    **combo
                }

    return None


def apply_combo_effect(
    combo: dict,
    base_damage: int,
    player: Any,
    enemy: Any,
) -> tuple[int, list[str]]:
    """
    콤보 효과 적용

    Args:
        combo: 콤보 데이터
        base_damage: 기본 데미지
        player: 플레이어
        enemy: 적

    Returns:
        (최종 데미지, 추가 메시지 리스트)
    """
    effect = combo.get("effect", {})
    messages = [combo["message"]]
    damage = base_damage

    # 데미지 배율
    if "damage_mult" in effect:
        damage = int(damage * effect["damage_mult"])

    # 추가 데미지
    if "bonus_damage" in effect:
        damage += effect["bonus_damage"]

    # 확정 빙결
    if effect.get("freeze_guaranteed"):
        from models.status_effect import StatusEffect, StatusType
        # enemy_status에 빙결 추가 필요 (외부에서 처리)
        messages.append("🧊 확정 빙결!")

    # 즉사 체크
    if "execute_threshold" in effect:
        threshold = effect["execute_threshold"]
        if enemy.hp / enemy.max_hp <= threshold:
            enemy.hp = 0
            messages.append(f"💀 즉사! (HP {int(threshold * 100)}% 이하)")

    # 회복
    if "heal_percent" in effect:
        heal = int(player.max_hp * effect["heal_percent"])
        player.heal(heal)
        messages.append(f"💚 HP +{heal} 회복")

    return damage, messages


# ============================================================
# Phase 1B: 콤보 체인 시스템
# ============================================================

class ComboChainManager:
    """콤보 체인 관리자"""

    def __init__(self):
        self.chain_count: int = 0  # 연속 콤보 횟수
        self.ultimate_gauge: float = 0.0  # 궁극기 게이지 (0.0 ~ 1.0)
        self.ultimate_ready: bool = False  # 궁극기 사용 가능 여부

    def on_combo_success(self, player: Any) -> tuple[str, Optional[dict]]:
        """
        콤보 성공 시 호출

        Returns:
            (보상 메시지, 보상 데이터)
        """
        self.chain_count += 1

        # 연속 콤보 보상 확인
        reward = COMBO_CHAIN_REWARDS.get(self.chain_count)
        if not reward:
            # 최대 콤보 초과 시 3회 보상 반복
            reward = COMBO_CHAIN_REWARDS[3]

        message = reward["message"]
        reward_data = {"type": reward["reward_type"], "value": reward["value"]}

        # 보상 즉시 적용
        if reward["reward_type"] == "mp_restore":
            # MP 전회복
            restored = player.max_mp - player.mp
            player.mp = player.max_mp
            message += f" (MP +{restored})"
            reward_data["restored"] = restored

        elif reward["reward_type"] == "ultimate":
            # 궁극기 게이지 충전
            self.ultimate_gauge = 1.0
            self.ultimate_ready = True
            message += " 💥 궁극기 준비 완료!"

        return message, reward_data

    def on_combo_fail(self) -> None:
        """콤보 실패 (콤보가 안 터졌을 때)"""
        self.chain_count = 0  # 연속 콤보 초기화

    def use_ultimate(self, player: Any, enemy: Any) -> tuple[int, str]:
        """
        궁극기 사용

        Returns:
            (데미지, 메시지)
        """
        if not self.ultimate_ready:
            return 0, "❌ 궁극기가 준비되지 않았습니다."

        # 적 현재 HP의 50% 데미지
        damage = int(enemy.hp * ULTIMATE_SKILL["damage_ratio"])
        damage = max(1, damage)  # 최소 1 데미지

        enemy.take_damage(damage)

        # 궁극기 소모
        self.ultimate_gauge = 0.0
        self.ultimate_ready = False
        self.chain_count = 0  # 연속 콤보도 초기화

        message = f"{ULTIMATE_SKILL['message']} {enemy.name}에게 {damage} 데미지!"

        return damage, message

    def get_status_display(self) -> str:
        """상태 표시 문자열"""
        parts = []

        if self.chain_count > 0:
            parts.append(f"🔗 콤보 {self.chain_count}연속")

        if self.ultimate_ready:
            parts.append("💥 궁극기 준비!")
        elif self.ultimate_gauge > 0:
            gauge_percent = int(self.ultimate_gauge * 100)
            parts.append(f"⚡ 궁극기 {gauge_percent}%")

        return " | ".join(parts) if parts else ""

    def add_ultimate_gauge(self, amount: float) -> None:
        """궁극기 게이지 추가"""
        self.ultimate_gauge = min(1.0, self.ultimate_gauge + amount)
        if self.ultimate_gauge >= 1.0:
            self.ultimate_ready = True


def get_combo_hint(skill_history: list[str], player_skills: list[str]) -> Optional[str]:
    """
    가능한 콤보 힌트 반환

    Args:
        skill_history: 최근 스킬 기록
        player_skills: 플레이어 보유 스킬

    Returns:
        힌트 메시지 or None
    """
    if not skill_history:
        return None

    last_skill = skill_history[-1]

    # 마지막 스킬로 시작하는 콤보 찾기
    for combo_id, combo in COMBOS.items():
        sequence = combo["sequence"]
        if len(sequence) < 2:
            continue

        # 현재 진행 중인 콤보 체크
        for i in range(len(sequence) - 1):
            if sequence[i] == last_skill:
                next_skill = sequence[i + 1]
                # 플레이어가 다음 스킬을 보유하고 있는지 확인
                if next_skill in player_skills:
                    return f"💡 콤보 힌트: {combo['icon']} {combo['name']} - 다음: {next_skill}"

    return None


def clear_combo_history(skill_history: list[str], max_size: int = 5) -> list[str]:
    """스킬 기록 정리 (최대 크기 유지)"""
    if len(skill_history) > max_size:
        return skill_history[-max_size:]
    return skill_history


# ============================================================
# 헬퍼 함수
# ============================================================

def get_all_combo_info() -> str:
    """모든 콤보 정보 반환 (도움말용)"""
    lines = ["콤보 목록:"]

    for combo_id, combo in COMBOS.items():
        seq_str = " → ".join(combo["sequence"])
        lines.append(f"  {combo['icon']} {combo['name']}: {seq_str}")

    lines.append("")
    lines.append("콤보 체인 보상:")
    lines.append("  1연속: 기본 콤보 효과")
    lines.append("  2연속: MP 전회복")
    lines.append("  3연속: 궁극기 게이지 충전!")
    lines.append("")
    lines.append("궁극기: 멸절의 일격")
    lines.append("  적 현재 HP의 50% 데미지")

    return "\n".join(lines)
