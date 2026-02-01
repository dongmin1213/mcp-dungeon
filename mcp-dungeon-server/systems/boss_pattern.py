"""보스 패턴 시스템"""
import json
import random
from typing import Any, Optional
from models.status_effect import StatusEffect, StatusType, StatusManager
from systems.combat import calculate_damage


class BossPhase:
    """보스 페이즈 정보"""
    def __init__(self, phase_data: dict):
        self.hp_range = phase_data.get("hp_range", [0.0, 1.0])
        self.actions = phase_data.get("actions", [])
        self.buffs = phase_data.get("buffs", [])
        self.summons = phase_data.get("summons", [])
        self.countdown = phase_data.get("countdown", 0)

    def is_active(self, hp_ratio: float) -> bool:
        """현재 HP 비율에서 이 페이즈가 활성화되는지"""
        return self.hp_range[0] <= hp_ratio <= self.hp_range[1]


class BossPattern:
    """보스 패턴 관리"""

    def __init__(self, pattern_json: str):
        self.phases: dict[str, BossPhase] = {}
        self.current_phase: Optional[str] = None
        self.action_index: int = 0
        self.phase_buffs_applied: set[str] = set()
        self.countdown_active: bool = False
        self.countdown_turns: int = 0

        if pattern_json:
            try:
                pattern_data = json.loads(pattern_json)
                for phase_name, phase_data in pattern_data.items():
                    self.phases[phase_name] = BossPhase(phase_data)
            except json.JSONDecodeError:
                pass

    def get_current_phase(self, hp_ratio: float) -> Optional[str]:
        """현재 HP 비율에 맞는 페이즈 반환"""
        for phase_name, phase in self.phases.items():
            if phase.is_active(hp_ratio):
                return phase_name
        return None

    def update_phase(self, boss: Any) -> dict:
        """
        페이즈 업데이트 및 변경 시 효과 적용

        Returns:
            {
                "phase_changed": bool,
                "new_phase": str,
                "buffs_applied": list,
                "message": str
            }
        """
        result = {
            "phase_changed": False,
            "new_phase": "",
            "buffs_applied": [],
            "message": ""
        }

        hp_ratio = boss.hp / boss.max_hp
        new_phase = self.get_current_phase(hp_ratio)

        if new_phase and new_phase != self.current_phase:
            old_phase = self.current_phase
            self.current_phase = new_phase
            self.action_index = 0
            result["phase_changed"] = True
            result["new_phase"] = new_phase

            phase = self.phases[new_phase]

            # 페이즈 버프 적용
            if new_phase not in self.phase_buffs_applied:
                for buff in phase.buffs:
                    if "atk_mult" in buff:
                        boss.atk = int(boss.atk * buff["atk_mult"])
                        result["buffs_applied"].append(f"ATK ×{buff['atk_mult']}")
                    if "def_mult" in buff:
                        boss.def_ = int(boss.def_ * buff["def_mult"])
                        result["buffs_applied"].append(f"DEF ×{buff['def_mult']}")

                self.phase_buffs_applied.add(new_phase)

            # 카운트다운 시작
            if phase.countdown > 0 and not self.countdown_active:
                self.countdown_active = True
                self.countdown_turns = phase.countdown
                result["message"] = f"⚠️ {boss.name}이(가) 강력한 공격을 준비합니다! ({phase.countdown}턴)"

            # 페이즈 변경 메시지
            if old_phase:
                result["message"] = f"💢 {boss.name}의 패턴이 변했다!"

        return result

    def get_next_action(self, boss: Any) -> str:
        """다음 행동 결정"""
        if not self.current_phase or self.current_phase not in self.phases:
            return "attack"  # 기본 공격

        phase = self.phases[self.current_phase]
        if not phase.actions:
            return "attack"

        action = phase.actions[self.action_index]
        self.action_index = (self.action_index + 1) % len(phase.actions)

        return action

    def process_countdown(self, boss: Any, player: Any) -> dict:
        """
        카운트다운 처리

        Returns:
            {
                "countdown_damage": int,
                "message": str,
                "countdown_finished": bool
            }
        """
        result = {
            "countdown_damage": 0,
            "message": "",
            "countdown_finished": False
        }

        if not self.countdown_active:
            return result

        self.countdown_turns -= 1

        if self.countdown_turns <= 0:
            # 카운트다운 완료 - 강력한 공격
            self.countdown_active = False
            result["countdown_finished"] = True

            # 최대 HP의 30% 데미지
            damage = int(player.max_hp * 0.3)
            player.take_damage(damage)
            result["countdown_damage"] = damage
            result["message"] = f"💥 {boss.name}의 필살기! {damage} 데미지!"
        else:
            result["message"] = f"⚠️ {boss.name}의 공격까지 {self.countdown_turns}턴!"

        return result

    def get_summons(self) -> list[str]:
        """소환할 몬스터 ID 목록"""
        if not self.current_phase or self.current_phase not in self.phases:
            return []

        phase = self.phases[self.current_phase]
        return phase.summons


async def process_boss_action(
    boss: Any,
    player: Any,
    pattern: BossPattern,
    boss_status: StatusManager,
    player_status: StatusManager,
) -> dict:
    """
    보스 행동 처리

    Returns:
        {
            "action": str,
            "damage": int,
            "message": str,
            "effects_applied": list,
            "summons": list,
        }
    """
    result = {
        "action": "",
        "damage": 0,
        "message": "",
        "effects_applied": [],
        "summons": [],
    }

    # 페이즈 업데이트
    phase_result = pattern.update_phase(boss)
    if phase_result["phase_changed"]:
        result["message"] += phase_result["message"] + "\n"
        if phase_result["buffs_applied"]:
            result["message"] += f"  버프: {', '.join(phase_result['buffs_applied'])}\n"

    # 카운트다운 처리
    countdown_result = pattern.process_countdown(boss, player)
    if countdown_result["message"]:
        result["message"] += countdown_result["message"] + "\n"
    if countdown_result["countdown_damage"] > 0:
        result["damage"] += countdown_result["countdown_damage"]
        return result  # 카운트다운 데미지 후에는 추가 행동 안함

    # 다음 행동 결정
    action = pattern.get_next_action(boss)
    result["action"] = action

    # 행동 처리
    if action == "attack":
        damage = _boss_basic_attack(boss, player, boss_status)
        result["damage"] = damage
        result["message"] += f"🐺 {boss.name}의 공격! {damage} 데미지!"

    elif action.startswith("summon_"):
        # 소환
        summons = pattern.get_summons()
        result["summons"] = summons
        if summons:
            result["message"] += f"📢 {boss.name}이(가) 부하를 소환!"

    else:
        # 특수 스킬 사용 (DB에서 스킬 정보 조회해야 하지만, 간단히 처리)
        skill_result = await _process_boss_skill(
            boss, player, action, boss_status, player_status
        )
        result["damage"] = skill_result["damage"]
        result["message"] += skill_result["message"]
        result["effects_applied"] = skill_result["effects_applied"]

    return result


def _boss_basic_attack(boss: Any, player: Any, boss_status: StatusManager) -> int:
    """보스 기본 공격"""
    atk_modifier = boss_status.get_atk_modifier()
    effective_atk = int(boss.atk * atk_modifier)

    damage = calculate_damage(effective_atk, player.def_)
    player.take_damage(damage)

    return damage


async def _process_boss_skill(
    boss: Any,
    player: Any,
    skill_id: str,
    boss_status: StatusManager,
    player_status: StatusManager,
) -> dict:
    """보스 스킬 처리"""
    result = {
        "damage": 0,
        "message": "",
        "effects_applied": []
    }

    # 간단한 스킬 효과 처리 (하드코딩, 나중에 DB 연동 가능)
    skill_effects = {
        "slash": {"damage_mult": 1.2, "name": "베기"},
        "shield_up": {"buff": "def", "name": "방어 태세"},
        "charge": {"damage_mult": 1.8, "stun": True, "name": "돌진"},
        "scratch": {"damage_mult": 0.8, "hits": 2, "name": "할퀴기"},
        "bite": {"damage_mult": 1.3, "name": "물기"},
        "soul_devour": {"damage_mult": 1.5, "lifesteal": 0.3, "name": "영혼 흡수"},
        "fear_scream": {"debuff": "atk", "name": "공포의 비명"},
        "invisibility": {"buff": "evasion", "name": "투명화"},
        "slam": {"damage_mult": 1.8, "name": "내려찍기"},
        "hellfire": {"damage_mult": 2.0, "burn": True, "name": "지옥불"},
        "dark_pact": {"self_buff": True, "name": "어둠의 계약"},
        "death_strike": {"damage_mult": 2.5, "lifesteal": 0.3, "name": "죽음의 일격"},
        "unholy_aura": {"debuff": "def", "name": "불경한 오라"},
    }

    if skill_id not in skill_effects:
        # 알 수 없는 스킬 - 기본 공격
        damage = _boss_basic_attack(boss, player, boss_status)
        result["damage"] = damage
        result["message"] = f"🐺 {boss.name}의 공격! {damage} 데미지!"
        return result

    effect = skill_effects[skill_id]
    skill_name = effect.get("name", skill_id)

    # 데미지 스킬
    if "damage_mult" in effect:
        atk_modifier = boss_status.get_atk_modifier()
        effective_atk = int(boss.atk * atk_modifier)

        hits = effect.get("hits", 1)
        total_damage = 0

        for _ in range(hits):
            damage = calculate_damage(
                effective_atk,
                player.def_,
                damage_mult=effect["damage_mult"]
            )
            total_damage += damage

        player.take_damage(total_damage)
        result["damage"] = total_damage

        hit_text = f" ({hits}회)" if hits > 1 else ""
        result["message"] = f"⚡ {boss.name}의 {skill_name}!{hit_text} {total_damage} 데미지!"

        # 흡혈
        if effect.get("lifesteal"):
            heal = int(total_damage * effect["lifesteal"])
            boss.hp = min(boss.max_hp, boss.hp + heal)
            result["message"] += f" (HP +{heal})"

        # 기절
        if effect.get("stun"):
            player_status.add_effect(StatusEffect(
                type=StatusType.STUN,
                duration=1,
                source=skill_name
            ))
            result["effects_applied"].append("💫 기절!")

        # 화상
        if effect.get("burn"):
            player_status.add_effect(StatusEffect(
                type=StatusType.BURN,
                duration=3,
                value=boss.atk // 4,
                source=skill_name
            ))
            result["effects_applied"].append("🔥 화상!")

    # 버프 스킬
    elif effect.get("buff"):
        buff_type = effect["buff"]
        if buff_type == "def":
            boss_status.add_effect(StatusEffect(
                type=StatusType.DEF_UP,
                duration=2,
                value=0.5,
                source=skill_name
            ))
            result["message"] = f"✨ {boss.name}의 {skill_name}! 방어력 상승!"
        elif buff_type == "evasion":
            boss_status.add_effect(StatusEffect(
                type=StatusType.EVASION,
                duration=2,
                value=0.5,
                source=skill_name
            ))
            result["message"] = f"✨ {boss.name}의 {skill_name}! 회피율 상승!"

    # 셀프 버프 (HP 소모 + ATK 상승)
    elif effect.get("self_buff"):
        hp_cost = int(boss.hp * 0.2)
        boss.hp -= hp_cost
        boss_status.add_effect(StatusEffect(
            type=StatusType.ATK_UP,
            duration=3,
            value=0.5,
            source=skill_name
        ))
        result["message"] = f"💢 {boss.name}의 {skill_name}! HP -{hp_cost}, ATK 50% 상승!"

    # 디버프 스킬
    elif effect.get("debuff"):
        debuff_type = effect["debuff"]
        if debuff_type == "atk":
            player_status.add_effect(StatusEffect(
                type=StatusType.ATK_DOWN,
                duration=3,
                value=0.7,
                source=skill_name
            ))
            result["message"] = f"🌀 {boss.name}의 {skill_name}! 공격력 30% 감소!"
            result["effects_applied"].append("⬇️ ATK 감소")
        elif debuff_type == "def":
            player_status.add_effect(StatusEffect(
                type=StatusType.DEF_DOWN,
                duration=3,
                value=0.7,
                source=skill_name
            ))
            result["message"] = f"🌀 {boss.name}의 {skill_name}! 방어력 30% 감소!"
            result["effects_applied"].append("🔽 DEF 감소")

    return result
