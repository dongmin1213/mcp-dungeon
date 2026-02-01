"""적 AI 시스템 (v5.0 행동 예고제)"""
import random
from models.monster import Monster, EnemyAction, ACTION_ICONS, ACTION_NAMES


def determine_next_action(monster: Monster, turn: int, player_hp_ratio: float = 1.0) -> EnemyAction:
    """
    적의 다음 행동 결정

    Args:
        monster: 몬스터 객체
        turn: 현재 전투 턴
        player_hp_ratio: 플레이어 HP 비율 (0~1)

    Returns:
        다음 행동 (EnemyAction)
    """
    # 충전 상태면 무조건 강타
    if monster.charged:
        monster.charged = False
        return EnemyAction.HEAVY

    # HP 낮으면 회복 우선
    hp_ratio = monster.hp / monster.max_hp
    if hp_ratio < 0.3 and random.random() < 0.4:
        # 30% 확률로 회복 시도 (회복 능력 있으면)
        if "heal" in (monster.action_pattern or []):
            return EnemyAction.HEAL

    # v6.7.2: 플레이어 HP가 낮으면 공격적으로 전환
    if player_hp_ratio < 0.3:
        # 플레이어가 빈사 상태면 강타 확률 증가
        if random.random() < 0.5:
            return EnemyAction.HEAVY

    # 엘리트/보스는 특수 행동 패턴 사용
    if monster.is_boss or monster.is_elite:
        return _get_pattern_action(monster, turn)

    # 일반 몬스터는 간단한 패턴
    return _get_simple_action(monster, turn)


def _get_pattern_action(monster: Monster, turn: int) -> EnemyAction:
    """패턴 기반 행동 선택 (엘리트/보스)"""
    if not monster.action_pattern:
        return EnemyAction.ATTACK

    # 턴 기반 패턴 순환
    pattern_index = (turn - 1) % len(monster.action_pattern)
    action_str = monster.action_pattern[pattern_index]

    try:
        action = EnemyAction(action_str)
    except ValueError:
        action = EnemyAction.ATTACK

    # 충전 행동이면 상태 설정
    if action == EnemyAction.CHARGE:
        monster.charged = True

    return action


def _get_simple_action(monster: Monster, turn: int) -> EnemyAction:
    """간단한 행동 선택 (일반 몬스터)"""
    # 기본 가중치
    weights = {
        EnemyAction.ATTACK: 60,
        EnemyAction.HEAVY: 20,
        EnemyAction.DEFEND: 15,
        EnemyAction.BUFF: 5,
    }

    # 패턴이 있으면 패턴 기반
    if monster.action_pattern:
        pattern_index = (turn - 1) % len(monster.action_pattern)
        action_str = monster.action_pattern[pattern_index]
        try:
            return EnemyAction(action_str)
        except ValueError:
            pass

    # 가중치 기반 랜덤
    actions = list(weights.keys())
    action_weights = list(weights.values())
    return random.choices(actions, weights=action_weights, k=1)[0]


def get_action_damage(monster: Monster, action: EnemyAction) -> int:
    """행동별 예상 데미지 계산"""
    base_atk = monster.atk

    if action == EnemyAction.ATTACK:
        return base_atk
    elif action == EnemyAction.HEAVY:
        return int(base_atk * 1.8)  # 강타: 180% 데미지
    elif action == EnemyAction.CHARGE:
        return 0  # 충전: 데미지 없음
    elif action == EnemyAction.DEFEND:
        return 0  # 방어: 데미지 없음
    elif action == EnemyAction.HEAL:
        return 0  # 회복: 데미지 없음
    elif action == EnemyAction.BUFF:
        return 0  # 버프: 데미지 없음
    elif action == EnemyAction.DEBUFF:
        return int(base_atk * 0.5)  # 디버프: 약한 데미지
    elif action == EnemyAction.SPECIAL:
        return int(base_atk * 1.5)  # 특수: 150% 데미지
    else:
        return base_atk


def get_action_description(action: EnemyAction, damage: int = 0) -> str:
    """행동 설명 텍스트 생성"""
    icon = ACTION_ICONS.get(action, "❓")
    name = ACTION_NAMES.get(action, "알 수 없음")

    if action == EnemyAction.ATTACK:
        return f"{icon} {name} (예상 데미지: {damage})"
    elif action == EnemyAction.HEAVY:
        return f"{icon} {name}! (예상 데미지: {damage}) ⚠️ 위험!"
    elif action == EnemyAction.CHARGE:
        return f"{icon} {name} 중... (다음 턴 강타!)"
    elif action == EnemyAction.DEFEND:
        return f"{icon} {name} 자세 (데미지 감소)"
    elif action == EnemyAction.HEAL:
        return f"{icon} {name} 준비 (HP 회복)"
    elif action == EnemyAction.BUFF:
        return f"{icon} {name} 준비 (능력 강화)"
    elif action == EnemyAction.DEBUFF:
        return f"{icon} {name} 준비 (플레이어 약화)"
    elif action == EnemyAction.SPECIAL:
        return f"{icon} 특수 공격! (예상 데미지: {damage}) ⭐"
    else:
        return f"{icon} 준비 중..."


def execute_enemy_action(
    monster: Monster,
    action: EnemyAction,
    player,
    player_defending: bool = False
) -> dict:
    """
    적 행동 실행

    Returns:
        {
            "damage": int,          # 가한 데미지
            "healed": int,          # 회복량
            "message": str,         # 행동 메시지
            "player_debuff": str,   # 플레이어에게 건 디버프
            "self_buff": str,       # 자신에게 건 버프
        }
    """
    result = {
        "damage": 0,
        "healed": 0,
        "message": "",
        "player_debuff": None,
        "self_buff": None,
    }

    base_damage = get_action_damage(monster, action)
    icon = ACTION_ICONS.get(action, "❓")

    if action == EnemyAction.ATTACK:
        damage = max(1, base_damage - player.def_)
        if player_defending:
            damage = max(1, damage // 2)
        player.take_damage(damage)
        result["damage"] = damage
        result["message"] = f"{icon} {monster.name}의 공격! {damage} 데미지!"

    elif action == EnemyAction.HEAVY:
        damage = max(1, base_damage - player.def_)
        if player_defending:
            damage = max(1, damage // 2)
            result["message"] = f"{icon} {monster.name}의 강타! {damage} 데미지! (방어로 감소)"
        else:
            result["message"] = f"{icon} {monster.name}의 강타! {damage} 데미지! 💥"
        player.take_damage(damage)
        result["damage"] = damage

    elif action == EnemyAction.CHARGE:
        monster.charged = True
        result["message"] = f"{icon} {monster.name}이(가) 힘을 모으고 있다... (다음 턴 강타!)"

    elif action == EnemyAction.DEFEND:
        result["self_buff"] = "defend"
        result["message"] = f"{icon} {monster.name}이(가) 방어 자세를 취했다!"

    elif action == EnemyAction.HEAL:
        heal_amount = int(monster.max_hp * 0.2)  # 최대 HP의 20% 회복
        monster.hp = min(monster.max_hp, monster.hp + heal_amount)
        result["healed"] = heal_amount
        result["message"] = f"{icon} {monster.name}이(가) {heal_amount} HP를 회복했다!"

    elif action == EnemyAction.BUFF:
        result["self_buff"] = "attack_up"
        result["message"] = f"{icon} {monster.name}이(가) 자신을 강화했다! (ATK +20%)"
        monster.atk = int(monster.atk * 1.2)

    elif action == EnemyAction.DEBUFF:
        damage = max(1, base_damage - player.def_)
        if player_defending:
            damage = max(1, damage // 2)
        player.take_damage(damage)
        result["damage"] = damage
        result["player_debuff"] = "defense_down"
        result["message"] = f"{icon} {monster.name}의 저주! {damage} 데미지 + 방어력 감소!"

    elif action == EnemyAction.SPECIAL:
        damage = max(1, base_damage - player.def_)
        if player_defending:
            damage = max(1, damage // 2)
        player.take_damage(damage)
        result["damage"] = damage
        result["message"] = f"{icon} {monster.name}의 특수 공격! {damage} 데미지! ⭐"

    return result


# 기본 행동 패턴 템플릿
DEFAULT_PATTERNS = {
    # 일반 몬스터: 공격 위주
    "normal_basic": ["attack", "attack", "attack"],
    "normal_aggressive": ["attack", "attack", "heavy"],
    "normal_defensive": ["attack", "defend", "attack"],

    # 엘리트: 다양한 패턴
    "elite_charger": ["attack", "charge", "heavy", "defend"],
    "elite_buffer": ["buff", "attack", "attack", "heavy"],
    "elite_debuffer": ["attack", "debuff", "attack", "attack"],

    # 보스: 복잡한 패턴
    "boss_balanced": ["attack", "attack", "charge", "heavy", "defend", "heal"],
    "boss_aggressive": ["attack", "buff", "attack", "charge", "heavy", "heavy"],
    "boss_tactical": ["debuff", "attack", "attack", "charge", "heavy", "heal"],
}
