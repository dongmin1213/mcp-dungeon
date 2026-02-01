"""v5.0 축복 시드 데이터"""
from models.blessing import Blessing, BlessingCategory, BlessingRarity

# 축복 데이터 정의
BLESSINGS = [
    # ===== 공격 축복 (ATTACK) =====
    # Common
    Blessing(
        id="atk_up_1", name="근력 강화", category=BlessingCategory.ATTACK,
        rarity=BlessingRarity.COMMON,
        description="ATK +3",
        effect={"atk": 3}
    ),
    Blessing(
        id="atk_up_2", name="강력한 일격", category=BlessingCategory.ATTACK,
        rarity=BlessingRarity.COMMON,
        description="ATK +2, 크리티컬 확률 +5%",
        effect={"atk": 2, "crit_chance": 0.05}
    ),
    Blessing(
        id="crit_up_1", name="급소 훈련", category=BlessingCategory.ATTACK,
        rarity=BlessingRarity.COMMON,
        description="크리티컬 확률 +10%",
        effect={"crit_chance": 0.10}
    ),

    # Uncommon
    Blessing(
        id="atk_up_3", name="전투의 달인", category=BlessingCategory.ATTACK,
        rarity=BlessingRarity.UNCOMMON,
        description="ATK +5",
        effect={"atk": 5}
    ),
    Blessing(
        id="damage_up_1", name="파괴자", category=BlessingCategory.ATTACK,
        rarity=BlessingRarity.UNCOMMON,
        description="모든 데미지 +10%",
        effect={"damage_mult": 1.10}
    ),
    Blessing(
        id="crit_up_2", name="치명타 마스터", category=BlessingCategory.ATTACK,
        rarity=BlessingRarity.UNCOMMON,
        description="크리티컬 확률 +15%",
        effect={"crit_chance": 0.15}
    ),

    # Rare
    Blessing(
        id="berserker", name="광전사", category=BlessingCategory.ATTACK,
        rarity=BlessingRarity.RARE,
        description="ATK +8, 받는 데미지 +10%",
        effect={"atk": 8, "damage_taken_mult": 1.10}
    ),
    Blessing(
        id="damage_up_2", name="학살자", category=BlessingCategory.ATTACK,
        rarity=BlessingRarity.RARE,
        description="모든 데미지 +20%",
        effect={"damage_mult": 1.20}
    ),

    # Legendary
    Blessing(
        id="double_hit", name="이중 타격", category=BlessingCategory.ATTACK,
        rarity=BlessingRarity.LEGENDARY,
        description="기본 공격 시 20% 확률로 2회 공격",
        effect={"double_hit": 0.20}
    ),
    Blessing(
        id="executioner", name="처형자", category=BlessingCategory.ATTACK,
        rarity=BlessingRarity.LEGENDARY,
        description="적 HP 15% 이하일 때 즉사",
        effect={"execute_threshold": 0.15}
    ),

    # ===== 방어 축복 (DEFENSE) =====
    # Common
    Blessing(
        id="def_up_1", name="철벽", category=BlessingCategory.DEFENSE,
        rarity=BlessingRarity.COMMON,
        description="DEF +2",
        effect={"def": 2}
    ),
    Blessing(
        id="hp_up_1", name="활력", category=BlessingCategory.DEFENSE,
        rarity=BlessingRarity.COMMON,
        description="최대 HP +15",
        effect={"max_hp": 15}
    ),
    Blessing(
        id="hp_up_2", name="생명력 강화", category=BlessingCategory.DEFENSE,
        rarity=BlessingRarity.COMMON,
        description="최대 HP +10, DEF +1",
        effect={"max_hp": 10, "def": 1}
    ),

    # Uncommon
    Blessing(
        id="def_up_2", name="강철 피부", category=BlessingCategory.DEFENSE,
        rarity=BlessingRarity.UNCOMMON,
        description="DEF +4",
        effect={"def": 4}
    ),
    Blessing(
        id="hp_up_3", name="거인의 체력", category=BlessingCategory.DEFENSE,
        rarity=BlessingRarity.UNCOMMON,
        description="최대 HP +25",
        effect={"max_hp": 25}
    ),
    Blessing(
        id="thorns_1", name="가시 갑옷", category=BlessingCategory.DEFENSE,
        rarity=BlessingRarity.UNCOMMON,
        description="피격 시 5 반사 데미지",
        effect={"thorns": 5}
    ),

    # Rare
    Blessing(
        id="tank", name="불굴의 의지", category=BlessingCategory.DEFENSE,
        rarity=BlessingRarity.RARE,
        description="최대 HP +40, DEF +3",
        effect={"max_hp": 40, "def": 3}
    ),
    Blessing(
        id="thorns_2", name="보복의 가시", category=BlessingCategory.DEFENSE,
        rarity=BlessingRarity.RARE,
        description="피격 시 10 반사 데미지",
        effect={"thorns": 10}
    ),

    # Legendary
    Blessing(
        id="immortal", name="불멸자", category=BlessingCategory.DEFENSE,
        rarity=BlessingRarity.LEGENDARY,
        description="최대 HP +50, DEF +5, ATK -3",
        effect={"max_hp": 50, "def": 5, "atk": -3}
    ),

    # ===== 유틸리티 축복 (UTILITY) =====
    # Common
    Blessing(
        id="gold_up_1", name="황금손", category=BlessingCategory.UTILITY,
        rarity=BlessingRarity.COMMON,
        description="골드 획득량 +15%",
        effect={"gold_mult": 1.15}
    ),
    Blessing(
        id="exp_up_1", name="빠른 성장", category=BlessingCategory.UTILITY,
        rarity=BlessingRarity.COMMON,
        description="경험치 획득량 +15%",
        effect={"exp_mult": 1.15}
    ),
    Blessing(
        id="mp_up_1", name="마나 샘", category=BlessingCategory.UTILITY,
        rarity=BlessingRarity.COMMON,
        description="최대 MP +10",
        effect={"max_mp": 10}
    ),

    # Uncommon
    Blessing(
        id="lifesteal_1", name="흡혈", category=BlessingCategory.UTILITY,
        rarity=BlessingRarity.UNCOMMON,
        description="공격 시 데미지의 10% HP 회복",
        effect={"lifesteal": 0.10}
    ),
    Blessing(
        id="gold_up_2", name="재물신의 축복", category=BlessingCategory.UTILITY,
        rarity=BlessingRarity.UNCOMMON,
        description="골드 획득량 +30%",
        effect={"gold_mult": 1.30}
    ),
    Blessing(
        id="exp_up_2", name="지혜의 빛", category=BlessingCategory.UTILITY,
        rarity=BlessingRarity.UNCOMMON,
        description="경험치 획득량 +30%",
        effect={"exp_mult": 1.30}
    ),

    # Rare
    Blessing(
        id="lifesteal_2", name="흡혈귀", category=BlessingCategory.UTILITY,
        rarity=BlessingRarity.RARE,
        description="공격 시 데미지의 20% HP 회복",
        effect={"lifesteal": 0.20}
    ),
    Blessing(
        id="treasure_hunter", name="보물 사냥꾼", category=BlessingCategory.UTILITY,
        rarity=BlessingRarity.RARE,
        description="골드 +50%, 경험치 +20%",
        effect={"gold_mult": 1.50, "exp_mult": 1.20}
    ),

    # Legendary
    Blessing(
        id="vampire_lord", name="뱀파이어 로드", category=BlessingCategory.UTILITY,
        rarity=BlessingRarity.LEGENDARY,
        description="흡혈 30%, 최대 HP -20",
        effect={"lifesteal": 0.30, "max_hp": -20}
    ),

    # ===== 스킬 축복 (SKILL) =====
    # Common
    Blessing(
        id="mp_regen_1", name="마나 순환", category=BlessingCategory.SKILL,
        rarity=BlessingRarity.COMMON,
        description="최대 MP +5, 스킬 데미지 +5%",
        effect={"max_mp": 5, "skill_damage_mult": 1.05}
    ),

    # Uncommon
    Blessing(
        id="skill_master", name="기술의 달인", category=BlessingCategory.SKILL,
        rarity=BlessingRarity.UNCOMMON,
        description="스킬 데미지 +15%",
        effect={"skill_damage_mult": 1.15}
    ),
    Blessing(
        id="mp_up_2", name="마력 증폭", category=BlessingCategory.SKILL,
        rarity=BlessingRarity.UNCOMMON,
        description="최대 MP +20",
        effect={"max_mp": 20}
    ),

    # Rare
    Blessing(
        id="arcane_power", name="비전력", category=BlessingCategory.SKILL,
        rarity=BlessingRarity.RARE,
        description="스킬 데미지 +25%, MP 소모 +10%",
        effect={"skill_damage_mult": 1.25, "mp_cost_mult": 1.10}
    ),

    # Legendary
    Blessing(
        id="spell_master", name="마법 대가", category=BlessingCategory.SKILL,
        rarity=BlessingRarity.LEGENDARY,
        description="스킬 데미지 +40%, 최대 MP +30",
        effect={"skill_damage_mult": 1.40, "max_mp": 30}
    ),
]


# 희귀도별 가중치 (축복 선택 시 사용)
RARITY_WEIGHTS = {
    BlessingRarity.COMMON: 60,
    BlessingRarity.UNCOMMON: 25,
    BlessingRarity.RARE: 12,
    BlessingRarity.LEGENDARY: 3,
}


def get_blessings_by_rarity(rarity: BlessingRarity) -> list[Blessing]:
    """희귀도별 축복 목록"""
    return [b for b in BLESSINGS if b.rarity == rarity]


def get_blessings_by_category(category: BlessingCategory) -> list[Blessing]:
    """카테고리별 축복 목록"""
    return [b for b in BLESSINGS if b.category == category]


def get_blessing_by_id(blessing_id: str) -> Blessing | None:
    """ID로 축복 조회"""
    for b in BLESSINGS:
        if b.id == blessing_id:
            return b
    return None
