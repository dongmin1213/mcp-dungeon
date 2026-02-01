"""메타 프로그레션 관련 모델"""
from pydantic import BaseModel
from typing import Optional


class Upgrade(BaseModel):
    """영구 업그레이드 정의"""
    id: str
    name: str
    description: str
    max_level: int
    base_cost: int           # 1레벨 비용
    cost_increase: int       # 레벨당 비용 증가
    stat_key: str            # ProfileUpgrades의 필드명

    def get_cost(self, current_level: int) -> int:
        """다음 레벨 비용 계산"""
        if current_level >= self.max_level:
            return -1  # 최대 레벨
        return self.base_cost + (self.cost_increase * current_level)


class Achievement(BaseModel):
    """업적 정의"""
    id: str
    name: str
    description: str
    category: str            # combat, explore, collect, challenge
    condition_type: str      # monsters_killed, floors_reached, runs_completed, etc.
    condition_value: int     # 달성 조건 값
    reward_type: str         # souls, unlock_class, unlock_item, unlock_mode
    reward_value: str | int  # 보상 값 (소울 양 또는 언락 ID)
    hidden: bool = False     # 숨겨진 업적 여부


class UnlockRequirement(BaseModel):
    """언락 조건"""
    id: str
    name: str
    type: str                # class, item, mode
    cost: int                # 소울 비용
    requirement_type: Optional[str] = None  # achievement, stat, none
    requirement_value: Optional[str] = None # 조건 값


# 업그레이드 정의
UPGRADES: list[Upgrade] = [
    Upgrade(
        id="max_hp", name="생명력 강화",
        description="최대 HP +5 (영구)",
        max_level=10, base_cost=50, cost_increase=25,
        stat_key="max_hp_bonus"
    ),
    Upgrade(
        id="max_mp", name="마나 강화",
        description="최대 MP +3 (영구)",
        max_level=10, base_cost=40, cost_increase=20,
        stat_key="max_mp_bonus"
    ),
    Upgrade(
        id="atk", name="공격력 강화",
        description="공격력 +1 (영구)",
        max_level=5, base_cost=80, cost_increase=40,
        stat_key="atk_bonus"
    ),
    Upgrade(
        id="def", name="방어력 강화",
        description="방어력 +1 (영구)",
        max_level=5, base_cost=80, cost_increase=40,
        stat_key="def_bonus"
    ),
    Upgrade(
        id="crit", name="치명타 강화",
        description="크리티컬 확률 +1% (영구)",
        max_level=10, base_cost=60, cost_increase=30,
        stat_key="crit_bonus"
    ),
    Upgrade(
        id="gold", name="황금 손",
        description="골드 획득량 +5% (영구)",
        max_level=10, base_cost=30, cost_increase=15,
        stat_key="gold_bonus"
    ),
    Upgrade(
        id="exp", name="빠른 성장",
        description="경험치 획득량 +5% (영구)",
        max_level=10, base_cost=40, cost_increase=20,
        stat_key="exp_bonus"
    ),
    Upgrade(
        id="potion", name="연금술 지식",
        description="포션 효과 +10% (영구)",
        max_level=5, base_cost=50, cost_increase=25,
        stat_key="potion_effect"
    ),
    Upgrade(
        id="starting_gold", name="유산",
        description="시작 골드 +20 (영구)",
        max_level=10, base_cost=25, cost_increase=15,
        stat_key="starting_gold"
    ),
    Upgrade(
        id="soul", name="영혼 수확자",
        description="소울 획득량 +5% (영구)",
        max_level=10, base_cost=100, cost_increase=50,
        stat_key="soul_bonus"
    ),
]

# 업적 정의
ACHIEVEMENTS: list[Achievement] = [
    # 전투 업적
    Achievement(
        id="first_blood", name="첫 번째 피",
        description="몬스터를 처음으로 처치하라",
        category="combat", condition_type="monsters_killed", condition_value=1,
        reward_type="souls", reward_value=10
    ),
    Achievement(
        id="monster_slayer", name="몬스터 슬레이어",
        description="몬스터 100마리 처치",
        category="combat", condition_type="monsters_killed", condition_value=100,
        reward_type="souls", reward_value=100
    ),
    Achievement(
        id="monster_hunter", name="몬스터 헌터",
        description="몬스터 500마리 처치",
        category="combat", condition_type="monsters_killed", condition_value=500,
        reward_type="souls", reward_value=300
    ),
    Achievement(
        id="boss_slayer", name="보스 슬레이어",
        description="보스 5마리 처치",
        category="combat", condition_type="bosses_killed", condition_value=5,
        reward_type="souls", reward_value=150
    ),
    Achievement(
        id="boss_hunter", name="보스 헌터",
        description="보스 20마리 처치",
        category="combat", condition_type="bosses_killed", condition_value=20,
        reward_type="souls", reward_value=500
    ),

    # 탐험 업적
    Achievement(
        id="first_steps", name="첫 발걸음",
        description="던전에 처음 입장하라",
        category="explore", condition_type="runs_completed", condition_value=1,
        reward_type="souls", reward_value=10
    ),
    Achievement(
        id="floor_3", name="중급 탐험가",
        description="3층에 도달하라",
        category="explore", condition_type="highest_floor", condition_value=3,
        reward_type="unlock_class", reward_value="mage"
    ),
    Achievement(
        id="floor_5", name="고급 탐험가",
        description="5층에 도달하라",
        category="explore", condition_type="highest_floor", condition_value=5,
        reward_type="unlock_class", reward_value="archer"
    ),
    Achievement(
        id="floor_clear", name="던전 정복자",
        description="던전을 클리어하라 (5층 보스 처치)",
        category="explore", condition_type="victories", condition_value=1,
        reward_type="unlock_class", reward_value="rogue"
    ),
    Achievement(
        id="veteran", name="베테랑",
        description="10회 플레이 완료",
        category="explore", condition_type="runs_completed", condition_value=10,
        reward_type="souls", reward_value=200
    ),
    Achievement(
        id="dedicated", name="헌신자",
        description="50회 플레이 완료",
        category="explore", condition_type="runs_completed", condition_value=50,
        reward_type="unlock_class", reward_value="paladin"
    ),

    # 수집 업적
    Achievement(
        id="gold_collector", name="황금 수집가",
        description="총 10,000 골드 획득",
        category="collect", condition_type="gold_earned", condition_value=10000,
        reward_type="souls", reward_value=150
    ),
    Achievement(
        id="gold_hoarder", name="황금 저장고",
        description="총 50,000 골드 획득",
        category="collect", condition_type="gold_earned", condition_value=50000,
        reward_type="souls", reward_value=400
    ),
    Achievement(
        id="soul_collector", name="영혼 수집가",
        description="총 1,000 소울 획득",
        category="collect", condition_type="souls_earned", condition_value=1000,
        reward_type="souls", reward_value=200
    ),
    Achievement(
        id="soul_hoarder", name="영혼 저장고",
        description="총 5,000 소울 획득",
        category="collect", condition_type="souls_earned", condition_value=5000,
        reward_type="unlock_class", reward_value="reaper"
    ),

    # 도전 업적
    Achievement(
        id="first_victory", name="첫 번째 승리",
        description="던전을 처음으로 클리어하라",
        category="challenge", condition_type="victories", condition_value=1,
        reward_type="souls", reward_value=500
    ),
    Achievement(
        id="veteran_victor", name="숙련된 승자",
        description="던전을 5회 클리어하라",
        category="challenge", condition_type="victories", condition_value=5,
        reward_type="unlock_mode", reward_value="hard"
    ),
    Achievement(
        id="master_victor", name="마스터 승자",
        description="던전을 10회 클리어하라",
        category="challenge", condition_type="victories", condition_value=10,
        reward_type="unlock_mode", reward_value="hell"
    ),
    Achievement(
        id="speedrunner", name="스피드러너",
        description="30분 이내에 클리어하라",
        category="challenge", condition_type="fastest_clear", condition_value=1800,
        reward_type="souls", reward_value=300,
        hidden=True
    ),
    Achievement(
        id="high_level", name="레벨 마스터",
        description="레벨 15 달성",
        category="challenge", condition_type="highest_level", condition_value=15,
        reward_type="souls", reward_value=250
    ),
]

# 언락 정의
UNLOCKS: list[UnlockRequirement] = [
    # 직업 언락
    UnlockRequirement(
        id="mage", name="마법사",
        type="class", cost=0,
        requirement_type="achievement", requirement_value="floor_3"
    ),
    UnlockRequirement(
        id="archer", name="궁수",
        type="class", cost=0,
        requirement_type="achievement", requirement_value="floor_5"
    ),
    UnlockRequirement(
        id="rogue", name="도적",
        type="class", cost=0,
        requirement_type="achievement", requirement_value="floor_clear"
    ),
    UnlockRequirement(
        id="paladin", name="성기사",
        type="class", cost=0,
        requirement_type="achievement", requirement_value="dedicated"
    ),
    UnlockRequirement(
        id="reaper", name="사신",
        type="class", cost=0,
        requirement_type="achievement", requirement_value="soul_hoarder"
    ),

    # 모드 언락
    UnlockRequirement(
        id="hard", name="하드 모드",
        type="mode", cost=0,
        requirement_type="achievement", requirement_value="veteran_victor"
    ),
    UnlockRequirement(
        id="hell", name="지옥 모드",
        type="mode", cost=0,
        requirement_type="achievement", requirement_value="master_victor"
    ),
    UnlockRequirement(
        id="infinite", name="무한 모드",
        type="mode", cost=500,
        requirement_type="stat", requirement_value="victories:3"
    ),
    UnlockRequirement(
        id="daily", name="일일 도전",
        type="mode", cost=300,
        requirement_type="stat", requirement_value="runs_completed:5"
    ),
]


def get_upgrade_by_id(upgrade_id: str) -> Upgrade | None:
    """ID로 업그레이드 찾기"""
    for upgrade in UPGRADES:
        if upgrade.id == upgrade_id:
            return upgrade
    return None


def get_achievement_by_id(achievement_id: str) -> Achievement | None:
    """ID로 업적 찾기"""
    for achievement in ACHIEVEMENTS:
        if achievement.id == achievement_id:
            return achievement
    return None


def get_unlock_by_id(unlock_id: str) -> UnlockRequirement | None:
    """ID로 언락 찾기"""
    for unlock in UNLOCKS:
        if unlock.id == unlock_id:
            return unlock
    return None


# ====================================
# v5.0 메타 진행 리디자인
# ====================================

class StartingOption(BaseModel):
    """v5.0 시작 옵션"""
    id: str
    name: str
    description: str
    effect: dict  # {"starting_gold": 100, "starting_item": "...", ...}
    requirement_type: Optional[str] = None  # victories, runs, achievements
    requirement_value: Optional[int | str] = None


class ChallengeModifier(BaseModel):
    """v5.0 도전 모드 수정자"""
    id: str
    name: str
    description: str
    effect: dict  # 난이도 수정
    souls_bonus: float = 1.0  # 소울 보너스 배율


# E3: 시작 옵션 정의
STARTING_OPTIONS: list[StartingOption] = [
    StartingOption(
        id="standard",
        name="기본 시작",
        description="일반적인 시작",
        effect={}
    ),
    StartingOption(
        id="rich_start",
        name="부자 시작",
        description="시작 골드 +100",
        effect={"starting_gold": 100},
        requirement_type="victories",
        requirement_value=3
    ),
    StartingOption(
        id="armed_start",
        name="무장 시작",
        description="기본 무기 장착 시작",
        effect={"starting_item": "old_sword"},
        requirement_type="runs",
        requirement_value=10
    ),
    StartingOption(
        id="blessed_start",
        name="축복 시작",
        description="랜덤 축복 1개로 시작",
        effect={"starting_blessing": True},
        requirement_type="achievements",
        requirement_value="soul_collector"
    ),
    StartingOption(
        id="prepared_start",
        name="준비된 시작",
        description="소형 HP/MP 포션으로 시작",
        effect={"starting_items": ["hp_potion_s", "mp_potion_s"]},
        requirement_type="runs",
        requirement_value=5
    ),
    StartingOption(
        id="lucky_start",
        name="행운의 시작",
        description="행운의 동전으로 시작",
        effect={"starting_item": "lucky_coin"},
        requirement_type="victories",
        requirement_value=5
    ),
    StartingOption(
        id="cursed_start",
        name="저주받은 시작",
        description="저주받은 아이템으로 시작 (강력하지만 위험)",
        effect={"starting_cursed": True, "starting_gold": 50},
        requirement_type="achievements",
        requirement_value="floor_clear"
    ),
]

# E2: 도전 모드 수정자 정의
CHALLENGE_MODIFIERS: list[ChallengeModifier] = [
    ChallengeModifier(
        id="no_shop",
        name="상점 없음",
        description="상점이 등장하지 않습니다",
        effect={"disable_shop": True},
        souls_bonus=1.3
    ),
    ChallengeModifier(
        id="no_rest",
        name="휴식 금지",
        description="휴식처가 등장하지 않습니다",
        effect={"disable_rest": True},
        souls_bonus=1.5
    ),
    ChallengeModifier(
        id="elite_only",
        name="엘리트 전쟁",
        description="모든 몬스터가 엘리트입니다",
        effect={"all_elite": True},
        souls_bonus=2.0
    ),
    ChallengeModifier(
        id="glass_cannon",
        name="유리 대포",
        description="데미지 2배, 받는 데미지 2배",
        effect={"damage_mult": 2.0, "damage_taken_mult": 2.0},
        souls_bonus=1.2
    ),
    ChallengeModifier(
        id="poor_start",
        name="가난한 시작",
        description="시작 골드 0, 상점 가격 +50%",
        effect={"starting_gold": 0, "shop_price_mult": 1.5},
        souls_bonus=1.4
    ),
    ChallengeModifier(
        id="fragile",
        name="유약함",
        description="최대 HP -30%",
        effect={"max_hp_mult": 0.7},
        souls_bonus=1.5
    ),
    ChallengeModifier(
        id="time_pressure",
        name="시간 압박",
        description="50턴마다 HP 10% 감소",
        effect={"turn_damage_interval": 50, "turn_damage_percent": 0.1},
        souls_bonus=1.3
    ),
]


def get_starting_option_by_id(option_id: str) -> StartingOption | None:
    """ID로 시작 옵션 찾기"""
    for option in STARTING_OPTIONS:
        if option.id == option_id:
            return option
    return None


def get_challenge_modifier_by_id(modifier_id: str) -> ChallengeModifier | None:
    """ID로 도전 수정자 찾기"""
    for modifier in CHALLENGE_MODIFIERS:
        if modifier.id == modifier_id:
            return modifier
    return None


def get_available_starting_options(profile_stats: dict) -> list[StartingOption]:
    """사용 가능한 시작 옵션 목록"""
    available = []

    for option in STARTING_OPTIONS:
        if option.requirement_type is None:
            available.append(option)
            continue

        # 조건 확인
        if option.requirement_type == "victories":
            if profile_stats.get("victories", 0) >= option.requirement_value:
                available.append(option)
        elif option.requirement_type == "runs":
            if profile_stats.get("runs_completed", 0) >= option.requirement_value:
                available.append(option)
        elif option.requirement_type == "achievements":
            if option.requirement_value in profile_stats.get("completed_achievements", []):
                available.append(option)

    return available
