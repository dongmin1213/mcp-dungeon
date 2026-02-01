"""몬스터 모델"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class MonsterType(str, Enum):
    NORMAL = "normal"
    ELITE = "elite"
    BOSS = "boss"


class EnemyAction(str, Enum):
    """적 행동 타입 (v5.0 행동 예고제)"""
    ATTACK = "attack"       # ⚔️ 기본 공격
    HEAVY = "heavy"         # 🔨 강타 (높은 데미지)
    DEFEND = "defend"       # 🛡️ 방어 (데미지 감소)
    CHARGE = "charge"       # ⚡ 충전 (다음 턴 강타)
    HEAL = "heal"           # 💚 회복
    BUFF = "buff"           # ⬆️ 자기 강화
    DEBUFF = "debuff"       # ⬇️ 플레이어 약화
    SPECIAL = "special"     # ⭐ 특수 행동


# 행동별 아이콘
ACTION_ICONS = {
    EnemyAction.ATTACK: "⚔️",
    EnemyAction.HEAVY: "🔨",
    EnemyAction.DEFEND: "🛡️",
    EnemyAction.CHARGE: "⚡",
    EnemyAction.HEAL: "💚",
    EnemyAction.BUFF: "⬆️",
    EnemyAction.DEBUFF: "⬇️",
    EnemyAction.SPECIAL: "⭐",
}

# 행동별 설명
ACTION_NAMES = {
    EnemyAction.ATTACK: "공격",
    EnemyAction.HEAVY: "강타",
    EnemyAction.DEFEND: "방어",
    EnemyAction.CHARGE: "충전",
    EnemyAction.HEAL: "회복",
    EnemyAction.BUFF: "강화",
    EnemyAction.DEBUFF: "약화",
    EnemyAction.SPECIAL: "특수",
}


class Monster(BaseModel):
    """몬스터"""
    id: str
    name: str
    type: MonsterType

    hp: int
    max_hp: int
    atk: int
    def_: int

    exp: int
    gold_min: int
    gold_max: int
    souls: int

    skills: list[str] = []
    pattern: Optional[dict] = None  # 보스 패턴 (파싱된 dict)
    pattern_json: Optional[str] = None  # 보스 패턴 (원본 JSON)

    # v5.0 행동 예고제
    action_pattern: list[str] = []  # 행동 패턴 (예: ["attack", "attack", "heavy"])
    next_action: Optional[EnemyAction] = None  # 다음 행동
    charged: bool = False  # 충전 상태 (다음 턴 강타)

    # v5.0 속성 시스템
    element: Optional[str] = None  # 속성 (fire, ice, lightning, poison, holy, dark)
    weaknesses: list[str] = []  # 약점 속성
    resistances: list[str] = []  # 저항 속성
    immunities: list[str] = []  # 면역 속성

    @property
    def is_alive(self) -> bool:
        """생존 여부"""
        return self.hp > 0

    @property
    def is_boss(self) -> bool:
        """보스 여부"""
        return self.type == MonsterType.BOSS

    @property
    def is_elite(self) -> bool:
        """엘리트 여부"""
        return self.type == MonsterType.ELITE

    def take_damage(self, damage: int) -> int:
        """데미지를 받음. 실제 받은 데미지 반환"""
        actual_damage = max(1, damage)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    @classmethod
    def from_db_row(cls, row: dict) -> "Monster":
        """DB 행에서 Monster 생성"""
        import json
        pattern_str = row.get("pattern")

        # v5.0 행동 패턴 파싱
        action_pattern_str = row.get("action_pattern")
        action_pattern = json.loads(action_pattern_str) if action_pattern_str else ["attack"]

        # v5.0 속성 파싱
        weaknesses_str = row.get("weaknesses")
        resistances_str = row.get("resistances")
        immunities_str = row.get("immunities")

        return cls(
            id=row["id"],
            name=row["name"],
            type=MonsterType(row["type"]),
            hp=row["hp"],
            max_hp=row["hp"],
            atk=row["atk"],
            def_=row["def"],
            exp=row["exp"],
            gold_min=row["gold_min"],
            gold_max=row["gold_max"],
            souls=row["souls"],
            skills=json.loads(row["skills"]) if row["skills"] else [],
            pattern=json.loads(pattern_str) if pattern_str else None,
            pattern_json=pattern_str,
            # v5.0 필드
            action_pattern=action_pattern,
            element=row.get("element"),
            weaknesses=json.loads(weaknesses_str) if weaknesses_str else [],
            resistances=json.loads(resistances_str) if resistances_str else [],
            immunities=json.loads(immunities_str) if immunities_str else [],
        )
