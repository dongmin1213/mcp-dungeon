"""업적 시드 데이터"""
import json

ACHIEVEMENTS = [
    # ===== 진행 업적 =====
    {
        "id": "first_monster",
        "name": "첫 번째 사냥",
        "description": "첫 몬스터를 처치하세요.",
        "condition": {"type": "monsters_killed", "count": 1},
        "reward_souls": 10,
        "hidden": False,
    },
    {
        "id": "monster_hunter_10",
        "name": "사냥꾼",
        "description": "몬스터를 10마리 처치하세요.",
        "condition": {"type": "monsters_killed", "count": 10},
        "reward_souls": 30,
        "hidden": False,
    },
    {
        "id": "monster_hunter_100",
        "name": "전문 사냥꾼",
        "description": "몬스터를 100마리 처치하세요.",
        "condition": {"type": "monsters_killed", "count": 100},
        "reward_souls": 100,
        "hidden": False,
    },
    {
        "id": "monster_hunter_500",
        "name": "전설의 사냥꾼",
        "description": "몬스터를 500마리 처치하세요.",
        "condition": {"type": "monsters_killed", "count": 500},
        "reward_souls": 300,
        "hidden": False,
    },

    # ===== 클리어 업적 =====
    {
        "id": "first_clear",
        "name": "탈출 성공",
        "description": "던전을 처음으로 클리어하세요.",
        "condition": {"type": "games_cleared", "count": 1},
        "reward_souls": 100,
        "reward_unlock": "archer,mage",  # 궁수, 마법사 언락
        "hidden": False,
    },
    {
        "id": "clear_5",
        "name": "던전 정복자",
        "description": "던전을 5번 클리어하세요.",
        "condition": {"type": "games_cleared", "count": 5},
        "reward_souls": 200,
        "hidden": False,
    },
    {
        "id": "clear_20",
        "name": "던전 마스터",
        "description": "던전을 20번 클리어하세요.",
        "condition": {"type": "games_cleared", "count": 20},
        "reward_souls": 500,
        "hidden": False,
    },

    # ===== 보스 업적 =====
    {
        "id": "defeat_rat_king",
        "name": "쥐잡이",
        "description": "쥐 왕을 처치하세요.",
        "condition": {"type": "boss_killed", "boss_id": "boss_rat_king"},
        "reward_souls": 25,
        "hidden": False,
    },
    {
        "id": "defeat_skeleton_general",
        "name": "해골 사냥꾼",
        "description": "해골 장군을 처치하세요.",
        "condition": {"type": "boss_killed", "boss_id": "boss_skeleton_general"},
        "reward_souls": 50,
        "hidden": False,
    },
    {
        "id": "defeat_crystal_guardian",
        "name": "수정 파괴자",
        "description": "수정 수호자를 처치하세요.",
        "condition": {"type": "boss_killed", "boss_id": "boss_crystal_guardian"},
        "reward_souls": 80,
        "hidden": False,
    },
    {
        "id": "defeat_demon_lord",
        "name": "악마 사냥꾼",
        "description": "악마 군주를 처치하세요.",
        "condition": {"type": "boss_killed", "boss_id": "boss_demon_lord"},
        "reward_souls": 120,
        "hidden": False,
    },
    {
        "id": "defeat_final_boss",
        "name": "던전의 종결자",
        "description": "던전 마스터를 처치하세요.",
        "condition": {"type": "boss_killed", "boss_id": "boss_dungeon_master"},
        "reward_souls": 200,
        "reward_unlock": "reaper",  # 사신 직업 언락
        "hidden": False,
    },

    # ===== 수집 업적 =====
    {
        "id": "gold_1000",
        "name": "부자의 시작",
        "description": "한 번에 1000 골드를 모으세요.",
        "condition": {"type": "gold_held", "amount": 1000},
        "reward_souls": 50,
        "hidden": False,
    },
    {
        "id": "gold_5000",
        "name": "금고의 주인",
        "description": "한 번에 5000 골드를 모으세요.",
        "condition": {"type": "gold_held", "amount": 5000},
        "reward_souls": 150,
        "hidden": False,
    },
    {
        "id": "soul_collector_100",
        "name": "영혼 수집가",
        "description": "총 100 소울을 획득하세요.",
        "condition": {"type": "total_souls", "amount": 100},
        "reward_souls": 20,
        "hidden": False,
    },
    {
        "id": "soul_collector_1000",
        "name": "영혼 지배자",
        "description": "총 1000 소울을 획득하세요.",
        "condition": {"type": "total_souls", "amount": 1000},
        "reward_souls": 100,
        "hidden": False,
    },

    # ===== 도전 업적 =====
    {
        "id": "no_damage_boss",
        "name": "완벽한 전투",
        "description": "보스전에서 데미지를 받지 않고 승리하세요.",
        "condition": {"type": "no_damage_boss"},
        "reward_souls": 150,
        "hidden": True,
    },
    {
        "id": "speedrun",
        "name": "스피드러너",
        "description": "30분 이내에 던전을 클리어하세요.",
        "condition": {"type": "clear_time", "max_seconds": 1800},
        "reward_souls": 200,
        "hidden": False,
    },
    {
        "id": "no_shop",
        "name": "자급자족",
        "description": "상점을 이용하지 않고 클리어하세요.",
        "condition": {"type": "clear_without_shop"},
        "reward_souls": 100,
        "hidden": True,
    },
    {
        "id": "close_call",
        "name": "아슬아슬",
        "description": "HP 1로 보스를 처치하세요.",
        "condition": {"type": "kill_boss_low_hp", "max_hp": 1},
        "reward_souls": 100,
        "hidden": True,
    },

    # ===== 사망 업적 =====
    {
        "id": "first_death",
        "name": "이런...",
        "description": "첫 사망을 경험하세요.",
        "condition": {"type": "deaths", "count": 1},
        "reward_souls": 5,
        "hidden": False,
    },
    {
        "id": "death_10",
        "name": "불굴의 의지",
        "description": "10번 사망하세요.",
        "condition": {"type": "deaths", "count": 10},
        "reward_souls": 30,
        "hidden": False,
    },
    {
        "id": "death_trap",
        "name": "함정 전문가",
        "description": "함정으로 사망하세요.",
        "condition": {"type": "death_by", "cause": "trap"},
        "reward_souls": 15,
        "hidden": True,
    },

    # ===== 직업 업적 =====
    {
        "id": "clear_warrior",
        "name": "전사의 길",
        "description": "전사로 던전을 클리어하세요.",
        "condition": {"type": "clear_with_class", "class": "warrior"},
        "reward_souls": 50,
        "hidden": False,
    },
    {
        "id": "clear_all_classes",
        "name": "만능 모험가",
        "description": "모든 직업으로 던전을 클리어하세요.",
        "condition": {"type": "clear_with_all_classes"},
        "reward_souls": 500,
        "hidden": False,
    },
]


async def seed_achievements(db) -> int:
    """업적 데이터 삽입"""
    for a in ACHIEVEMENTS:
        await db.execute("""
            INSERT INTO achievements (id, name, description, condition,
                reward_souls, reward_unlock, hidden)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            a["id"], a["name"], a["description"],
            json.dumps(a["condition"]),
            a.get("reward_souls", 0),
            a.get("reward_unlock"),
            a.get("hidden", False),
        ))
    return len(ACHIEVEMENTS)
