"""Phase 3: 듀오 축복 시드 데이터

듀오 축복은 두 축복을 함께 보유할 때 특수 효과가 발동하는 시스템입니다.
발견은 직접 해야 하며, 힌트만 "???"로 표시됩니다.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DuoBlessing:
    """듀오 축복 정의"""
    id: str
    name: str
    icon: str
    blessing_a: str  # 첫 번째 축복 ID
    blessing_b: str  # 두 번째 축복 ID
    description: str
    effect: dict
    discovered: bool = False  # 발견 여부


# ============================================================
# 듀오 축복 정의 (10종)
# ============================================================
DUO_BLESSINGS = [
    # 1. 피의 광기 (흡혈자 + 광전사)
    DuoBlessing(
        id="blood_frenzy",
        name="피의 광기",
        icon="🩸⚔️",
        blessing_a="vampiric",      # 흡혈자
        blessing_b="berserker",     # 광전사
        description="흡혈 100%, HP 회복 시 ATK +5% 스택",
        effect={
            "lifesteal_bonus": 1.0,     # 흡혈 +100% (총 2배)
            "heal_to_atk": 0.05,        # HP 회복 시 ATK +5% 스택
            "max_atk_stacks": 10,       # 최대 10스택 (+50%)
        },
    ),

    # 2. 암살자의 낙인 (처형자 + 독 마스터)
    DuoBlessing(
        id="assassin_mark",
        name="암살자의 낙인",
        icon="💀🟢",
        blessing_a="executioner",   # 처형자
        blessing_b="poison_master", # 독 마스터
        description="독 상태 적 HP 30% 이하 즉사",
        effect={
            "poison_execute_threshold": 0.3,  # 독 상태 적 30% 이하 즉사
        },
    ),

    # 3. 아크메이지 (마나 샘 + 주문 증폭)
    DuoBlessing(
        id="archmage",
        name="아크메이지",
        icon="🔮✨",
        blessing_a="mana_well",     # 마나 샘
        blessing_b="spell_amp",     # 주문 증폭
        description="스킬 MP 소모 50%, 스킬 데미지 x2",
        effect={
            "skill_mp_cost_mult": 0.5,   # MP 소모 50%
            "skill_damage_mult": 2.0,    # 스킬 데미지 2배
        },
    ),

    # 4. 고슴도치 (철벽 + 가시)
    DuoBlessing(
        id="hedgehog",
        name="고슴도치",
        icon="🦔💥",
        blessing_a="iron_wall",     # 철벽
        blessing_b="thorns",        # 가시
        description="방어 시 받는 데미지 100% 반사",
        effect={
            "defend_full_reflect": True,  # 방어 중 100% 반사
        },
    ),

    # 5. 폭풍의 검 (신속 + 연속 공격)
    DuoBlessing(
        id="storm_blade",
        name="폭풍의 검",
        icon="⚡🗡️",
        blessing_a="swift",         # 신속
        blessing_b="multi_strike",  # 연속 공격
        description="기본 공격 3회 타격",
        effect={
            "attack_hits": 3,  # 공격 3회
        },
    ),

    # 6. 불멸의 투사 (끈질긴 생명 + 재생)
    DuoBlessing(
        id="immortal_warrior",
        name="불멸의 투사",
        icon="💪💚",
        blessing_a="tenacity",      # 끈질긴 생명
        blessing_b="regeneration",  # 재생
        description="치명상 시 HP 1로 생존 (1회), 턴당 HP 5% 회복",
        effect={
            "death_save": 1,           # 1회 죽음 회피
            "hp_regen_percent": 0.05,  # 턴당 5% 회복
        },
    ),

    # 7. 황금 손 (행운 + 상인)
    DuoBlessing(
        id="golden_touch",
        name="황금 손",
        icon="✋💰",
        blessing_a="lucky",         # 행운
        blessing_b="merchant",      # 상인
        description="모든 골드 획득 3배, 상점 가격 50% 할인",
        effect={
            "gold_mult": 3.0,       # 골드 3배
            "shop_discount": 0.5,   # 50% 할인
        },
    ),

    # 8. 마나 폭주 (마나 샘 + 재생)
    DuoBlessing(
        id="mana_overflow",
        name="마나 폭주",
        icon="💧💫",
        blessing_a="mana_well",     # 마나 샘
        blessing_b="regeneration",  # 재생
        description="MP가 가득 차면 데미지 +50%, 턴당 MP 10% 회복",
        effect={
            "full_mp_damage_bonus": 0.5,  # MP 가득 시 +50%
            "mp_regen_percent": 0.1,      # 턴당 10% 회복
        },
    ),

    # 9. 분노의 화신 (광전사 + 가시)
    DuoBlessing(
        id="rage_incarnate",
        name="분노의 화신",
        icon="😤🔥",
        blessing_a="berserker",     # 광전사
        blessing_b="thorns",        # 가시
        description="피격 시 분노 스택, ATK +10% (최대 5스택)",
        effect={
            "hit_to_atk": 0.1,      # 피격 시 ATK +10%
            "max_rage_stacks": 5,   # 최대 5스택 (+50%)
        },
    ),

    # 10. 완전한 전사 (철벽 + 광전사)
    DuoBlessing(
        id="perfect_warrior",
        name="완전한 전사",
        icon="⚔️🛡️",
        blessing_a="iron_wall",     # 철벽
        blessing_b="berserker",     # 광전사
        description="공격력과 방어력 중 높은 값을 둘 다에 적용",
        effect={
            "sync_atk_def": True,  # ATK/DEF 동기화 (높은 값으로)
        },
    ),
]


def get_duo_by_id(duo_id: str) -> Optional[DuoBlessing]:
    """ID로 듀오 축복 찾기"""
    return next((d for d in DUO_BLESSINGS if d.id == duo_id), None)


def get_duo_by_blessings(blessing_a_id: str, blessing_b_id: str) -> Optional[DuoBlessing]:
    """두 축복 ID로 듀오 축복 찾기"""
    for duo in DUO_BLESSINGS:
        if (duo.blessing_a == blessing_a_id and duo.blessing_b == blessing_b_id) or \
           (duo.blessing_a == blessing_b_id and duo.blessing_b == blessing_a_id):
            return duo
    return None


def get_potential_duo(blessing_id: str, owned_blessing_ids: set[str]) -> Optional[DuoBlessing]:
    """보유 축복과 조합 가능한 듀오 찾기"""
    for duo in DUO_BLESSINGS:
        if duo.blessing_a == blessing_id and duo.blessing_b in owned_blessing_ids:
            return duo
        if duo.blessing_b == blessing_id and duo.blessing_a in owned_blessing_ids:
            return duo
    return None


def check_active_duos(owned_blessing_ids: set[str]) -> list[DuoBlessing]:
    """현재 활성화된 듀오 축복 목록"""
    active = []
    for duo in DUO_BLESSINGS:
        if duo.blessing_a in owned_blessing_ids and duo.blessing_b in owned_blessing_ids:
            active.append(duo)
    return active


def format_duo_hint(duo: DuoBlessing) -> str:
    """듀오 힌트 포맷 (발견 전에는 ??? 표시)"""
    return f"??? (특수 조합!)"


def format_duo_discovered(duo: DuoBlessing) -> str:
    """발견된 듀오 표시"""
    return f"{duo.icon} {duo.name}: {duo.description}"
