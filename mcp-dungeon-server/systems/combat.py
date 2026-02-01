"""전투 시스템"""
import random
from typing import TYPE_CHECKING

# v6.6: 게임 설정은 config.py에서 import (중복 제거)
from config import GameConfig

# v6.6: 순환 참조 방지를 위한 TYPE_CHECKING 사용
if TYPE_CHECKING:
    from models.player import Player
    from models.monster import Monster


def calculate_damage(
    attacker_atk: int,
    defender_def: int,
    is_critical: bool = False,
    damage_mult: float = 1.0,
    flat_bonus: int = 0
) -> int:
    """
    데미지 계산

    공식: max(1, (ATK - DEF) * mult + flat) * crit_mult

    Args:
        attacker_atk: 공격자 공격력
        defender_def: 방어자 방어력
        is_critical: 크리티컬 여부
        damage_mult: 데미지 배율 (스킬 등)
        flat_bonus: 고정 추가 데미지

    Returns:
        최종 데미지 (최소 1)
    """
    base_damage = attacker_atk - defender_def
    damage = int(base_damage * damage_mult) + flat_bonus
    damage = max(GameConfig.MIN_DAMAGE, damage)

    if is_critical:
        damage = int(damage * GameConfig.CRITICAL_MULTIPLIER)

    return damage


def check_critical(crit_chance: float = 0.15) -> bool:
    """크리티컬 판정"""
    return random.random() < crit_chance


def process_player_attack(
    player: "Player",
    enemy: "Monster",
    defending: bool = False
) -> dict:
    """
    플레이어 공격 처리

    Returns:
        {
            "damage": int,
            "is_critical": bool,
            "enemy_killed": bool,
        }
    """
    is_critical = check_critical(player.crit_chance)
    damage = calculate_damage(player.atk, enemy.def_, is_critical)

    enemy.take_damage(damage)

    return {
        "damage": damage,
        "is_critical": is_critical,
        "enemy_killed": not enemy.is_alive,
    }


def process_enemy_attack(
    enemy: "Monster",
    player: "Player",
    player_defending: bool = False,
    enemy_status: object = None,
) -> dict:
    """
    적 공격 처리

    Returns:
        {
            "damage": int,
            "player_killed": bool,
        }
    """
    # 상태이상에 의한 공격력 수정
    effective_atk = enemy.atk
    if enemy_status:
        effective_atk = int(enemy.atk * enemy_status.get_atk_modifier())

    damage = calculate_damage(effective_atk, player.def_)

    # 방어 중이면 데미지 절반
    if player_defending:
        damage = int(damage * GameConfig.DEFENSE_REDUCTION)
        damage = max(GameConfig.MIN_DAMAGE, damage)

    player.take_damage(damage)

    return {
        "damage": damage,
        "player_killed": not player.is_alive,
    }


def calculate_flee_chance(player: "Player", enemy: "Monster") -> int:
    """
    도망 성공률 계산

    공식: 50% + (민첩차이 * 2%) + HP보정
    범위: 30~80%

    Args:
        player: 플레이어
        enemy: 적 몬스터

    Returns:
        도망 성공 확률 (%)
    """
    # 보스전 도망 불가
    if enemy.is_boss:
        return 0

    base_chance = GameConfig.FLEE_BASE_CHANCE

    # 민첩 차이 (간단히 레벨 기반)
    agi_diff = player.level - (enemy.exp // 20)  # 경험치 기반 레벨 추정
    agi_bonus = agi_diff * 2

    # HP 비율 보정 (HP 낮을수록 도망 확률 증가)
    hp_ratio = player.hp / player.max_hp
    hp_bonus = int((1 - hp_ratio) * 10)

    flee_chance = base_chance + agi_bonus + hp_bonus

    # 엘리트면 -10%
    if enemy.is_elite:
        flee_chance -= 10

    # 범위 제한
    return max(GameConfig.FLEE_MIN_CHANCE, min(GameConfig.FLEE_MAX_CHANCE, flee_chance))


def attempt_flee(player: "Player", enemy: "Monster") -> tuple[bool, int]:
    """
    도망 시도

    Returns:
        (성공여부, 성공확률)
    """
    chance = calculate_flee_chance(player, enemy)

    if chance == 0:
        return False, 0

    success = random.randint(1, 100) <= chance
    return success, chance
