"""스킬 시드 데이터"""
import json

# v5.0 속성 시스템
# 속성: physical, fire, ice, lightning, poison, holy, dark
SKILLS = [
    # ===== 전사 스킬 =====
    {"id": "power_strike", "name": "강타", "type": "attack",
     "description": "강력한 일격으로 150% 데미지를 준다.",
     "mp_cost": 10, "cooldown": 0, "unlock_level": 1,
     "effect": {"damage_mult": 1.5},
     "element": "physical",  # v5.0
     "classes": ["warrior"]},
    {"id": "shield_bash", "name": "방패 강타", "type": "attack",
     "description": "방패로 적을 때려 100% 데미지 + 기절 확률 30%.",
     "mp_cost": 15, "cooldown": 2, "unlock_level": 3,
     "effect": {"damage_mult": 1.0, "stun_chance": 0.3},
     "element": "physical",  # v5.0
     "classes": ["warrior", "paladin"]},
    {"id": "war_cry", "name": "전투 함성", "type": "buff",
     "description": "3턴간 공격력 20% 증가.",
     "mp_cost": 20, "cooldown": 5, "unlock_level": 5,
     "effect": {"buff": {"atk_mult": 1.2, "duration": 3}},
     "classes": ["warrior"]},

    # ===== 궁수 스킬 =====
    {"id": "precise_shot", "name": "정밀 사격", "type": "attack",
     "description": "크리티컬 확률 100%로 120% 데미지.",
     "mp_cost": 15, "cooldown": 0, "unlock_level": 1,
     "effect": {"damage_mult": 1.2, "guaranteed_crit": True},
     "element": "physical",  # v5.0
     "classes": ["archer"]},
    {"id": "multi_shot", "name": "다중 사격", "type": "attack",
     "description": "3회 연속 공격, 각 70% 데미지.",
     "mp_cost": 20, "cooldown": 2, "unlock_level": 3,
     "effect": {"hits": 3, "damage_mult": 0.7},
     "element": "physical",  # v5.0
     "classes": ["archer"]},
    {"id": "evasion", "name": "회피 기동", "type": "buff",
     "description": "2턴간 회피율 50% 증가.",
     "mp_cost": 15, "cooldown": 4, "unlock_level": 5,
     "effect": {"buff": {"evasion": 0.5, "duration": 2}},
     "classes": ["archer", "rogue"]},

    # ===== 마법사 스킬 =====
    {"id": "fireball", "name": "파이어볼", "type": "attack",
     "description": "🔥 불덩이로 180% 마법 데미지. 언데드/냉기에 강함.",
     "mp_cost": 20, "cooldown": 0, "unlock_level": 1,
     "effect": {"damage_mult": 1.8, "magic_damage": True},
     "element": "fire",  # v5.0 화염 속성
     "classes": ["mage"]},
    {"id": "ice_lance", "name": "얼음 창", "type": "attack",
     "description": "🧊 얼음 창으로 140% 데미지 + 빙결 확률 25%. 화염/슬라임에 강함.",
     "mp_cost": 18, "cooldown": 1, "unlock_level": 3,
     "effect": {"damage_mult": 1.4, "freeze_chance": 0.25},
     "element": "ice",  # v5.0 냉기 속성
     "classes": ["mage"]},
    {"id": "mana_shield", "name": "마나 실드", "type": "buff",
     "description": "3턴간 받는 데미지의 50%를 MP로 대신 받음.",
     "mp_cost": 25, "cooldown": 5, "unlock_level": 5,
     "effect": {"buff": {"mana_shield": 0.5, "duration": 3}},
     "classes": ["mage"]},
    {"id": "lightning_bolt", "name": "번개 화살", "type": "attack",
     "description": "⚡ 번개로 160% 데미지. 금속/물 적에게 강함.",
     "mp_cost": 22, "cooldown": 1, "unlock_level": 4,
     "effect": {"damage_mult": 1.6},
     "element": "lightning",  # v5.0 번개 속성
     "classes": ["mage"]},

    # ===== 도적 스킬 =====
    {"id": "backstab", "name": "백스탭", "type": "attack",
     "description": "급소를 찔러 200% 데미지. 첫 턴에만 사용 가능.",
     "mp_cost": 15, "cooldown": 0, "unlock_level": 1,
     "effect": {"damage_mult": 2.0, "first_turn_only": True},
     "element": "physical",  # v5.0
     "classes": ["rogue"]},
    {"id": "poison_blade", "name": "독 칼날", "type": "attack",
     "description": "🟢 100% 데미지 + 3턴간 독 부여. 생물에게 강함, 언데드/골렘 면역.",
     "mp_cost": 12, "cooldown": 2, "unlock_level": 3,
     "effect": {"damage_mult": 1.0, "poison": {"damage": 5, "duration": 3}},
     "element": "poison",  # v5.0 독 속성
     "classes": ["rogue"]},
    {"id": "shadow_step", "name": "그림자 걸음", "type": "buff",
     "description": "다음 공격이 확정 크리티컬 + 회피 불가.",
     "mp_cost": 20, "cooldown": 4, "unlock_level": 5,
     "effect": {"buff": {"next_attack_crit": True, "unavoidable": True, "duration": 1}},
     "classes": ["rogue"]},

    # ===== 성기사 스킬 =====
    {"id": "holy_strike", "name": "신성한 일격", "type": "attack",
     "description": "✨ 신성한 힘으로 130% 데미지. 언데드/악마에게 강함.",
     "mp_cost": 15, "cooldown": 0, "unlock_level": 1,
     "effect": {"damage_mult": 1.3, "bonus_vs_undead": 2.0},
     "element": "holy",  # v5.0 신성 속성
     "classes": ["paladin"]},
    {"id": "heal", "name": "치유", "type": "heal",
     "description": "HP를 최대 HP의 30% 회복.",
     "mp_cost": 25, "cooldown": 3, "unlock_level": 3,
     "effect": {"heal_percent": 0.3},
     "classes": ["paladin"]},
    {"id": "divine_protection", "name": "신의 가호", "type": "buff",
     "description": "3턴간 받는 데미지 40% 감소.",
     "mp_cost": 30, "cooldown": 6, "unlock_level": 5,
     "effect": {"buff": {"damage_reduction": 0.4, "duration": 3}},
     "classes": ["paladin"]},
    {"id": "smite", "name": "천벌", "type": "attack",
     "description": "✨ 신성한 번개로 170% 데미지. 암흑 속성에 강함.",
     "mp_cost": 25, "cooldown": 2, "unlock_level": 4,
     "effect": {"damage_mult": 1.7},
     "element": "holy",  # v5.0 신성 속성
     "classes": ["paladin"]},

    # ===== 사신 스킬 =====
    {"id": "soul_reap", "name": "영혼 수확", "type": "attack",
     "description": "💀 160% 데미지 + 피해량의 20% HP 흡수. 신성에 강함.",
     "mp_cost": 18, "cooldown": 0, "unlock_level": 1,
     "effect": {"damage_mult": 1.6, "lifesteal": 0.2},
     "element": "dark",  # v5.0 암흑 속성
     "classes": ["reaper"]},
    {"id": "death_mark", "name": "죽음의 표식", "type": "debuff",
     "description": "적에게 표식 부여. 3턴 후 최대 HP 20% 데미지.",
     "mp_cost": 20, "cooldown": 4, "unlock_level": 3,
     "effect": {"mark": {"trigger_turn": 3, "damage_percent": 0.2}},
     "classes": ["reaper"]},
    {"id": "grim_harvest", "name": "죽음의 낫", "type": "attack",
     "description": "💀 적 HP가 25% 이하일 때 즉사. 아니면 250% 데미지.",
     "mp_cost": 35, "cooldown": 5, "unlock_level": 5,
     "effect": {"execute_threshold": 0.25, "damage_mult": 2.5},
     "element": "dark",  # v5.0 암흑 속성
     "classes": ["reaper"]},

    # ===== 공용 스킬 =====
    {"id": "focus", "name": "집중", "type": "buff",
     "description": "다음 공격의 크리티컬 확률 +30%.",
     "mp_cost": 8, "cooldown": 2, "unlock_level": 2,
     "effect": {"buff": {"crit_bonus": 0.3, "duration": 1}},
     "classes": ["warrior", "archer", "mage", "rogue", "paladin", "reaper"]},

    # ===== 몬스터 전용 스킬 =====
    {"id": "bone_shield", "name": "뼈 방패", "type": "buff",
     "description": "방어력 50% 증가 (2턴).",
     "mp_cost": 0, "cooldown": 3, "unlock_level": 1,
     "effect": {"buff": {"def_mult": 1.5, "duration": 2}},
     "classes": []},
    {"id": "crystal_shield", "name": "수정 방패", "type": "buff",
     "description": "모든 데미지 30% 반사 (2턴).",
     "mp_cost": 0, "cooldown": 4, "unlock_level": 1,
     "effect": {"buff": {"reflect": 0.3, "duration": 2}},
     "classes": []},
    {"id": "slam", "name": "내려찍기", "type": "attack",
     "description": "강력한 내려찍기 180% 데미지.",
     "mp_cost": 0, "cooldown": 2, "unlock_level": 1,
     "effect": {"damage_mult": 1.8},
     "element": "physical",
     "classes": []},
    {"id": "hellfire", "name": "지옥불", "type": "attack",
     "description": "지옥의 불꽃 200% 데미지 + 화상.",
     "mp_cost": 0, "cooldown": 3, "unlock_level": 1,
     "effect": {"damage_mult": 2.0, "burn": {"damage": 10, "duration": 3}},
     "element": "fire",  # v5.0 화염 속성
     "classes": []},
    {"id": "dark_pact", "name": "어둠의 계약", "type": "buff",
     "description": "HP 20% 소모, 공격력 50% 증가 (3턴).",
     "mp_cost": 0, "cooldown": 5, "unlock_level": 1,
     "effect": {"self_damage_percent": 0.2, "buff": {"atk_mult": 1.5, "duration": 3}},
     "classes": []},
    {"id": "death_strike", "name": "죽음의 일격", "type": "attack",
     "description": "250% 데미지 + HP 흡수 30%.",
     "mp_cost": 0, "cooldown": 4, "unlock_level": 1,
     "effect": {"damage_mult": 2.5, "lifesteal": 0.3},
     "element": "dark",  # v5.0 암흑 속성
     "classes": []},
    {"id": "unholy_aura", "name": "불경한 오라", "type": "debuff",
     "description": "플레이어 방어력 30% 감소 (3턴).",
     "mp_cost": 0, "cooldown": 5, "unlock_level": 1,
     "effect": {"debuff": {"def_mult": 0.7, "duration": 3}},
     "classes": []},
]


async def seed_skills(db) -> int:
    """스킬 데이터 삽입"""
    for s in SKILLS:
        element = s.get("element")  # v5.0 속성
        await db.execute("""
            INSERT INTO skills (id, name, description, type, mp_cost,
                cooldown, unlock_level, effect, classes, element)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s["id"], s["name"], s["description"], s["type"],
            s["mp_cost"], s["cooldown"], s["unlock_level"],
            json.dumps(s["effect"]), json.dumps(s["classes"]),
            element
        ))
    return len(SKILLS)
