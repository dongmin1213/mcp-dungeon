"""아이템 시드 데이터"""
import json

# 무기 (8종) - 가격 및 스탯 조정됨
WEAPONS = [
    {"id": "rusty_dagger", "name": "녹슨 단검", "grade": "common",
     "description": "녹이 슬었지만 아직 쓸만하다.",
     "price": 25, "floor_min": 1, "floor_max": 3,
     "stat_atk": 3, "stat_def": 0, "stat_hp": 0, "stat_mp": 0},
    {"id": "old_sword", "name": "낡은 검", "grade": "common",
     "description": "오래된 검. 기본적인 성능을 갖추고 있다.",
     "price": 50, "floor_min": 1, "floor_max": 4,
     "stat_atk": 5, "stat_def": 0, "stat_hp": 0, "stat_mp": 0},
    {"id": "steel_sword", "name": "강철 검", "grade": "uncommon",
     "description": "잘 단련된 강철로 만든 검.",
     "price": 120, "floor_min": 3, "floor_max": 5,
     "stat_atk": 8, "stat_def": 0, "stat_hp": 0, "stat_mp": 0},
    {"id": "steel_axe", "name": "강철 도끼", "grade": "uncommon",
     "description": "묵직한 강철 도끼. 파괴력이 강하다.",
     "price": 150, "floor_min": 4, "floor_max": 5,
     "stat_atk": 10, "stat_def": -1, "stat_hp": 0, "stat_mp": 0},
    {"id": "magic_staff", "name": "마법 지팡이", "grade": "uncommon",
     "description": "마력이 깃든 지팡이.",
     "price": 160, "floor_min": 3, "floor_max": 5,
     "stat_atk": 6, "stat_def": 0, "stat_hp": 0, "stat_mp": 20},
    {"id": "ritual_dagger", "name": "의식용 단검", "grade": "rare",
     "description": "사악한 의식에 사용된 단검. 저주가 느껴진다.",
     "price": 280, "floor_min": 4, "floor_max": 5,
     "stat_atk": 12, "stat_def": 0, "stat_hp": -10, "stat_mp": 10,
     "effect": {"crit_bonus": 0.05}},
    {"id": "infernal_blade", "name": "지옥의 검", "grade": "rare",
     "description": "지옥불로 단련된 검. 불길이 타오른다.",
     "price": 480, "floor_min": 5, "floor_max": 5,
     "stat_atk": 15, "stat_def": 0, "stat_hp": 0, "stat_mp": 0,
     "effect": {"fire_damage": 5}},
    {"id": "void_blade", "name": "공허의 검", "grade": "legendary",
     "description": "공허의 힘이 담긴 전설의 검.",
     "price": 1200, "floor_min": 5, "floor_max": 5,
     "stat_atk": 22, "stat_def": 2, "stat_hp": 0, "stat_mp": 0,
     "effect": {"void_damage": 8, "crit_bonus": 0.10}},
]

# 방어구 (6종) - 가격 조정됨
ARMORS = [
    {"id": "leather_armor", "name": "가죽 갑옷", "grade": "common",
     "description": "기본적인 가죽 갑옷.",
     "price": 40, "floor_min": 1, "floor_max": 3,
     "stat_atk": 0, "stat_def": 3, "stat_hp": 0, "stat_mp": 0},
    {"id": "chainmail", "name": "사슬 갑옷", "grade": "uncommon",
     "description": "촘촘한 사슬로 엮은 갑옷.",
     "price": 120, "floor_min": 3, "floor_max": 5,
     "stat_atk": 0, "stat_def": 6, "stat_hp": 10, "stat_mp": 0},
    {"id": "bone_armor", "name": "뼈 갑옷", "grade": "uncommon",
     "description": "몬스터의 뼈로 만든 갑옷. 으스스하다.",
     "price": 160, "floor_min": 4, "floor_max": 5,
     "stat_atk": 2, "stat_def": 7, "stat_hp": 0, "stat_mp": 0},
    {"id": "steel_plate", "name": "강철 판금 갑옷", "grade": "rare",
     "description": "두꺼운 강철판으로 만든 갑옷.",
     "price": 320, "floor_min": 5, "floor_max": 5,
     "stat_atk": 0, "stat_def": 10, "stat_hp": 20, "stat_mp": 0},
    {"id": "crystal_armor", "name": "수정 갑옷", "grade": "rare",
     "description": "마법 수정으로 강화된 갑옷.",
     "price": 550, "floor_min": 5, "floor_max": 5,
     "stat_atk": 0, "stat_def": 12, "stat_hp": 15, "stat_mp": 15},
    {"id": "infernal_armor", "name": "지옥의 갑옷", "grade": "legendary",
     "description": "지옥에서 온 전설의 갑옷.",
     "price": 950, "floor_min": 5, "floor_max": 5,
     "stat_atk": 3, "stat_def": 18, "stat_hp": 30, "stat_mp": 0,
     "effect": {"fire_resist": 0.3}},
    # Phase 1A: 시너지용 신규 아이템
    {"id": "thorn_armor", "name": "가시 갑옷", "grade": "rare",
     "description": "날카로운 가시가 돋아난 갑옷. 공격자에게 피해를 반사한다.",
     "price": 380, "floor_min": 3, "floor_max": 5,
     "stat_atk": 0, "stat_def": 8, "stat_hp": 15, "stat_mp": 0,
     "effect": {"reflect_damage": 0.2}},  # 20% 반사
]

# 투구 (4종) - 가격 조정됨
HELMETS = [
    {"id": "leather_cap", "name": "가죽 모자", "grade": "common",
     "description": "간단한 가죽 모자.",
     "price": 25, "floor_min": 1, "floor_max": 4,
     "stat_atk": 0, "stat_def": 1, "stat_hp": 5, "stat_mp": 0},
    {"id": "iron_helm", "name": "철제 투구", "grade": "uncommon",
     "description": "철로 만든 기본적인 투구.",
     "price": 80, "floor_min": 3, "floor_max": 5,
     "stat_atk": 0, "stat_def": 3, "stat_hp": 10, "stat_mp": 0},
    {"id": "knight_helm", "name": "기사의 투구", "grade": "rare",
     "description": "정예 기사가 착용하던 투구.",
     "price": 280, "floor_min": 4, "floor_max": 5,
     "stat_atk": 0, "stat_def": 5, "stat_hp": 20, "stat_mp": 0},
    {"id": "crown_of_shadows", "name": "그림자의 왕관", "grade": "legendary",
     "description": "어둠의 힘이 깃든 왕관.",
     "price": 650, "floor_min": 5, "floor_max": 5,
     "stat_atk": 4, "stat_def": 4, "stat_hp": 15, "stat_mp": 25,
     "effect": {"shadow_cloak": 0.1}},
]

# 장신구 (6종) - 가격 조정됨
ACCESSORIES = [
    {"id": "lucky_coin", "name": "행운의 동전", "grade": "common",
     "description": "행운을 가져다 준다는 동전.",
     "price": 65, "floor_min": 1, "floor_max": 5,
     "stat_atk": 0, "stat_def": 0, "stat_hp": 0, "stat_mp": 0,
     "effect": {"luck_bonus": 0.05}},
    {"id": "ring_of_strength", "name": "힘의 반지", "grade": "uncommon",
     "description": "착용자의 힘을 증폭시킨다.",
     "price": 160, "floor_min": 3, "floor_max": 5,
     "stat_atk": 4, "stat_def": 0, "stat_hp": 0, "stat_mp": 0},
    {"id": "amulet_of_protection", "name": "수호의 목걸이", "grade": "uncommon",
     "description": "착용자를 보호하는 마법이 담겨있다.",
     "price": 160, "floor_min": 3, "floor_max": 5,
     "stat_atk": 0, "stat_def": 4, "stat_hp": 10, "stat_mp": 0},
    {"id": "mana_crystal", "name": "마나 수정", "grade": "rare",
     "description": "순수한 마나가 응축된 수정.",
     "price": 320, "floor_min": 4, "floor_max": 5,
     "stat_atk": 0, "stat_def": 0, "stat_hp": 0, "stat_mp": 40},
    {"id": "vampiric_ring", "name": "흡혈의 반지", "grade": "rare",
     "description": "적에게 가한 데미지의 일부를 흡수한다.",
     "price": 400, "floor_min": 5, "floor_max": 5,
     "stat_atk": 2, "stat_def": 0, "stat_hp": 0, "stat_mp": 0,
     "effect": {"lifesteal": 0.1}},
    {"id": "masters_pendant", "name": "마스터의 펜던트", "grade": "legendary",
     "description": "던전 마스터가 지녔던 펜던트.",
     "price": 800, "floor_min": 5, "floor_max": 5,
     "stat_atk": 5, "stat_def": 5, "stat_hp": 25, "stat_mp": 25,
     "effect": {"all_stats_mult": 1.1}},
    # Phase 1A: 시너지용 신규 아이템
    {"id": "taunt_shield", "name": "도발의 방패", "grade": "rare",
     "description": "적의 시선을 끄는 마법이 깃든 방패. 모든 공격이 당신에게 집중된다.",
     "price": 350, "floor_min": 3, "floor_max": 5,
     "stat_atk": 0, "stat_def": 6, "stat_hp": 20, "stat_mp": 0,
     "effect": {"taunt": True, "aggro_bonus": 1.0}},
    {"id": "fire_ring", "name": "화염의 반지", "grade": "rare",
     "description": "불꽃이 타오르는 반지. 화염 속성을 강화한다.",
     "price": 420, "floor_min": 4, "floor_max": 5,
     "stat_atk": 4, "stat_def": 0, "stat_hp": 0, "stat_mp": 10,
     "effect": {"fire_damage": 8, "fire_resist": 0.2}},
    {"id": "ice_ring", "name": "냉기의 반지", "grade": "rare",
     "description": "서리가 맺힌 반지. 냉기 속성을 강화한다.",
     "price": 420, "floor_min": 4, "floor_max": 5,
     "stat_atk": 3, "stat_def": 0, "stat_hp": 0, "stat_mp": 15,
     "effect": {"ice_damage": 6, "slow_chance": 0.2}},
    {"id": "poison_ring", "name": "독의 반지", "grade": "rare",
     "description": "독액이 스며든 반지. 독 효과를 강화한다.",
     "price": 380, "floor_min": 3, "floor_max": 5,
     "stat_atk": 2, "stat_def": 0, "stat_hp": 0, "stat_mp": 5,
     "effect": {"poison_damage": 5, "poison_chance": 0.25}},
]

# 소비 아이템 (8종) - 가격 조정됨
CONSUMABLES = [
    # v5.0 자원 긴장감: 포션 회복량 하향 조정
    {"id": "hp_potion_s", "name": "소형 HP 포션", "grade": "common",
     "description": "HP를 25 회복한다.",
     "price": 20, "floor_min": 1, "floor_max": 5,
     "effect": {"heal_hp": 25}},
    {"id": "hp_potion_m", "name": "중형 HP 포션", "grade": "uncommon",
     "description": "HP를 50 회복한다.",
     "price": 45, "floor_min": 3, "floor_max": 5,
     "effect": {"heal_hp": 50}},
    {"id": "hp_potion_l", "name": "대형 HP 포션", "grade": "rare",
     "description": "HP를 100 회복한다.",
     "price": 90, "floor_min": 4, "floor_max": 5,
     "effect": {"heal_hp": 100}},
    {"id": "mp_potion_s", "name": "소형 MP 포션", "grade": "common",
     "description": "MP를 15 회복한다.",
     "price": 25, "floor_min": 1, "floor_max": 5,
     "effect": {"heal_mp": 15}},
    {"id": "mp_potion_m", "name": "중형 MP 포션", "grade": "uncommon",
     "description": "MP를 35 회복한다.",
     "price": 55, "floor_min": 3, "floor_max": 5,
     "effect": {"heal_mp": 35}},
    {"id": "antidote", "name": "해독제", "grade": "common",
     "description": "독 상태를 치료한다.",
     "price": 30, "floor_min": 1, "floor_max": 5,
     "effect": {"cure": "poison"}},
    {"id": "smoke_bomb", "name": "연막탄", "grade": "uncommon",
     "description": "전투에서 확실하게 도망칠 수 있다.",
     "price": 60, "floor_min": 2, "floor_max": 5,
     "effect": {"guaranteed_flee": True}},
    {"id": "elixir", "name": "엘릭서", "grade": "legendary",
     "description": "HP와 MP를 전부 회복한다.",
     "price": 400, "floor_min": 5, "floor_max": 5,
     "effect": {"heal_hp": 9999, "heal_mp": 9999}},
]

# 특수 아이템 (4종) - 퀘스트/이벤트용
SPECIAL_ITEMS = [
    {"id": "old_map", "name": "낡은 지도", "grade": "rare",
     "description": "현재 층의 모든 방을 공개한다.",
     "price": 200, "floor_min": 1, "floor_max": 5,
     "effect": {"reveal_map": True}},
    {"id": "teleport_stone", "name": "귀환석", "grade": "rare",
     "description": "시작 방으로 즉시 이동한다.",
     "price": 150, "floor_min": 1, "floor_max": 5,
     "effect": {"teleport": "start"}},
    {"id": "lucky_dice", "name": "행운의 주사위", "grade": "rare",
     "description": "사용 시 랜덤한 효과가 발생한다. 행운을 시험해보자!",
     "price": 100, "floor_min": 1, "floor_max": 5,
     "effect": {"random_dice": True}},
    {"id": "dungeon_key", "name": "던전 열쇠", "grade": "legendary",
     "description": "비밀 방으로 가는 문을 연다.",
     "price": 0, "floor_min": 1, "floor_max": 5,
     "effect": {"unlock_secret": True}},
]

# v5.0 저주받은 아이템 (강력하지만 페널티)
CURSED_ITEMS = [
    # 저주받은 무기
    {"id": "cursed_greatsword", "name": "저주받은 대검", "type": "weapon", "grade": "cursed",
     "description": "어둠의 힘이 깃든 대검. 강력하지만 생명력을 갉아먹는다.",
     "price": 0, "floor_min": 2, "floor_max": 5,
     "stat_atk": 15, "stat_def": 0, "stat_hp": 0, "stat_mp": 0,
     "curse": {"rest_heal_mult": 0.5}},  # 휴식 회복량 -50%

    {"id": "bloodthirst_blade", "name": "갈증의 검", "type": "weapon", "grade": "cursed",
     "description": "피에 굶주린 검. 적을 베지 않으면 자신을 벤다.",
     "price": 0, "floor_min": 3, "floor_max": 5,
     "stat_atk": 18, "stat_def": 0, "stat_hp": 0, "stat_mp": 0,
     "effect": {"lifesteal": 0.15},
     "curse": {"no_combat_damage": 5}},  # 전투 없이 방 이동 시 5 데미지

    {"id": "glass_cannon", "name": "유리 대포", "type": "weapon", "grade": "cursed",
     "description": "압도적인 파괴력을 지녔지만 방어력이 0이 된다.",
     "price": 0, "floor_min": 4, "floor_max": 5,
     "stat_atk": 25, "stat_def": 0, "stat_hp": 0, "stat_mp": 0,
     "curse": {"set_def_zero": True}},  # DEF = 0

    # 저주받은 방어구
    {"id": "pain_armor", "name": "고통의 갑옷", "type": "armor", "grade": "cursed",
     "description": "착용자에게 끊임없는 고통을 주지만 강력한 방어력을 제공한다.",
     "price": 0, "floor_min": 3, "floor_max": 5,
     "stat_atk": 0, "stat_def": 15, "stat_hp": 0, "stat_mp": 0,
     "curse": {"damage_per_turn": 3}},  # 매 턴 3 데미지

    {"id": "heavy_destiny", "name": "운명의 족쇄", "type": "armor", "grade": "cursed",
     "description": "엄청난 방어력을 주지만 도망칠 수 없게 된다.",
     "price": 0, "floor_min": 2, "floor_max": 5,
     "stat_atk": 0, "stat_def": 12, "stat_hp": 30, "stat_mp": 0,
     "curse": {"no_flee": True}},  # 도망 불가

    # 저주받은 장신구
    {"id": "greed_ring", "name": "탐욕의 반지", "type": "accessory", "grade": "cursed",
     "description": "골드를 2배로 얻지만 상점 가격도 올라간다.",
     "price": 0, "floor_min": 1, "floor_max": 5,
     "stat_atk": 0, "stat_def": 0, "stat_hp": 0, "stat_mp": 0,
     "effect": {"gold_mult": 2.0},
     "curse": {"shop_price_mult": 1.5}},  # 상점 가격 +50%

    {"id": "madness_helm", "name": "광기의 투구", "type": "helmet", "grade": "cursed",
     "description": "광기가 크리티컬을 높이지만 받는 데미지도 증가한다.",
     "price": 0, "floor_min": 3, "floor_max": 5,
     "stat_atk": 5, "stat_def": 0, "stat_hp": 0, "stat_mp": 0,
     "effect": {"crit_bonus": 0.25},
     "curse": {"damage_taken_mult": 1.2}},  # 받는 데미지 +20%

    {"id": "soul_eater", "name": "영혼 착취자", "type": "accessory", "grade": "cursed",
     "description": "소울을 2배로 얻지만 최대 HP가 감소한다.",
     "price": 0, "floor_min": 2, "floor_max": 5,
     "stat_atk": 3, "stat_def": 0, "stat_hp": -20, "stat_mp": 0,
     "effect": {"soul_mult": 2.0},
     "curse": {"max_hp_penalty": 20}},  # 이미 stat_hp로 적용

    {"id": "berserker_amulet", "name": "광전사의 목걸이", "type": "accessory", "grade": "cursed",
     "description": "HP가 낮을수록 강해지지만 회복 아이템 효과가 감소한다.",
     "price": 0, "floor_min": 3, "floor_max": 5,
     "stat_atk": 5, "stat_def": 0, "stat_hp": 0, "stat_mp": 0,
     "effect": {"berserk": True},  # HP 30% 이하시 ATK +50%
     "curse": {"potion_heal_mult": 0.5}},  # 포션 회복량 -50%

    {"id": "chaos_orb", "name": "혼돈의 오브", "type": "accessory", "grade": "cursed",
     "description": "모든 스탯이 증가하지만 효과가 무작위로 변한다.",
     "price": 0, "floor_min": 4, "floor_max": 5,
     "stat_atk": 8, "stat_def": 5, "stat_hp": 20, "stat_mp": 20,
     "curse": {"random_effect_per_combat": True}},  # 전투마다 효과 변동
]

# 재료 아이템 (몬스터 드롭용)
MATERIALS = [
    {"id": "slime_jelly", "name": "슬라임 젤리", "grade": "common",
     "description": "슬라임에서 추출한 젤리.", "price": 5},
    {"id": "bat_wing", "name": "박쥐 날개", "grade": "common",
     "description": "박쥐의 날개.", "price": 5},
    {"id": "bone", "name": "뼈", "grade": "common",
     "description": "몬스터의 뼈.", "price": 8},
    {"id": "rotten_flesh", "name": "썩은 살점", "grade": "common",
     "description": "좀비의 살점. 역겹다.", "price": 3},
    {"id": "ectoplasm", "name": "에크토플라즘", "grade": "uncommon",
     "description": "유령의 잔해.", "price": 15},
    {"id": "spider_silk", "name": "거미줄", "grade": "common",
     "description": "질긴 거미줄.", "price": 10},
    {"id": "poison_fang", "name": "독니", "grade": "uncommon",
     "description": "독이 묻은 이빨.", "price": 20},
    {"id": "stone_core", "name": "돌 핵", "grade": "uncommon",
     "description": "골렘의 핵.", "price": 25},
    {"id": "iron_ore", "name": "철광석", "grade": "common",
     "description": "가공되지 않은 철.", "price": 12},
    {"id": "magic_crystal", "name": "마법 수정", "grade": "rare",
     "description": "마력이 담긴 수정.", "price": 50},
    {"id": "orc_tusk", "name": "오크 어금니", "grade": "uncommon",
     "description": "오크의 어금니.", "price": 18},
    {"id": "gold_tooth", "name": "금니", "grade": "rare",
     "description": "미믹에서 나온 금니.", "price": 40},
    {"id": "rare_gem", "name": "희귀 보석", "grade": "rare",
     "description": "가치 있는 보석.", "price": 80},
    {"id": "demon_horn", "name": "악마의 뿔", "grade": "rare",
     "description": "악마에서 떨어진 뿔.", "price": 60},
    {"id": "cursed_tome", "name": "저주받은 책", "grade": "rare",
     "description": "금지된 지식이 담긴 책.", "price": 70},
    {"id": "gargoyle_wing", "name": "가고일 날개", "grade": "rare",
     "description": "돌로 된 날개.", "price": 55},
    {"id": "stone_heart", "name": "돌 심장", "grade": "legendary",
     "description": "가고일의 심장.", "price": 150},
    {"id": "soul_essence", "name": "영혼 정수", "grade": "rare",
     "description": "원혼의 정수.", "price": 75},
    {"id": "ghost_cloak", "name": "유령의 망토", "grade": "legendary",
     "description": "유령이 입던 망토.", "price": 200},
    {"id": "dark_steel", "name": "암흑 강철", "grade": "rare",
     "description": "어둠에 물든 강철.", "price": 90},
    {"id": "phylactery_shard", "name": "필락터리 파편", "grade": "legendary",
     "description": "리치의 영혼이 담긴 파편.", "price": 180},
    {"id": "arcane_staff", "name": "비전 지팡이", "grade": "legendary",
     "description": "강력한 마법 지팡이.", "price": 250},
    {"id": "dragon_scale", "name": "용의 비늘", "grade": "legendary",
     "description": "드래곤의 비늘.", "price": 200},
    {"id": "fire_essence", "name": "불의 정수", "grade": "rare",
     "description": "불의 원소 정수.", "price": 85},
    {"id": "void_crystal", "name": "공허 수정", "grade": "legendary",
     "description": "공허의 힘이 담긴 수정.", "price": 220},
    {"id": "reality_shard", "name": "현실 파편", "grade": "legendary",
     "description": "현실 자체의 파편.", "price": 300},
    # 보스 드롭
    {"id": "rat_king_crown", "name": "쥐 왕의 왕관", "grade": "rare",
     "description": "쥐 왕이 쓰던 왕관.", "price": 100},
    {"id": "goblin_crown", "name": "고블린 왕관", "grade": "uncommon",
     "description": "고블린 족장의 왕관.", "price": 50},
    {"id": "lord_skull", "name": "군주의 해골", "grade": "rare",
     "description": "해골 군주의 머리.", "price": 80},
    {"id": "general_sword", "name": "장군의 검", "grade": "rare",
     "description": "해골 장군이 쓰던 검.", "price": 120},
    {"id": "skeleton_shield", "name": "해골 방패", "grade": "uncommon",
     "description": "뼈로 만든 방패.", "price": 60},
    {"id": "crystal_core", "name": "수정 핵", "grade": "rare",
     "description": "수정 골렘의 핵.", "price": 100},
    {"id": "guardian_core", "name": "수호자의 핵", "grade": "legendary",
     "description": "수정 수호자의 핵.", "price": 200},
    {"id": "demon_heart", "name": "악마의 심장", "grade": "legendary",
     "description": "상급 악마의 심장.", "price": 180},
    {"id": "demon_lord_horn", "name": "악마 군주의 뿔", "grade": "legendary",
     "description": "악마 군주의 거대한 뿔.", "price": 300},
    {"id": "death_essence", "name": "죽음의 정수", "grade": "legendary",
     "description": "죽음의 기사에서 얻은 정수.", "price": 250},
    {"id": "cursed_blade", "name": "저주받은 칼날", "grade": "legendary",
     "description": "저주가 깃든 칼날.", "price": 280},
    {"id": "dungeon_heart", "name": "던전의 심장", "grade": "legendary",
     "description": "던전 마스터의 힘의 원천.", "price": 500},
    {"id": "master_robe", "name": "마스터의 로브", "grade": "legendary",
     "description": "던전 마스터가 입던 로브.", "price": 400},
]


async def seed_items(db) -> int:
    """아이템 데이터 삽입"""
    count = 0
    all_items = []

    # 장비 아이템
    for item in WEAPONS:
        item["type"] = "weapon"
        all_items.append(item)
    for item in ARMORS:
        item["type"] = "armor"
        all_items.append(item)
    for item in HELMETS:
        item["type"] = "helmet"
        all_items.append(item)
    for item in ACCESSORIES:
        item["type"] = "accessory"
        all_items.append(item)

    # 소비 아이템
    for item in CONSUMABLES:
        item["type"] = "consumable"
        all_items.append(item)

    # 특수 아이템
    for item in SPECIAL_ITEMS:
        item["type"] = "special"
        all_items.append(item)

    # v5.0 저주받은 아이템
    for item in CURSED_ITEMS:
        all_items.append(item)

    # 재료 아이템
    for item in MATERIALS:
        item["type"] = "special"
        item.setdefault("floor_min", 1)
        item.setdefault("floor_max", 5)
        item.setdefault("stat_atk", 0)
        item.setdefault("stat_def", 0)
        item.setdefault("stat_hp", 0)
        item.setdefault("stat_mp", 0)
        all_items.append(item)

    # DB 삽입
    for item in all_items:
        effect = item.get("effect")
        curse = item.get("curse")
        await db.execute("""
            INSERT INTO items (id, name, type, grade, description, price,
                floor_min, floor_max, stat_atk, stat_def, stat_hp, stat_mp, effect, curse)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["id"], item["name"], item["type"], item["grade"],
            item["description"], item["price"],
            item.get("floor_min", 1), item.get("floor_max", 5),
            item.get("stat_atk", 0), item.get("stat_def", 0),
            item.get("stat_hp", 0), item.get("stat_mp", 0),
            json.dumps(effect) if effect else None,
            json.dumps(curse) if curse else None
        ))
        count += 1

    return count
