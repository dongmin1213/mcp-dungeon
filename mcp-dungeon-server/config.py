"""게임 설정 값"""
from pathlib import Path

# 경로 설정
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "db" / "game.db"

# 직업 데이터는 seeds/classes.py에서 import (Single Source of Truth)
from seeds.classes import CLASS_STATS, CLASS_NAMES, DEFAULT_UNLOCKED_CLASSES

# 게임 밸런스 상수
class GameConfig:
    # 데미지 계산
    MIN_DAMAGE = 1
    CRITICAL_MULTIPLIER = 1.5
    DEFENSE_REDUCTION = 0.5  # 방어 시 데미지 50% 감소

    # 도망 확률
    FLEE_BASE_CHANCE = 50
    FLEE_MIN_CHANCE = 30
    FLEE_MAX_CHANCE = 80

    # 레벨업
    EXP_PER_LEVEL = 100  # 필요 경험치 = 레벨 * 100
    LEVEL_UP_HP = 10
    LEVEL_UP_MP = 5
    LEVEL_UP_ATK = 2
    LEVEL_UP_DEF = 1

    # 인벤토리
    MAX_INVENTORY_SIZE = 20
    MAX_GOLD = 99999

    # 던전 구조 (v4.0 개편: 10층 → 5층)
    MAX_FLOOR = 5
    BOSS_FLOORS = [1, 2, 3, 4, 5]  # 매 층 보스 등장 (50% 확률, 5층은 100%)

    # 엘리트 출현율 (v4.0: 10% → 25%)
    ELITE_SPAWN_RATE = 0.25

    # 함정 데미지 배율 (v4.0: 1.0 → 1.5)
    TRAP_DAMAGE_MULTIPLIER = 1.5

# CLASS_STATS, CLASS_NAMES는 seeds/classes.py에서 import됨 (위 참조)

# 맵 크기 (층별) - v4.0: 5층 구조
MAP_SIZES = {
    1: (4, 4),   # 하수도
    2: (4, 5),   # 지하 감옥
    3: (5, 5),   # 마석 광산
    4: (5, 5),   # 심연의 사원
    5: (6, 5),   # 최종 심층부
}

# 층별 목표 방 개수 - v4.0: 5층 구조
ROOM_COUNTS = {
    1: (8, 10),   # 하수도: 간결한 입문
    2: (10, 12),  # 지하 감옥
    3: (12, 15),  # 마석 광산
    4: (14, 17),  # 심연의 사원
    5: (16, 20),  # 최종 심층부
}

# 이벤트 확률 - v4.0: 몬스터↑, 보물↓
EVENT_RATIOS = {
    "monster": 0.45,  # 40% → 45%
    "treasure": 0.12,  # 20% → 12% (보물 감소)
    "trap": 0.18,      # 15% → 18% (함정 증가)
    "shop": 0.10,
    "rest": 0.10,
    "mystery": 0.05,
}

# ====================================
# 밸런스 조정 설정
# ====================================

# 층별 권장 레벨 (밸런스 기준) - v4.0: 5층 구조
FLOOR_RECOMMENDED_LEVEL = {
    1: 1,   # 입문
    2: 3,   # 중반 진입
    3: 5,   # 중반
    4: 7,   # 후반 진입
    5: 9,   # 최종 보스
}

# 전투 밸런스 기준값
class BalanceConfig:
    """밸런스 조정을 위한 기준값"""

    # 일반 몬스터 전투 예상 턴 수
    NORMAL_COMBAT_TURNS = 3  # 일반 몬스터는 3턴 내 처치
    ELITE_COMBAT_TURNS = 6   # 엘리트는 6턴 내 처치
    BOSS_COMBAT_TURNS = 12   # 보스는 12턴 내 처치

    # 층당 예상 레벨 상승
    LEVELS_PER_FLOOR = 1.2

    # 적정 체감 난이도 (턴당 HP 손실 비율)
    NORMAL_HP_LOSS_RATIO = 0.08   # 일반 몬스터: 전투당 HP 8% 손실
    ELITE_HP_LOSS_RATIO = 0.20    # 엘리트: 전투당 HP 20% 손실
    BOSS_HP_LOSS_RATIO = 0.50     # 보스: 전투당 HP 50% 손실

    # 드롭률 조정 배율
    DROP_RATE_MULT = {
        "normal": 1.0,
        "elite": 1.5,
        "boss": 2.0,
    }

    # 보상 배율 (행운 스탯 기준)
    LUCK_BONUS_PER_POINT = 0.02  # 행운 1당 드롭률 2% 증가

    # 경험치 밸런스 (층별 필요 전투 수)
    COMBATS_TO_LEVEL_UP = 4  # 4번 전투당 1레벨 상승 목표

    # 골드 밸런스
    SHOP_VISITS_PER_FLOOR = 1.5  # 층당 평균 1.5회 상점 방문 예상
    GOLD_SURPLUS_RATIO = 1.2     # 상점 가격 대비 1.2배 골드 획득

# 클리어율 목표
CLEAR_RATE_TARGETS = {
    "first_play": (0.05, 0.10),   # 첫 플레이: 5~10%
    "experienced": (0.25, 0.35),  # 숙련자: 25~35%
}

# ====================================
# v5.0 자원 긴장감 시스템
# ====================================

class ResourceConfig:
    """v5.0 자원 긴장감 설정"""

    # C1: 휴식처 제한
    REST_LIMIT_PER_FLOOR = 1  # 층당 최대 휴식 횟수

    # C2: 포션 슬롯 제한
    MAX_POTION_SLOTS = 3  # 포션 전용 슬롯 개수

    # C3: 회복량 조정 (기존 대비)
    REST_HEAL_PERCENT = 0.25       # 30% → 25%
    HP_POTION_S_HEAL = 25          # 30 → 25
    HP_POTION_M_HEAL = 50          # 60 → 50
    HP_POTION_L_HEAL = 100         # 120 → 100
    MP_POTION_S_HEAL = 15          # 20 → 15
    MP_POTION_M_HEAL = 35          # 40 → 35

    # 포션 ID 목록
    POTION_IDS = [
        "hp_potion_s", "hp_potion_m", "hp_potion_l",
        "mp_potion_s", "mp_potion_m", "elixir",
        "antidote"
    ]

# 난이도별 배율
DIFFICULTY_MULTIPLIERS = {
    "easy": {
        "monster_hp": 0.8,
        "monster_atk": 0.8,
        "monster_def": 0.8,
        "exp_mult": 0.8,
        "gold_mult": 1.2,
    },
    "normal": {
        "monster_hp": 1.0,
        "monster_atk": 1.0,
        "monster_def": 1.0,
        "exp_mult": 1.0,
        "gold_mult": 1.0,
    },
    "hard": {
        "monster_hp": 1.3,
        "monster_atk": 1.3,
        "monster_def": 1.2,
        "exp_mult": 1.3,
        "gold_mult": 0.9,
    },
    "hell": {
        "monster_hp": 1.6,
        "monster_atk": 1.5,
        "monster_def": 1.4,
        "exp_mult": 1.5,
        "gold_mult": 0.8,
    },
}
