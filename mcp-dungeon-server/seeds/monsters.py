"""몬스터 시드 데이터"""
import json

# 일반 몬스터 (5층 구조) - v4.0 밸런스 대개편
# 전사 DEF 8 기준, 최소 5~10 데미지 발생하도록 ATK 상향
# 레벨업 기준: 4회 전투당 1레벨 상승, 필요 경험치 = 레벨 * 100
# v5.0: action_pattern (행동 예고제), element/weaknesses/resistances/immunities (속성 시스템)
NORMAL_MONSTERS = [
    # 1층: 하수도 (권장 레벨 1, 경험치 ~25/전투)
    # v4.0: ATK +5~7 (전사 DEF 8 기준 5~7 데미지)
    {"id": "rat", "name": "쥐", "floor_min": 1, "floor_max": 1,
     "hp": 22, "atk": 13, "def": 1, "exp": 22, "gold_min": 5, "gold_max": 12, "souls": 1,
     "action_pattern": ["attack", "attack", "attack"],  # 기본 공격만
     "drops": [("hp_potion_s", 0.18)]},
    {"id": "slime", "name": "슬라임", "floor_min": 1, "floor_max": 1,
     "hp": 30, "atk": 14, "def": 2, "exp": 24, "gold_min": 6, "gold_max": 14, "souls": 1,
     "action_pattern": ["attack", "attack", "defend"],  # 가끔 방어
     "weaknesses": ["fire", "lightning"], "resistances": ["physical"],
     "drops": [("slime_jelly", 0.22)]},
    {"id": "bat", "name": "박쥐", "floor_min": 1, "floor_max": 1,
     "hp": 18, "atk": 16, "def": 0, "exp": 20, "gold_min": 4, "gold_max": 10, "souls": 1,
     "action_pattern": ["attack", "attack", "heavy"],  # 빠른 공격 + 가끔 강타
     "drops": [("bat_wing", 0.18)]},
    {"id": "goblin", "name": "고블린", "floor_min": 1, "floor_max": 1,
     "hp": 35, "atk": 15, "def": 2, "exp": 30, "gold_min": 10, "gold_max": 18, "souls": 2,
     "action_pattern": ["attack", "attack", "attack", "heavy"],  # 공격 위주
     "drops": [("rusty_dagger", 0.10), ("hp_potion_s", 0.12)]},

    # 2층: 지하 감옥 (권장 레벨 3, 경험치 ~50/전투)
    # v4.0: ATK +6~8 (예상 DEF 10 기준 8~12 데미지)
    {"id": "skeleton", "name": "해골", "floor_min": 2, "floor_max": 2,
     "hp": 48, "atk": 18, "def": 3, "exp": 50, "gold_min": 15, "gold_max": 25, "souls": 3,
     "action_pattern": ["attack", "attack", "defend", "attack"],
     "weaknesses": ["holy", "fire"], "resistances": ["poison"], "immunities": ["poison"],
     "drops": [("bone", 0.28), ("old_sword", 0.06)]},
    {"id": "zombie", "name": "좀비", "floor_min": 2, "floor_max": 2,
     "hp": 62, "atk": 17, "def": 2, "exp": 52, "gold_min": 14, "gold_max": 22, "souls": 3,
     "action_pattern": ["attack", "attack", "attack", "heavy"],  # 느리지만 강력
     "weaknesses": ["holy", "fire"], "immunities": ["poison"],
     "drops": [("rotten_flesh", 0.32), ("hp_potion_m", 0.10)]},
    {"id": "ghost", "name": "유령", "floor_min": 2, "floor_max": 2,
     "hp": 40, "atk": 21, "def": 0, "exp": 58, "gold_min": 18, "gold_max": 28, "souls": 4,
     "action_pattern": ["attack", "debuff", "attack", "attack"],  # 디버프 사용
     "weaknesses": ["holy"], "resistances": ["physical"], "immunities": ["poison"],
     "element": "dark",
     "drops": [("ectoplasm", 0.22)]},
    {"id": "spider", "name": "거대 거미", "floor_min": 2, "floor_max": 2,
     "hp": 52, "atk": 19, "def": 4, "exp": 60, "gold_min": 16, "gold_max": 26, "souls": 3,
     "action_pattern": ["attack", "attack", "debuff", "attack"],  # 독 디버프
     "element": "poison",
     "drops": [("spider_silk", 0.28), ("poison_fang", 0.12)]},

    # 3층: 마석 광산 (권장 레벨 5, 경험치 ~85/전투)
    # v4.0: ATK +7~9 (예상 DEF 12 기준 10~15 데미지)
    {"id": "golem", "name": "석상 골렘", "floor_min": 3, "floor_max": 3,
     "hp": 90, "atk": 22, "def": 7, "exp": 82, "gold_min": 30, "gold_max": 50, "souls": 5,
     "action_pattern": ["defend", "attack", "attack", "charge", "heavy"],  # 충전→강타
     "resistances": ["physical", "fire"], "immunities": ["poison"],
     "drops": [("stone_core", 0.18), ("iron_ore", 0.32)]},
    {"id": "dark_mage", "name": "암흑 마법사", "floor_min": 3, "floor_max": 3,
     "hp": 58, "atk": 25, "def": 3, "exp": 92, "gold_min": 35, "gold_max": 55, "souls": 6,
     "action_pattern": ["buff", "attack", "attack", "special"],  # 버프 후 공격
     "element": "dark", "weaknesses": ["holy"],
     "drops": [("magic_crystal", 0.15), ("mp_potion_m", 0.18)]},
    {"id": "orc", "name": "오크 전사", "floor_min": 3, "floor_max": 3,
     "hp": 80, "atk": 23, "def": 5, "exp": 85, "gold_min": 32, "gold_max": 52, "souls": 5,
     "action_pattern": ["attack", "attack", "charge", "heavy", "attack"],  # 충전→강타
     "drops": [("orc_tusk", 0.22), ("steel_axe", 0.06)]},
    {"id": "mimic", "name": "미믹", "floor_min": 3, "floor_max": 3,
     "hp": 70, "atk": 22, "def": 6, "exp": 98, "gold_min": 60, "gold_max": 100, "souls": 7,
     "action_pattern": ["attack", "attack", "heavy", "defend"],  # 기습형
     "drops": [("gold_tooth", 0.35), ("rare_gem", 0.10)]},

    # 4층: 심연의 사원 (권장 레벨 7, 경험치 ~120/전투)
    # v4.0: ATK +8~10 (예상 DEF 14 기준 12~18 데미지)
    {"id": "demon", "name": "하급 악마", "floor_min": 4, "floor_max": 4,
     "hp": 100, "atk": 27, "def": 7, "exp": 115, "gold_min": 50, "gold_max": 80, "souls": 8,
     "action_pattern": ["attack", "attack", "buff", "heavy", "attack"],
     "element": "fire", "weaknesses": ["holy", "ice"], "resistances": ["fire"],
     "drops": [("demon_horn", 0.18), ("hp_potion_l", 0.12)]},
    {"id": "cultist", "name": "광신도", "floor_min": 4, "floor_max": 4,
     "hp": 75, "atk": 29, "def": 5, "exp": 110, "gold_min": 45, "gold_max": 70, "souls": 7,
     "action_pattern": ["debuff", "attack", "attack", "heal", "attack"],  # 디버프+회복
     "element": "dark", "weaknesses": ["holy"],
     "drops": [("cursed_tome", 0.12), ("ritual_dagger", 0.10)]},
    {"id": "gargoyle", "name": "가고일", "floor_min": 4, "floor_max": 4,
     "hp": 110, "atk": 25, "def": 10, "exp": 125, "gold_min": 55, "gold_max": 85, "souls": 8,
     "action_pattern": ["defend", "attack", "attack", "charge", "heavy"],  # 방어형
     "resistances": ["physical"], "immunities": ["poison"],
     "drops": [("gargoyle_wing", 0.20), ("stone_heart", 0.06)]},
    {"id": "wraith", "name": "원혼", "floor_min": 4, "floor_max": 4,
     "hp": 85, "atk": 31, "def": 2, "exp": 130, "gold_min": 60, "gold_max": 95, "souls": 10,
     "action_pattern": ["attack", "debuff", "attack", "special"],  # 디버프+특수
     "element": "dark", "weaknesses": ["holy"], "resistances": ["physical"],
     "immunities": ["poison"],
     "drops": [("soul_essence", 0.22), ("ghost_cloak", 0.04)]},

    # 5층: 던전 심층부 (권장 레벨 9, 경험치 ~160/전투)
    # v4.0: ATK +10~12 (예상 DEF 16 기준 16~22 데미지)
    {"id": "dark_knight", "name": "암흑 기사", "floor_min": 5, "floor_max": 5,
     "hp": 140, "atk": 34, "def": 12, "exp": 155, "gold_min": 75, "gold_max": 110, "souls": 12,
     "action_pattern": ["attack", "defend", "attack", "charge", "heavy", "attack"],
     "element": "dark", "resistances": ["dark"],
     "drops": [("dark_steel", 0.22), ("knight_helm", 0.06)]},
    {"id": "lich", "name": "리치", "floor_min": 5, "floor_max": 5,
     "hp": 100, "atk": 38, "def": 6, "exp": 180, "gold_min": 85, "gold_max": 120, "souls": 15,
     "action_pattern": ["buff", "attack", "debuff", "attack", "special", "heal"],
     "element": "dark", "weaknesses": ["holy", "fire"], "immunities": ["poison", "dark"],
     "drops": [("phylactery_shard", 0.12), ("arcane_staff", 0.04)]},
    {"id": "dragon_spawn", "name": "드래곤 스폰", "floor_min": 5, "floor_max": 5,
     "hp": 160, "atk": 36, "def": 10, "exp": 170, "gold_min": 95, "gold_max": 140, "souls": 14,
     "action_pattern": ["attack", "attack", "charge", "heavy", "attack", "special"],
     "element": "fire", "weaknesses": ["ice"], "resistances": ["fire"],
     "drops": [("dragon_scale", 0.18), ("fire_essence", 0.14)]},
    {"id": "void_walker", "name": "공허의 방랑자", "floor_min": 5, "floor_max": 5,
     "hp": 120, "atk": 40, "def": 4, "exp": 190, "gold_min": 90, "gold_max": 130, "souls": 16,
     "action_pattern": ["special", "attack", "debuff", "attack", "charge", "heavy"],
     "element": "dark", "weaknesses": ["holy"], "resistances": ["physical", "dark"],
     "drops": [("void_crystal", 0.14), ("reality_shard", 0.06)]},
]

# 엘리트 몬스터 (각 층별 1종) - v4.0: 5층 구조, ATK 대폭 상향
# 일반 몬스터 대비 HP 2배, ATK 1.5배, 경험치 2배
# 출현율: 25% (config.py ELITE_SPAWN_RATE)
# v5.0: 엘리트는 더 복잡한 행동 패턴
ELITE_MONSTERS = [
    # 1층 엘리트: v4.0 ATK 22 (일반 15 × 1.5)
    {"id": "elite_goblin_chief", "name": "고블린 족장", "floor_min": 1, "floor_max": 1,
     "hp": 70, "atk": 22, "def": 3, "exp": 65, "gold_min": 30, "gold_max": 50, "souls": 10,
     "action_pattern": ["attack", "buff", "attack", "attack", "charge", "heavy"],
     "skills": ["power_strike"], "drops": [("goblin_crown", 0.55), ("hp_potion_m", 0.35)]},
    # 2층 엘리트: v4.0 ATK 28 (일반 19 × 1.5)
    {"id": "elite_bone_lord", "name": "해골 군주", "floor_min": 2, "floor_max": 2,
     "hp": 105, "atk": 28, "def": 5, "exp": 120, "gold_min": 50, "gold_max": 75, "souls": 15,
     "action_pattern": ["attack", "defend", "attack", "buff", "charge", "heavy"],
     "weaknesses": ["holy", "fire"], "immunities": ["poison"],
     "skills": ["bone_shield"], "drops": [("lord_skull", 0.55), ("bone_armor", 0.25)]},
    # 3층 엘리트: v4.0 ATK 34 (일반 23 × 1.5)
    {"id": "elite_crystal_golem", "name": "수정 골렘", "floor_min": 3, "floor_max": 3,
     "hp": 150, "atk": 34, "def": 10, "exp": 185, "gold_min": 75, "gold_max": 110, "souls": 22,
     "action_pattern": ["defend", "attack", "attack", "charge", "heavy", "defend"],
     "resistances": ["physical", "fire"], "immunities": ["poison"],
     "skills": ["crystal_shield", "slam"], "drops": [("crystal_core", 0.55), ("rare_gem", 0.30)]},
    # 4층 엘리트: v4.0 ATK 42 (일반 28 × 1.5)
    {"id": "elite_arch_demon", "name": "상급 악마", "floor_min": 4, "floor_max": 4,
     "hp": 185, "atk": 42, "def": 8, "exp": 250, "gold_min": 100, "gold_max": 150, "souls": 30,
     "action_pattern": ["buff", "attack", "attack", "special", "charge", "heavy"],
     "element": "fire", "weaknesses": ["holy", "ice"], "resistances": ["fire", "dark"],
     "skills": ["hellfire", "dark_pact"], "drops": [("demon_heart", 0.55), ("infernal_blade", 0.12)]},
    # 5층 엘리트: v4.0 ATK 55 (일반 37 × 1.5)
    {"id": "elite_death_knight", "name": "죽음의 기사", "floor_min": 5, "floor_max": 5,
     "hp": 240, "atk": 55, "def": 14, "exp": 350, "gold_min": 130, "gold_max": 180, "souls": 40,
     "action_pattern": ["attack", "defend", "attack", "debuff", "charge", "heavy", "heal"],
     "element": "dark", "weaknesses": ["holy"], "resistances": ["dark", "poison"],
     "skills": ["death_strike", "unholy_aura"], "drops": [("death_essence", 0.55), ("cursed_blade", 0.18)]},
]

# 보스 몬스터 - v4.0: 5층 구조, ATK 대폭 상향
# DEF 감소: 전투 시간 단축, HP로 난이도 조절
# 1~4층: 50% 확률 등장, 5층: 100% 등장
# v5.0: 보스는 가장 복잡한 행동 패턴 + 페이즈 변화
BOSS_MONSTERS = [
    # 1층 보스 (50% 확률로 등장) - v4.0: ATK 20
    {"id": "boss_slime_king", "name": "슬라임 킹", "floor_min": 1, "floor_max": 1,
     "hp": 80, "atk": 20, "def": 1, "exp": 90, "gold_min": 50, "gold_max": 80, "souls": 15,
     "action_pattern": ["attack", "attack", "defend", "attack", "buff", "heavy"],
     "weaknesses": ["fire", "lightning"], "resistances": ["physical"],
     "skills": ["split", "absorb"],
     "pattern": {"phase1": {"hp_percent": 50, "action": "split"}},
     "drops": [("slime_core", 1.0), ("hp_potion_m", 0.30)]},

    {"id": "boss_rat_king", "name": "쥐 왕", "floor_min": 1, "floor_max": 1,
     "hp": 70, "atk": 18, "def": 2, "exp": 85, "gold_min": 45, "gold_max": 75, "souls": 14,
     "action_pattern": ["attack", "attack", "debuff", "attack", "charge", "heavy"],
     "element": "poison",
     "skills": ["summon_rats", "plague_bite"],
     "pattern": {"phase1": {"hp_percent": 50, "action": "summon_rats"},
                 "phase2": {"hp_percent": 25, "buff": {"atk_mult": 1.3}}},
     "drops": [("rat_king_crown", 1.0), ("hp_potion_m", 0.50)]},

    # 2층 보스 (50% 확률로 등장) - v4.0: ATK 26~28
    {"id": "boss_giant_spider", "name": "여왕 거미", "floor_min": 2, "floor_max": 2,
     "hp": 130, "atk": 26, "def": 3, "exp": 140, "gold_min": 80, "gold_max": 120, "souls": 25,
     "action_pattern": ["attack", "debuff", "attack", "attack", "charge", "heavy"],
     "element": "poison",
     "skills": ["web_trap", "poison_fang"],
     "pattern": {"phase1": {"hp_percent": 60, "action": "web_trap"},
                 "phase2": {"hp_percent": 30, "buff": {"atk_mult": 1.2}}},
     "drops": [("spider_silk", 1.0), ("venom_gland", 0.40)]},

    {"id": "boss_skeleton_general", "name": "해골 장군", "floor_min": 2, "floor_max": 2,
     "hp": 140, "atk": 28, "def": 4, "exp": 150, "gold_min": 90, "gold_max": 130, "souls": 28,
     "action_pattern": ["attack", "buff", "attack", "attack", "charge", "heavy", "defend"],
     "weaknesses": ["holy", "fire"], "immunities": ["poison"],
     "skills": ["sword_dance", "bone_storm", "rally"],
     "pattern": {"phase1": {"hp_percent": 60, "action": "rally"},
                 "phase2": {"hp_percent": 30, "action": "bone_storm"}},
     "drops": [("general_sword", 1.0), ("skeleton_shield", 0.50)]},

    # 3층 보스 (50% 확률로 등장) - v4.0: ATK 32~35
    {"id": "boss_orc_warlord", "name": "오크 대족장", "floor_min": 3, "floor_max": 3,
     "hp": 180, "atk": 32, "def": 5, "exp": 200, "gold_min": 120, "gold_max": 180, "souls": 40,
     "action_pattern": ["buff", "attack", "attack", "charge", "heavy", "attack", "heal"],
     "skills": ["war_cry", "brutal_slam", "enrage"],
     "pattern": {"phase1": {"hp_percent": 70, "action": "war_cry"},
                 "phase2": {"hp_percent": 40, "action": "enrage"}},
     "drops": [("warlord_axe", 1.0), ("orc_trophy", 0.45)]},

    {"id": "boss_crystal_guardian", "name": "수정 수호자", "floor_min": 3, "floor_max": 3,
     "hp": 200, "atk": 35, "def": 8, "exp": 220, "gold_min": 140, "gold_max": 200, "souls": 45,
     "action_pattern": ["defend", "attack", "attack", "special", "charge", "heavy", "defend"],
     "resistances": ["physical", "fire"], "immunities": ["poison"],
     "skills": ["crystal_barrage", "mirror_shield", "shatter"],
     "pattern": {"phase1": {"hp_percent": 70, "action": "mirror_shield"},
                 "phase2": {"hp_percent": 40, "action": "crystal_barrage"},
                 "phase3": {"hp_percent": 15, "action": "shatter"}},
     "drops": [("guardian_core", 1.0), ("crystal_armor", 0.40)]},

    # 4층 보스 (50% 확률로 등장) - v4.0: ATK 40~45
    {"id": "boss_vampire_lord", "name": "뱀파이어 로드", "floor_min": 4, "floor_max": 4,
     "hp": 250, "atk": 40, "def": 6, "exp": 280, "gold_min": 180, "gold_max": 250, "souls": 60,
     "action_pattern": ["attack", "debuff", "attack", "heal", "charge", "heavy", "special"],
     "element": "dark", "weaknesses": ["holy", "fire"], "resistances": ["dark"],
     "skills": ["blood_drain", "bat_swarm", "charm"],
     "pattern": {"phase1": {"hp_percent": 75, "action": "charm"},
                 "phase2": {"hp_percent": 50, "action": "bat_swarm"},
                 "phase3": {"hp_percent": 25, "action": "blood_drain"}},
     "drops": [("vampire_fang", 1.0), ("blood_cape", 0.35)]},

    {"id": "boss_demon_lord", "name": "악마 군주", "floor_min": 4, "floor_max": 4,
     "hp": 280, "atk": 45, "def": 8, "exp": 320, "gold_min": 200, "gold_max": 280, "souls": 70,
     "action_pattern": ["buff", "attack", "attack", "special", "charge", "heavy", "heal"],
     "element": "fire", "weaknesses": ["holy", "ice"], "resistances": ["fire", "dark"],
     "skills": ["inferno", "soul_drain", "demon_summon", "dark_ritual"],
     "pattern": {"phase1": {"hp_percent": 75, "action": "demon_summon"},
                 "phase2": {"hp_percent": 50, "action": "dark_ritual"},
                 "phase3": {"hp_percent": 25, "buff": {"atk_mult": 1.5, "def_mult": 0.8}}},
     "drops": [("demon_lord_horn", 1.0), ("infernal_armor", 0.30)]},

    # 5층 최종 보스 (100% 등장) - v4.0: ATK 55~60
    {"id": "boss_lich_king", "name": "리치 왕", "floor_min": 5, "floor_max": 5,
     "hp": 350, "atk": 55, "def": 8, "exp": 400, "gold_min": 300, "gold_max": 400, "souls": 100,
     "action_pattern": ["debuff", "attack", "attack", "special", "charge", "heavy", "heal", "buff"],
     "element": "dark", "weaknesses": ["holy", "fire"], "immunities": ["poison", "dark"],
     "skills": ["death_bolt", "summon_undead", "soul_cage", "necrotic_aura"],
     "pattern": {"phase1": {"hp_percent": 80, "action": "summon_undead"},
                 "phase2": {"hp_percent": 50, "action": "necrotic_aura"},
                 "phase3": {"hp_percent": 20, "action": "soul_cage"}},
     "drops": [("lich_phylactery", 1.0), ("staff_of_death", 0.35)]},

    {"id": "boss_dungeon_master", "name": "던전 마스터", "floor_min": 5, "floor_max": 5,
     "hp": 400, "atk": 60, "def": 10, "exp": 500, "gold_min": 400, "gold_max": 500, "souls": 150,
     "action_pattern": ["buff", "attack", "special", "attack", "charge", "heavy", "debuff", "heal"],
     "element": "dark", "weaknesses": ["holy"], "resistances": ["physical", "fire", "ice", "dark"],
     "skills": ["reality_warp", "void_blast", "time_stop", "ultimate_power"],
     "pattern": {"phase1": {"hp_percent": 80, "action": "reality_warp"},
                 "phase2": {"hp_percent": 50, "action": "time_stop"},
                 "phase3": {"hp_percent": 25, "action": "ultimate_power"},
                 "enrage": {"hp_percent": 10, "buff": {"atk_mult": 2.0}}},
     "drops": [("dungeon_heart", 1.0), ("master_robe", 0.50), ("void_blade", 0.20)]},
]


async def seed_monsters(db) -> int:
    """몬스터 데이터 삽입"""
    count = 0

    # 일반 몬스터
    for m in NORMAL_MONSTERS:
        drops = m.pop("drops", [])
        action_pattern = m.get("action_pattern", ["attack"])
        element = m.get("element")
        weaknesses = m.get("weaknesses", [])
        resistances = m.get("resistances", [])
        immunities = m.get("immunities", [])
        await db.execute("""
            INSERT INTO monsters (id, name, type, floor_min, floor_max,
                hp, atk, def, exp, gold_min, gold_max, souls, skills, pattern,
                action_pattern, element, weaknesses, resistances, immunities)
            VALUES (?, ?, 'normal', ?, ?, ?, ?, ?, ?, ?, ?, ?, '[]', NULL, ?, ?, ?, ?, ?)
        """, (
            m["id"], m["name"], m["floor_min"], m["floor_max"],
            m["hp"], m["atk"], m["def"], m["exp"],
            m["gold_min"], m["gold_max"], m["souls"],
            json.dumps(action_pattern),
            element,
            json.dumps(weaknesses),
            json.dumps(resistances),
            json.dumps(immunities)
        ))
        m["drops"] = drops  # 복원
        await _insert_drops(db, m["id"], drops)
        count += 1

    # 엘리트 몬스터
    for m in ELITE_MONSTERS:
        drops = m.pop("drops", [])
        skills = m.get("skills", [])
        action_pattern = m.get("action_pattern", ["attack"])
        element = m.get("element")
        weaknesses = m.get("weaknesses", [])
        resistances = m.get("resistances", [])
        immunities = m.get("immunities", [])
        await db.execute("""
            INSERT INTO monsters (id, name, type, floor_min, floor_max,
                hp, atk, def, exp, gold_min, gold_max, souls, skills, pattern,
                action_pattern, element, weaknesses, resistances, immunities)
            VALUES (?, ?, 'elite', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?)
        """, (
            m["id"], m["name"], m["floor_min"], m["floor_max"],
            m["hp"], m["atk"], m["def"], m["exp"],
            m["gold_min"], m["gold_max"], m["souls"],
            json.dumps(skills),
            json.dumps(action_pattern),
            element,
            json.dumps(weaknesses),
            json.dumps(resistances),
            json.dumps(immunities)
        ))
        m["drops"] = drops
        await _insert_drops(db, m["id"], drops)
        count += 1

    # 보스 몬스터
    for m in BOSS_MONSTERS:
        drops = m.pop("drops", [])
        skills = m.get("skills", [])
        pattern = m.get("pattern")
        action_pattern = m.get("action_pattern", ["attack"])
        element = m.get("element")
        weaknesses = m.get("weaknesses", [])
        resistances = m.get("resistances", [])
        immunities = m.get("immunities", [])
        await db.execute("""
            INSERT INTO monsters (id, name, type, floor_min, floor_max,
                hp, atk, def, exp, gold_min, gold_max, souls, skills, pattern,
                action_pattern, element, weaknesses, resistances, immunities)
            VALUES (?, ?, 'boss', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m["id"], m["name"], m["floor_min"], m["floor_max"],
            m["hp"], m["atk"], m["def"], m["exp"],
            m["gold_min"], m["gold_max"], m["souls"],
            json.dumps(skills),
            json.dumps(pattern) if pattern else None,
            json.dumps(action_pattern),
            element,
            json.dumps(weaknesses),
            json.dumps(resistances),
            json.dumps(immunities)
        ))
        m["drops"] = drops
        await _insert_drops(db, m["id"], drops)
        count += 1

    return count


async def _insert_drops(db, monster_id: str, drops: list) -> None:
    """몬스터 드롭 아이템 삽입"""
    for item_id, chance in drops:
        await db.execute("""
            INSERT INTO monster_drops (monster_id, item_id, drop_chance)
            VALUES (?, ?, ?)
        """, (monster_id, item_id, chance))
