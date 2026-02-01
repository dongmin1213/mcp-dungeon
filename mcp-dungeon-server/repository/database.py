"""데이터베이스 연결 관리"""
import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager

# DB 경로
DB_PATH = Path(__file__).parent.parent / "db" / "game.db"


@asynccontextmanager
async def get_db():
    """DB 연결 컨텍스트 매니저"""
    db = await Database.connect()
    try:
        yield db
    finally:
        pass  # 싱글톤이므로 연결 유지


# DB 스키마 정의
SCHEMA_SQL = """
-- ============================================================
-- 프로필 테이블 (DEPRECATED - v1.0 레거시)
-- 주의: 이 테이블은 하위 호환성을 위해 유지됩니다.
-- 새 코드는 profiles 테이블을 사용하세요.
-- ============================================================
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY DEFAULT 1,
    souls INTEGER DEFAULT 0,
    total_souls_earned INTEGER DEFAULT 0,
    games_played INTEGER DEFAULT 0,
    games_cleared INTEGER DEFAULT 0,
    total_monsters_killed INTEGER DEFAULT 0,
    total_gold_earned INTEGER DEFAULT 0,
    best_clear_time INTEGER DEFAULT NULL,
    highest_floor INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 업그레이드 테이블
CREATE TABLE IF NOT EXISTS upgrades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upgrade_type TEXT NOT NULL UNIQUE,
    level INTEGER DEFAULT 0,
    max_level INTEGER DEFAULT 10
);

-- 언락 테이블
CREATE TABLE IF NOT EXISTS unlocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unlock_type TEXT NOT NULL,
    unlock_key TEXT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(unlock_type, unlock_key)
);

-- 몬스터 테이블
CREATE TABLE IF NOT EXISTS monsters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('normal', 'elite', 'boss')),
    floor_min INTEGER NOT NULL,
    floor_max INTEGER NOT NULL,
    hp INTEGER NOT NULL,
    atk INTEGER NOT NULL,
    def INTEGER NOT NULL,
    exp INTEGER NOT NULL,
    gold_min INTEGER NOT NULL,
    gold_max INTEGER NOT NULL,
    souls INTEGER NOT NULL,
    skills TEXT DEFAULT '[]',
    pattern TEXT DEFAULT NULL,
    -- v5.0 행동 예고제
    action_pattern TEXT DEFAULT '["attack"]',
    -- v5.0 속성 시스템
    element TEXT DEFAULT NULL,
    weaknesses TEXT DEFAULT '[]',
    resistances TEXT DEFAULT '[]',
    immunities TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 몬스터 드롭 테이블
CREATE TABLE IF NOT EXISTS monster_drops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monster_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    drop_chance REAL NOT NULL,
    min_quantity INTEGER DEFAULT 1,
    max_quantity INTEGER DEFAULT 1,
    FOREIGN KEY (monster_id) REFERENCES monsters(id)
);

-- 아이템 테이블
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('weapon', 'armor', 'helmet', 'accessory', 'consumable', 'special')),
    grade TEXT NOT NULL CHECK(grade IN ('common', 'uncommon', 'rare', 'legendary', 'cursed')),
    description TEXT NOT NULL,
    price INTEGER NOT NULL,
    floor_min INTEGER DEFAULT 1,
    floor_max INTEGER DEFAULT 5,
    stat_atk INTEGER DEFAULT 0,
    stat_def INTEGER DEFAULT 0,
    stat_hp INTEGER DEFAULT 0,
    stat_mp INTEGER DEFAULT 0,
    effect TEXT DEFAULT NULL,
    -- v5.0 저주 시스템
    curse TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 스킬 테이블
CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('attack', 'buff', 'debuff', 'heal')),
    mp_cost INTEGER NOT NULL,
    cooldown INTEGER DEFAULT 0,
    unlock_level INTEGER DEFAULT 1,
    effect TEXT NOT NULL,
    classes TEXT NOT NULL,
    -- v5.0 속성 시스템
    element TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 이벤트 테이블
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('trap', 'treasure', 'rest', 'mystery', 'shop')),
    description TEXT NOT NULL,
    floor_min INTEGER DEFAULT 1,
    floor_max INTEGER DEFAULT 5,
    effect TEXT DEFAULT NULL,
    choices TEXT DEFAULT NULL,
    requires TEXT DEFAULT NULL,
    rewards TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 업적 정의 테이블
CREATE TABLE IF NOT EXISTS achievements (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    condition TEXT NOT NULL,
    reward_souls INTEGER DEFAULT 0,
    reward_unlock TEXT DEFAULT NULL,
    hidden BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 유저 업적 달성 테이블
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    achievement_id TEXT NOT NULL UNIQUE,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
);

-- 직업 테이블
CREATE TABLE IF NOT EXISTS classes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    base_hp INTEGER NOT NULL,
    base_mp INTEGER NOT NULL,
    base_atk INTEGER NOT NULL,
    base_def INTEGER NOT NULL,
    special_ability TEXT NOT NULL,
    unlock_condition TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 현재 게임 상태 테이블 (런 데이터)
CREATE TABLE IF NOT EXISTS current_run (
    id INTEGER PRIMARY KEY DEFAULT 1,
    player_data TEXT NOT NULL,
    dungeon_data TEXT NOT NULL,
    floor INTEGER NOT NULL,
    play_time INTEGER DEFAULT 0,
    checksum TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 게임 기록 테이블 (히스토리)
CREATE TABLE IF NOT EXISTS game_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    player_class TEXT NOT NULL,
    floor_reached INTEGER NOT NULL,
    monsters_killed INTEGER DEFAULT 0,
    gold_earned INTEGER DEFAULT 0,
    souls_earned INTEGER DEFAULT 0,
    play_time INTEGER DEFAULT 0,
    cleared BOOLEAN DEFAULT FALSE,
    death_reason TEXT DEFAULT NULL,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 프로필 테이블 (Phase 4 - ACTIVE)
-- 이 테이블이 현재 사용되는 프로필 테이블입니다.
-- id: 'default' 또는 플레이어 고유 ID
-- ============================================================
CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_played TEXT NOT NULL,
    souls INTEGER DEFAULT 0,
    stats TEXT NOT NULL,
    upgrades TEXT NOT NULL,
    unlocked_classes TEXT NOT NULL,
    unlocked_items TEXT NOT NULL,
    unlocked_modes TEXT NOT NULL,
    completed_achievements TEXT NOT NULL
);

-- 저장 슬롯 테이블 (Phase 5)
CREATE TABLE IF NOT EXISTS save_slots (
    slot_id INTEGER PRIMARY KEY,
    data TEXT NOT NULL,
    saved_at TEXT NOT NULL
);

-- 랭킹 테이블 (Phase 5, Phase 2: 승천 추가)
CREATE TABLE IF NOT EXISTS rankings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id TEXT NOT NULL,
    profile_name TEXT NOT NULL,
    class_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    ascension_level INTEGER DEFAULT 0,
    score INTEGER NOT NULL,
    floor INTEGER NOT NULL,
    level INTEGER NOT NULL,
    monsters_killed INTEGER NOT NULL,
    bosses_killed INTEGER NOT NULL,
    play_time INTEGER NOT NULL,
    victory INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

-- Phase 2: 프로필에 해금된 승천 레벨 추가
-- 클리어한 승천 레벨까지 다음 레벨 해금
CREATE TABLE IF NOT EXISTS ascension_progress (
    profile_id TEXT PRIMARY KEY DEFAULT 'default',
    max_unlocked INTEGER DEFAULT 0,
    max_cleared INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO ascension_progress (profile_id) VALUES ('default');

-- 랭킹 인덱스
CREATE INDEX IF NOT EXISTS idx_rankings_score ON rankings (score DESC);
CREATE INDEX IF NOT EXISTS idx_rankings_mode_score ON rankings (mode, score DESC);

-- 기본 데이터 초기화
INSERT OR IGNORE INTO profile (id) VALUES (1);

INSERT OR IGNORE INTO upgrades (upgrade_type, level, max_level) VALUES
    ('hp', 0, 10),
    ('atk', 0, 10),
    ('def', 0, 10),
    ('potion', 0, 10),
    ('gold', 0, 10),
    ('luck', 0, 10);

INSERT OR IGNORE INTO unlocks (unlock_type, unlock_key) VALUES
    ('class', 'warrior');
"""


class Database:
    """데이터베이스 연결 관리 싱글톤"""
    _connection: aiosqlite.Connection | None = None

    @classmethod
    async def connect(cls) -> aiosqlite.Connection:
        """DB 연결 (없으면 생성)"""
        if cls._connection is None:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            cls._connection = await aiosqlite.connect(DB_PATH)
            cls._connection.row_factory = aiosqlite.Row
            await cls._init_tables()
        return cls._connection

    @classmethod
    async def _init_tables(cls) -> None:
        """테이블 초기화"""
        if cls._connection:
            await cls._connection.executescript(SCHEMA_SQL)
            await cls._connection.commit()

    @classmethod
    async def close(cls) -> None:
        """연결 종료"""
        if cls._connection:
            await cls._connection.close()
            cls._connection = None

    @classmethod
    async def execute(cls, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        """쿼리 실행"""
        db = await cls.connect()
        return await db.execute(query, params)

    @classmethod
    async def executemany(cls, query: str, params_list: list[tuple]) -> None:
        """여러 쿼리 실행"""
        db = await cls.connect()
        await db.executemany(query, params_list)
        await db.commit()

    @classmethod
    async def commit(cls) -> None:
        """커밋"""
        if cls._connection:
            await cls._connection.commit()
