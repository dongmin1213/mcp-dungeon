"""v5.0 시너지 시드 데이터 (Phase 1A 상향)"""
from models.synergy import Synergy, SynergyType


# ============================================================
# 세트 시너지 (특정 아이템 조합) - 대폭 상향
# ============================================================
SET_SYNERGIES = [
    # 1. 화염의 마스터 (상향: 화염 면역 + 저항 무시)
    Synergy(
        id="fire_master",
        name="화염의 마스터",
        description="화염 계열 아이템 2개 이상 장착 시",
        type=SynergyType.SET,
        required_items=["infernal_blade", "infernal_armor"],
        required_count=2,
        effect={
            "fire_damage_mult": 2.0,       # 화염 데미지 2배 (기존 1.2)
            "fire_immunity": True,          # 화염 면역 (신규)
            "ignore_fire_resist": True,     # 적 화염 저항 무시 (신규)
        },
        hidden=False
    ),

    # 2. 흡혈 군주 (상향: 조건부 흡혈 폭발)
    Synergy(
        id="vampire_lord",
        name="흡혈 군주",
        description="흡혈 효과 아이템 2개 이상 장착 시",
        type=SynergyType.SET,
        required_items=["vampiric_ring", "bloodthirst_blade"],
        required_count=2,
        effect={
            "lifesteal": 0.25,              # 흡혈 25% (기존 10%)
            "lifesteal_on_low_hp": 2.0,     # HP 50% 이하 시 흡혈 2배 (신규)
            "lifesteal_threshold": 0.5,     # 조건: HP 50% 이하
        },
        hidden=True
    ),

    # 3. 그림자 보행자 (상향: 첫 타격 보너스)
    Synergy(
        id="shadow_walker",
        name="그림자 보행자",
        description="그림자 아이템 2개 이상 장착 시",
        type=SynergyType.SET,
        required_items=["crown_of_shadows", "ritual_dagger"],
        required_count=2,
        effect={
            "crit_bonus": 0.25,             # 크리 +25% (기존 15%)
            "first_strike_mult": 2.0,       # 첫 공격 데미지 2배 (신규)
            "stealth": True,                # 은신 상태 (신규): 적 첫 공격 회피
        },
        hidden=True
    ),

    # 4. 행운의 탐험가 (상향: 드롭 폭발)
    Synergy(
        id="fortune_seeker",
        name="행운의 탐험가",
        description="행운 아이템 2개 이상 장착 시",
        type=SynergyType.SET,
        required_items=["lucky_coin", "lucky_dice"],
        required_count=2,
        effect={
            "gold_mult": 2.0,               # 골드 2배 (기존 1.5)
            "drop_mult": 3.0,               # 드롭률 3배 (기존 2.0)
            "legendary_chance": 0.1,        # 전설 아이템 10% 추가 확률 (신규)
        },
        hidden=True
    ),

    # 5. 비전 마스터 (상향: 스킬 강화)
    Synergy(
        id="arcane_master",
        name="비전 마스터",
        description="마력 아이템 2개 이상 장착 시",
        type=SynergyType.SET,
        required_items=["magic_staff", "mana_crystal"],
        required_count=2,
        effect={
            "max_mp": 50,                   # MP +50 (기존 30)
            "mp_regen": 10,                 # 턴당 MP 회복 +10 (기존 5)
            "skill_damage_mult": 1.5,       # 스킬 데미지 +50% (신규)
            "mp_cost_reduction": 0.3,       # MP 소모 30% 감소 (신규)
        },
        hidden=False
    ),

    # 6. 수정 공명 (상향: 마법 방어 특화)
    Synergy(
        id="crystal_resonance",
        name="수정 공명",
        description="수정 아이템 2개 이상 장착 시",
        type=SynergyType.SET,
        required_items=["crystal_armor", "mana_crystal"],
        required_count=2,
        effect={
            "def": 8,                       # DEF +8 (기존 5)
            "max_mp": 30,                   # MP +30 (기존 20)
            "magic_resist": 0.5,            # 마법 피해 50% 감소 (신규)
            "reflect_magic": 0.2,           # 마법 피해 20% 반사 (신규)
        },
        hidden=False
    ),

    # 7. 전사의 혼 (상향: 반격 시스템)
    Synergy(
        id="warrior_spirit",
        name="전사의 혼",
        description="강철 장비 3개 이상 장착 시",
        type=SynergyType.SET,
        required_items=["steel_sword", "chainmail", "iron_helm"],
        required_count=3,
        effect={
            "atk": 8,                       # ATK +8 (기존 5)
            "def": 8,                       # DEF +8 (기존 5)
            "max_hp": 30,                   # HP +30 (기존 20)
            "counter_chance": 0.3,          # 피격 시 30% 확률 반격 (신규)
            "counter_damage_mult": 1.5,     # 반격 데미지 150% (신규)
        },
        hidden=False
    ),

    # 8. 공허의 포옹 (상향: 공허 특화)
    Synergy(
        id="void_embrace",
        name="공허의 포옹",
        description="공허/지옥 장비 2개 이상 장착 시",
        type=SynergyType.SET,
        required_items=["void_blade", "infernal_armor"],
        required_count=2,
        effect={
            "void_damage": 25,              # 공허 데미지 +25 (기존 15)
            "atk": 12,                      # ATK +12 (기존 8)
            "execute_threshold": 0.2,       # HP 20% 이하 적 즉사 (신규)
            "void_immunity": True,          # 공허 면역 (신규)
        },
        hidden=True
    ),

    # 9. 저주의 짐꾼 (대폭 상향: 저주 반전)
    Synergy(
        id="curse_bearer",
        name="저주의 짐꾼",
        description="저주받은 아이템 2개 이상 장착 시",
        type=SynergyType.SET,
        required_items=["cursed_greatsword", "pain_armor", "madness_helm",
                        "greed_ring", "soul_eater", "berserker_amulet",
                        "glass_cannon", "bloodthirst_blade", "heavy_destiny",
                        "chaos_orb"],
        required_count=2,
        effect={
            "atk": 20,                      # ATK +20 (기존 15)
            "damage_mult": 1.5,             # 데미지 +50% (기존 30%)
            "crit_bonus": 0.3,              # 크리 +30% (신규)
            "curse_immunity": True,         # 저주 페널티 무효화!! (신규)
        },
        hidden=True
    ),

    # 10. 던전 마스터 (최강 세트)
    Synergy(
        id="dungeon_master",
        name="던전 마스터",
        description="마스터 장비 전부 장착 시",
        type=SynergyType.SET,
        required_items=["masters_pendant", "master_robe"],
        required_count=2,
        effect={
            "all_stats": 15,                # 모든 스탯 +15 (기존 10)
            "exp_mult": 2.0,                # 경험치 2배 (기존 1.5)
            "damage_mult": 1.5,             # 데미지 +50% (신규)
            "damage_reduction": 0.2,        # 받는 피해 20% 감소 (신규)
        },
        hidden=True
    ),
]

# ============================================================
# 속성 시너지 (같은 속성 스킬/아이템) - 상향
# ============================================================
ELEMENT_SYNERGIES = [
    Synergy(
        id="fire_affinity",
        name="화염 친화",
        description="화염 속성 효과 강화",
        type=SynergyType.ELEMENT,
        required_category="fire",
        required_count=2,
        effect={
            "fire_damage_mult": 1.5,        # 화염 +50% (기존 30%)
            "burn_chance": 0.3,             # 화상 확률 30% (신규)
            "burn_damage": 5,               # 화상 턴당 데미지 (신규)
        },
        hidden=False
    ),
    Synergy(
        id="ice_affinity",
        name="냉기 친화",
        description="냉기 속성 효과 강화",
        type=SynergyType.ELEMENT,
        required_category="ice",
        required_count=2,
        effect={
            "ice_damage_mult": 1.5,         # 냉기 +50% (기존 30%)
            "slow_duration": 2,             # 둔화 2턴 (기존 1)
            "freeze_chance": 0.15,          # 빙결 확률 15% (신규)
        },
        hidden=False
    ),
    Synergy(
        id="poison_mastery",
        name="독극물 숙련",
        description="독 효과 강화",
        type=SynergyType.ELEMENT,
        required_category="poison",
        required_count=2,
        effect={
            "poison_damage_mult": 2.0,      # 독 +100% (기존 50%)
            "poison_duration": 3,           # 독 지속 +3턴 (기존 2)
            "poison_stack": 2,              # 독 중첩 가능 (신규)
        },
        hidden=False
    ),
    Synergy(
        id="holy_blessing",
        name="신성한 축복",
        description="신성 효과 강화",
        type=SynergyType.ELEMENT,
        required_category="holy",
        required_count=2,
        effect={
            "holy_damage_mult": 1.6,        # 신성 +60% (기존 40%)
            "heal_bonus": 0.5,              # 회복량 +50% (기존 20%)
            "undead_damage_mult": 2.0,      # 언데드 특공 2배 (신규)
        },
        hidden=True
    ),
    Synergy(
        id="dark_pact",
        name="어둠의 계약",
        description="암흑 효과 강화",
        type=SynergyType.ELEMENT,
        required_category="dark",
        required_count=2,
        effect={
            "dark_damage_mult": 1.6,        # 암흑 +60% (기존 40%)
            "lifesteal": 0.15,              # 흡혈 +15% (기존 5%)
            "soul_mult": 1.5,               # 소울 +50% (신규)
        },
        hidden=True
    ),
]

# ============================================================
# 숨겨진 시너지 (발견의 재미) - Phase 1A 신규
# ============================================================
HIDDEN_SYNERGIES = [
    # 1. 저주의 주인 (저주 3개 = 저주가 축복으로)
    Synergy(
        id="curse_master",
        name="저주의 주인",
        description="저주받은 아이템 3개 이상 장착 시 - 저주가 축복이 된다",
        type=SynergyType.SET,
        required_items=["cursed_greatsword", "pain_armor", "madness_helm",
                        "greed_ring", "soul_eater", "berserker_amulet",
                        "glass_cannon", "bloodthirst_blade", "heavy_destiny",
                        "chaos_orb"],
        required_count=3,
        effect={
            "curse_to_blessing": True,      # 저주 효과가 긍정 효과로 변환!!
            "atk": 30,                      # ATK +30
            "damage_mult": 2.0,             # 데미지 2배
            "lifesteal": 0.2,               # 흡혈 20%
        },
        hidden=True
    ),

    # 2. 원소의 화신 (같은 속성 무기+방어구+악세)
    Synergy(
        id="elemental_avatar",
        name="원소의 화신",
        description="같은 속성 장비 3개 이상 (무기+방어구+악세서리)",
        type=SynergyType.SET,
        # 화염 세트
        required_items=["infernal_blade", "infernal_armor", "fire_ring"],
        required_count=3,
        effect={
            "element_immunity": True,       # 해당 속성 면역
            "element_damage_mult": 2.5,     # 해당 속성 데미지 2.5배
            "aura_damage": 10,              # 턴마다 주변 적에게 데미지 (신규)
        },
        hidden=True
    ),

    # 3. 무한 탱커 (흡혈 + 가시 + 도발)
    Synergy(
        id="immortal_tank",
        name="무한 탱커",
        description="흡혈 + 반사 + 도발 효과 장비 조합",
        type=SynergyType.SET,
        required_items=["vampiric_ring", "thorn_armor", "taunt_shield",
                        "bloodthirst_blade"],
        required_count=3,
        effect={
            "lifesteal": 0.5,               # 흡혈 50%
            "reflect_damage": 0.5,          # 반사 50%
            "taunt": True,                  # 도발 (적 공격 집중)
            "lifesteal_on_reflect": True,   # 반사 데미지에도 흡혈 적용!!
            "def": 10,                      # DEF +10
        },
        hidden=True
    ),
]

# ============================================================
# 모든 시너지
# ============================================================
ALL_SYNERGIES = SET_SYNERGIES + ELEMENT_SYNERGIES + HIDDEN_SYNERGIES


def get_synergy_by_id(synergy_id: str) -> Synergy | None:
    """ID로 시너지 찾기"""
    for synergy in ALL_SYNERGIES:
        if synergy.id == synergy_id:
            return synergy
    return None


def get_hidden_synergies() -> list[Synergy]:
    """숨겨진 시너지 목록"""
    return [s for s in ALL_SYNERGIES if s.hidden]


def get_visible_synergies() -> list[Synergy]:
    """공개된 시너지 목록"""
    return [s for s in ALL_SYNERGIES if not s.hidden]
