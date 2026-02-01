"""이벤트 시드 데이터"""
import json

EVENTS = [
    # ===== 함정 이벤트 (5종) =====
    {
        "id": "spike_trap",
        "name": "가시 함정",
        "type": "trap",
        "description": "바닥에서 날카로운 가시가 솟아올랐다!",
        "floor_min": 1, "floor_max": 5,
        "effect": {"damage_percent": 0.15},  # 최대 HP의 15% 데미지
    },
    {
        "id": "poison_gas",
        "name": "독가스 함정",
        "type": "trap",
        "description": "녹색 독가스가 분출된다!",
        "floor_min": 3, "floor_max": 5,
        "effect": {"damage_flat": 20, "poison": {"damage": 5, "duration": 3}},
    },
    {
        "id": "arrow_trap",
        "name": "화살 함정",
        "type": "trap",
        "description": "벽에서 화살이 날아온다!",
        "floor_min": 2, "floor_max": 5,
        "effect": {"damage_percent": 0.20},
    },
    {
        "id": "pit_trap",
        "name": "낙하 함정",
        "type": "trap",
        "description": "바닥이 무너져 아래로 떨어졌다!",
        "floor_min": 4, "floor_max": 5,
        "effect": {"damage_percent": 0.25},
    },
    {
        "id": "curse_trap",
        "name": "저주 함정",
        "type": "trap",
        "description": "고대의 저주가 발동했다!",
        "floor_min": 5, "floor_max": 5,
        "effect": {"debuff": {"atk_mult": 0.8, "def_mult": 0.8, "duration": 10}},
    },

    # ===== 보물 이벤트 (3종) =====
    {
        "id": "small_chest",
        "name": "작은 상자",
        "type": "treasure",
        "description": "먼지 쌓인 작은 상자를 발견했다.",
        "floor_min": 1, "floor_max": 5,
        "rewards": {"gold_min": 20, "gold_max": 50, "item_chance": 0.3},
    },
    {
        "id": "golden_chest",
        "name": "황금 상자",
        "type": "treasure",
        "description": "황금빛으로 빛나는 상자가 있다!",
        "floor_min": 3, "floor_max": 5,
        "rewards": {"gold_min": 50, "gold_max": 120, "item_chance": 0.6, "rare_chance": 0.2},
    },
    {
        "id": "ancient_vault",
        "name": "고대의 금고",
        "type": "treasure",
        "description": "아주 오래된 금고가 열려있다.",
        "floor_min": 5, "floor_max": 5,
        "rewards": {"gold_min": 100, "gold_max": 250, "item_chance": 0.9, "rare_chance": 0.5},
    },

    # ===== 휴식 이벤트 (1종) =====
    {
        "id": "campfire",
        "name": "모닥불",
        "type": "rest",
        "description": "따뜻한 모닥불이 피워져 있다. 잠시 쉬어가자.",
        "floor_min": 1, "floor_max": 5,
        "choices": [
            {
                "id": "rest",
                "text": "휴식하기",
                "description": "HP 30% 회복",
                "effect": {"heal_percent": 0.30}
            },
            {
                "id": "meditate",
                "text": "명상하기",
                "description": "MP 50% 회복",
                "effect": {"heal_mp_percent": 0.50}
            },
            {
                "id": "train",
                "text": "수련하기",
                "description": "이번 층 동안 공격력 10% 증가",
                "effect": {"buff": {"atk_mult": 1.1, "duration": 99}}
            },
        ],
    },

    # ===== 미스터리 이벤트 (5종) =====
    {
        "id": "mysterious_statue",
        "name": "신비한 석상",
        "type": "mystery",
        "description": "고대의 석상이 희미하게 빛나고 있다.",
        "floor_min": 1, "floor_max": 5,
        "choices": [
            {
                "id": "pray",
                "text": "기도하기",
                "description": "랜덤 효과",
                "effect": {"random": [
                    {"weight": 40, "result": {"heal_percent": 0.20}, "message": "신성한 빛이 당신을 감싸 HP가 회복되었다."},
                    {"weight": 30, "result": {"buff": {"all_stats": 5, "duration": 20}}, "message": "석상의 축복을 받았다!"},
                    {"weight": 20, "result": {"gold": 100}, "message": "석상 아래에서 금화를 발견했다!"},
                    {"weight": 10, "result": {"damage_percent": 0.10}, "message": "석상이 갑자기 폭발했다!"},
                ]}
            },
            {
                "id": "ignore",
                "text": "지나치기",
                "description": "아무 일도 일어나지 않음",
                "effect": {}
            },
        ],
    },
    {
        "id": "strange_fountain",
        "name": "이상한 샘",
        "type": "mystery",
        "description": "알 수 없는 액체가 담긴 샘이 있다.",
        "floor_min": 2, "floor_max": 5,
        "choices": [
            {
                "id": "drink",
                "text": "마시기",
                "description": "위험할 수 있음",
                "effect": {"random": [
                    {"weight": 35, "result": {"heal_percent": 0.50}, "message": "생명의 물이었다! HP가 크게 회복되었다."},
                    {"weight": 25, "result": {"heal_mp_percent": 0.50}, "message": "마나의 샘이었다! MP가 회복되었다."},
                    {"weight": 25, "result": {"damage_percent": 0.15}, "message": "독이었다! 데미지를 받았다."},
                    {"weight": 15, "result": {"buff": {"max_hp": 10, "permanent": True}}, "message": "최대 HP가 10 증가했다!"},
                ]}
            },
            {
                "id": "ignore",
                "text": "지나치기",
                "description": "안전하게 지나감",
                "effect": {}
            },
        ],
    },
    {
        "id": "wandering_merchant",
        "name": "떠돌이 상인",
        "type": "mystery",
        "description": "수상한 상인이 당신을 불러 세운다.",
        "floor_min": 3, "floor_max": 5,
        "choices": [
            {
                "id": "buy_info",
                "text": "정보 구매 (50G)",
                "description": "맵의 일부를 공개",
                "requires": {"gold": 50},
                "effect": {"reveal_adjacent": True, "cost_gold": 50}
            },
            {
                "id": "buy_item",
                "text": "아이템 구매 (100G)",
                "description": "랜덤 아이템 획득",
                "requires": {"gold": 100},
                "effect": {"random_item": True, "cost_gold": 100}
            },
            {
                "id": "gamble",
                "text": "도박 (50G)",
                "description": "2배 또는 0",
                "requires": {"gold": 50},
                "effect": {"random": [
                    {"weight": 50, "result": {"gold": 100}, "message": "이겼다! 100 골드를 얻었다!"},
                    {"weight": 50, "result": {"gold": -50}, "message": "졌다... 50 골드를 잃었다."},
                ]}
            },
            {
                "id": "ignore",
                "text": "지나치기",
                "description": "무시하고 지나감",
                "effect": {}
            },
        ],
    },
    {
        "id": "cursed_altar",
        "name": "저주받은 제단",
        "type": "mystery",
        "description": "어둠의 기운이 느껴지는 제단이 있다.",
        "floor_min": 5, "floor_max": 5,
        "choices": [
            {
                "id": "sacrifice_hp",
                "text": "HP 희생",
                "description": "HP 20% 소모, 강력한 버프",
                "effect": {"damage_percent": 0.20, "buff": {"atk_mult": 1.3, "duration": 30}}
            },
            {
                "id": "sacrifice_gold",
                "text": "골드 희생 (200G)",
                "description": "영구 방어력 +2",
                "requires": {"gold": 200},
                "effect": {"cost_gold": 200, "buff": {"def": 2, "permanent": True}}
            },
            {
                "id": "destroy",
                "text": "제단 파괴",
                "description": "저주 해제 또는 역효과",
                "effect": {"random": [
                    {"weight": 60, "result": {"exp": 50}, "message": "저주가 풀리며 경험치를 얻었다!"},
                    {"weight": 40, "result": {"debuff": {"all_stats": -3, "duration": 30}}, "message": "저주가 당신에게 옮겨붙었다!"},
                ]}
            },
            {
                "id": "ignore",
                "text": "지나치기",
                "description": "건드리지 않고 지나감",
                "effect": {}
            },
        ],
    },
    {
        "id": "treasure_goblin",
        "name": "보물 고블린",
        "type": "mystery",
        "description": "금화 자루를 든 고블린이 도망치려 한다!",
        "floor_min": 2, "floor_max": 5,
        "choices": [
            {
                "id": "chase",
                "text": "추격하기",
                "description": "잡으면 대박, 실패하면 함정",
                "effect": {"random": [
                    {"weight": 40, "result": {"gold": 200, "item_chance": 0.5}, "message": "고블린을 잡았다! 대량의 골드 획득!"},
                    {"weight": 35, "result": {"gold": 50}, "message": "고블린이 금화 일부를 흘리고 도망갔다."},
                    {"weight": 25, "result": {"damage_percent": 0.15}, "message": "함정에 빠졌다! 데미지를 받았다."},
                ]}
            },
            {
                "id": "ignore",
                "text": "무시하기",
                "description": "안전하게 지나감",
                "effect": {}
            },
        ],
    },

    # ===== v5.0 악마의 거래 이벤트 =====
    {
        "id": "demon_deal",
        "name": "악마의 거래",
        "type": "mystery",
        "description": "\"욕망이 보이는군... 거래하지 않겠나?\" 어둠 속에서 악마가 나타났다.",
        "floor_min": 2, "floor_max": 5,
        "choices": [
            {
                "id": "deal_hp_skill",
                "text": "💀 영혼 계약",
                "description": "최대 HP -20, 강력한 스킬 획득",
                "effect": {"devil_deal": True, "max_hp_cost": 20, "grant_skill": "soul_harvest"}
            },
            {
                "id": "deal_gold_item",
                "text": "💰 황금의 유혹",
                "description": "골드 전부, 저주받은 아이템 획득",
                "effect": {"devil_deal": True, "gold_cost_all": True, "grant_cursed_item": True}
            },
            {
                "id": "deal_hp_blessing",
                "text": "🩸 피의 맹세",
                "description": "현재 HP 50%, 희귀 축복 2개",
                "effect": {"devil_deal": True, "hp_cost_percent": 0.5, "grant_blessing_count": 2}
            },
            {
                "id": "deal_soul_curse",
                "text": "✨ 저주 해방",
                "description": "소울 -50, 장착 중인 저주 제거",
                "requires": {"souls": 50},
                "effect": {"devil_deal": True, "soul_cost": 50, "remove_curse": True}
            },
            {
                "id": "refuse",
                "text": "❌ 거절한다",
                "description": "\"현명한 선택이군...\"",
                "effect": {}
            },
        ],
    },
    {
        "id": "demon_shrine",
        "name": "악마의 제단",
        "type": "mystery",
        "description": "피로 물든 제단에서 불길한 기운이 뿜어져 나온다.",
        "floor_min": 4, "floor_max": 5,
        "choices": [
            {
                "id": "offer_life",
                "text": "💀 생명 바치기",
                "description": "최대 HP -30, ATK +10 영구",
                "effect": {"devil_deal": True, "max_hp_cost": 30, "permanent_atk": 10}
            },
            {
                "id": "offer_blood",
                "text": "🩸 피 바치기",
                "description": "현재 HP 40%, DEF +8 영구",
                "effect": {"devil_deal": True, "hp_cost_percent": 0.4, "permanent_def": 8}
            },
            {
                "id": "offer_soul",
                "text": "👻 영혼 일부 바치기",
                "description": "소울 획득량 -50% (이번 런), 전설 아이템",
                "effect": {"devil_deal": True, "soul_penalty_run": 0.5, "grant_legendary_item": True}
            },
            {
                "id": "ignore",
                "text": "지나치기",
                "description": "건드리지 않고 지나감",
                "effect": {}
            },
        ],
    },
]


async def seed_events(db) -> int:
    """이벤트 데이터 삽입"""
    for e in EVENTS:
        await db.execute("""
            INSERT INTO events (id, name, type, description, floor_min, floor_max,
                effect, choices, requires, rewards)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            e["id"], e["name"], e["type"], e["description"],
            e.get("floor_min", 1), e.get("floor_max", 5),
            json.dumps(e.get("effect")) if e.get("effect") else None,
            json.dumps(e.get("choices")) if e.get("choices") else None,
            json.dumps(e.get("requires")) if e.get("requires") else None,
            json.dumps(e.get("rewards")) if e.get("rewards") else None,
        ))
    return len(EVENTS)
