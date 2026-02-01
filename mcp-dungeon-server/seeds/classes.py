"""직업 시드 데이터 (Single Source of Truth)

이 파일은 직업 관련 데이터의 단일 진실 공급원(SSOT)입니다.
다른 파일에서 직업 데이터가 필요하면 이 파일에서 import하세요.

v6.6: 코드 중복 제거를 위해 CLASS_STATS, CLASS_NAMES 추가
"""
import json

# ============================================================
# 빠른 조회용 딕셔너리 (config.py, models/player.py에서 사용)
# ============================================================

CLASS_STATS: dict[str, dict[str, int]] = {
    "warrior": {"hp": 120, "mp": 30, "atk": 12, "def_": 8},
    "archer": {"hp": 90, "mp": 50, "atk": 14, "def_": 4},
    "mage": {"hp": 80, "mp": 80, "atk": 8, "def_": 3},
    "rogue": {"hp": 85, "mp": 40, "atk": 11, "def_": 5},
    "paladin": {"hp": 130, "mp": 50, "atk": 10, "def_": 12},
    "reaper": {"hp": 70, "mp": 60, "atk": 16, "def_": 3},
}

CLASS_NAMES: dict[str, str] = {
    "warrior": "전사",
    "archer": "궁수",
    "mage": "마법사",
    "rogue": "도적",
    "paladin": "성기사",
    "reaper": "사신",
}

# 기본 해금 직업 목록
DEFAULT_UNLOCKED_CLASSES: list[str] = ["warrior", "archer"]


# ============================================================
# DB 시드용 상세 데이터
# ============================================================

CLASSES = [
    {
        "id": "warrior",
        "name": "전사",
        "description": "검과 방패의 달인. 높은 체력과 방어력으로 전선을 지킨다.",
        "base_hp": 120,
        "base_mp": 30,
        "base_atk": 12,
        "base_def": 8,
        "special_ability": json.dumps({
            "name": "분노",
            "description": "HP가 30% 이하일 때 공격력 20% 증가",
            "trigger": "hp_below_30",
            "effect": {"atk_mult": 1.2}
        }),
        "unlock_condition": None,  # 기본 해금
    },
    {
        "id": "archer",
        "name": "궁수",
        "description": "민첩한 사냥꾼. 높은 공격력과 크리티컬로 적을 처치한다.",
        "base_hp": 90,
        "base_mp": 50,
        "base_atk": 14,
        "base_def": 4,
        "special_ability": json.dumps({
            "name": "급소 공격",
            "description": "크리티컬 확률 +10%",
            "trigger": "passive",
            "effect": {"crit_bonus": 0.10}
        }),
        "unlock_condition": None,  # 기본 해금
    },
    {
        "id": "mage",
        "name": "마법사",
        "description": "강력한 마법의 사용자. 마나로 적을 압도한다.",
        "base_hp": 80,
        "base_mp": 80,
        "base_atk": 8,
        "base_def": 3,
        "special_ability": json.dumps({
            "name": "마나 순환",
            "description": "전투 승리 시 MP 10% 회복",
            "trigger": "on_victory",
            "effect": {"mp_restore_percent": 0.10}
        }),
        "unlock_condition": json.dumps({
            "type": "achievement",
            "id": "first_clear"
        }),
    },
    {
        "id": "rogue",
        "name": "도적",
        "description": "그림자의 암살자. 치명적인 일격으로 적을 제압한다.",
        "base_hp": 85,
        "base_mp": 40,
        "base_atk": 11,
        "base_def": 5,
        "special_ability": json.dumps({
            "name": "기습",
            "description": "전투 첫 턴 데미지 50% 증가",
            "trigger": "first_turn",
            "effect": {"damage_mult": 1.5}
        }),
        "unlock_condition": json.dumps({
            "type": "souls",
            "amount": 500
        }),
    },
    {
        "id": "paladin",
        "name": "성기사",
        "description": "신성한 전사. 방어와 회복에 특화되어 있다.",
        "base_hp": 130,
        "base_mp": 50,
        "base_atk": 10,
        "base_def": 12,
        "special_ability": json.dumps({
            "name": "신의 가호",
            "description": "휴식 시 HP 회복량 50% 증가",
            "trigger": "on_rest",
            "effect": {"heal_mult": 1.5}
        }),
        "unlock_condition": json.dumps({
            "type": "souls",
            "amount": 1000
        }),
    },
    {
        "id": "reaper",
        "name": "사신",
        "description": "죽음을 다루는 자. 유리하지만 극단적인 성능.",
        "base_hp": 70,
        "base_mp": 60,
        "base_atk": 16,
        "base_def": 3,
        "special_ability": json.dumps({
            "name": "영혼 수확",
            "description": "적 처치 시 소울 획득량 50% 증가",
            "trigger": "on_kill",
            "effect": {"soul_mult": 1.5}
        }),
        "unlock_condition": json.dumps({
            "type": "achievement",
            "id": "defeat_final_boss"
        }),
    },
]


async def seed_classes(db) -> int:
    """직업 데이터 삽입"""
    for c in CLASSES:
        await db.execute("""
            INSERT INTO classes (id, name, description, base_hp, base_mp,
                base_atk, base_def, special_ability, unlock_condition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c["id"], c["name"], c["description"],
            c["base_hp"], c["base_mp"], c["base_atk"], c["base_def"],
            c["special_ability"], c["unlock_condition"]
        ))
    return len(CLASSES)


# ============================================================
# 헬퍼 함수
# ============================================================

def get_class_stat(class_type: str, stat: str) -> int:
    """특정 직업의 특정 스탯 조회"""
    if class_type not in CLASS_STATS:
        raise ValueError(f"존재하지 않는 직업: {class_type}")
    if stat not in CLASS_STATS[class_type]:
        raise ValueError(f"존재하지 않는 스탯: {stat}")
    return CLASS_STATS[class_type][stat]


def get_class_name(class_type: str) -> str:
    """직업 한글명 조회"""
    return CLASS_NAMES.get(class_type, "???")


def is_class_valid(class_type: str) -> bool:
    """유효한 직업인지 확인"""
    return class_type in CLASS_STATS
