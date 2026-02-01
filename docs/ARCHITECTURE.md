# 아키텍처 문서

> MCP 던전 로그라이크 기술 문서 (v6.9)

---

## 1. 기술 스택

| 항목 | 기술 | 버전 |
|------|------|------|
| 언어 | Python | 3.11+ |
| 프로토콜 | MCP (Model Context Protocol) | - |
| DB | SQLite + aiosqlite | - |
| 모델 | Pydantic | - |
| 패키지 관리 | pip | - |

---

## 2. 프로젝트 구조

```
mcp-dungeon-server/
├── server.py              # MCP 서버 진입점 (31개 도구 등록)
├── config.py              # 설정값/밸런스 상수/GameConfig
│
├── tools/                 # MCP 도구 (UI/입출력 담당)
│   ├── game.py            # start_game, get_status, move, interact, get_map
│   ├── combat.py          # attack, defend, flee, choose_blessing (1245줄)
│   ├── skill.py           # use_skill, get_skills
│   ├── inventory.py       # get_inventory, use_item, equip, unequip
│   ├── shop.py            # shop_list, buy, sell
│   ├── meta.py            # get_profile, get_souls, upgrade, unlock, etc.
│   ├── save.py            # save_game, load_game, get_save_slots, delete_save
│   └── ranking.py         # get_ranking, get_records
│
├── systems/               # 게임 로직 (비즈니스 로직)
│   ├── combat.py          # 전투 계산/공식
│   ├── blessing.py        # 축복 (31종) + 듀오 (10종) 로직
│   ├── combo.py           # 콤보 (12종) + 체인/궁극기
│   ├── synergy.py         # 시너지 (18종) 효과 계산
│   ├── element.py         # 속성 (7종) 상성 계산
│   ├── enemy_ai.py        # 적 AI/행동 예고
│   ├── devil_deal.py      # 악마의 거래
│   ├── secret_room.py     # 비밀 방 (5종)
│   ├── ascension.py       # 승천 모드 (10레벨)
│   ├── boss_gimmick.py    # 보스 기믹 (5종)
│   ├── boss_pattern.py    # 보스 행동 패턴
│   ├── dungeon.py         # 던전 생성 (Random Walk)
│   ├── shop.py            # 상점 로직
│   ├── skill.py           # 스킬 로직
│   └── event.py           # 이벤트 처리
│
├── models/                # Pydantic 모델 (데이터 구조)
│   ├── player.py          # Player 클래스
│   ├── monster.py         # Monster, EnemyAction
│   ├── item.py            # Item 클래스
│   ├── dungeon.py         # Dungeon, Room
│   ├── blessing.py        # Blessing 클래스
│   └── synergy.py         # Synergy 클래스
│
├── state/                 # 상태 관리 (싱글톤)
│   └── game_state.py      # GameState, CombatState
│
├── repository/            # DB 접근 (Repository 패턴)
│   ├── database.py        # DB 스키마/연결
│   ├── monster_repo.py    # MonsterRepository
│   ├── item_repo.py       # ItemRepository
│   ├── skill_repo.py      # SkillRepository
│   ├── event_repo.py      # EventRepository
│   ├── profile_repo.py    # ProfileRepository
│   └── save_repo.py       # SaveRepository
│
├── seeds/                 # 시드 데이터 (SSOT)
│   ├── classes.py         # CLASS_STATS, CLASS_NAMES (SSOT)
│   ├── monsters.py        # 30종 (일반 16, 엘리트 5, 보스 10)
│   ├── items.py           # 70+종 (무기, 방어구, 소비, 저주)
│   ├── skills.py          # 25+종
│   ├── events.py          # 14종
│   ├── achievements.py    # 25+종
│   ├── blessings.py       # 31종
│   ├── duo_blessings.py   # 10종
│   ├── synergies.py       # 18종 + 숨겨진 3종
│   └── seed_all.py        # 전체 시드 실행
│
├── db/                    # SQLite DB 파일
│   └── game.db            # 게임 데이터
│
└── tests/                 # 테스트 (미작성)
    └── (빈 폴더)
```

---

## 3. MCP 도구 목록 (31개)

### 3.1 게임 진행 (5개)

| 도구 | 파일 | 설명 |
|------|------|------|
| `start_game(name)` | tools/game.py | 게임 시작 (없으면 세이브 확인) |
| `get_status()` | tools/game.py | 현재 상태 표시 |
| `move(direction)` | tools/game.py | 이동 (north/south/east/west) |
| `interact(choice)` | tools/game.py | 상호작용/선택 |
| `get_map()` | tools/game.py | 미니맵 표시 |

### 3.2 전투 (6개)

| 도구 | 파일 | 설명 |
|------|------|------|
| `attack()` | tools/combat.py | 기본 공격 |
| `defend()` | tools/combat.py | 방어 (데미지 50% 감소) |
| `flee()` | tools/combat.py | 도망 (보스전 불가) |
| `choose_blessing(n)` | tools/combat.py | 축복 선택 (1~3) |
| `use_skill(id)` | tools/skill.py | 스킬 사용 |
| `get_skills()` | tools/skill.py | 스킬 목록 |

### 3.3 인벤토리 (4개)

| 도구 | 파일 | 설명 |
|------|------|------|
| `get_inventory()` | tools/inventory.py | 인벤토리 조회 |
| `use_item(id)` | tools/inventory.py | 아이템 사용 |
| `equip(id)` | tools/inventory.py | 장착 |
| `unequip(slot)` | tools/inventory.py | 해제 |

### 3.4 상점 (3개)

| 도구 | 파일 | 설명 |
|------|------|------|
| `shop_list()` | tools/shop.py | 상점 목록 |
| `buy(id)` | tools/shop.py | 구매 |
| `sell(id)` | tools/shop.py | 판매 (50%) |

### 3.5 메타 (6개)

| 도구 | 파일 | 설명 |
|------|------|------|
| `get_profile()` | tools/meta.py | 프로필 |
| `get_souls()` | tools/meta.py | 소울/업그레이드 |
| `upgrade(id)` | tools/meta.py | 업그레이드 구매 |
| `unlock(id)` | tools/meta.py | 언락 |
| `get_achievements()` | tools/meta.py | 업적 |
| `get_unlocks()` | tools/meta.py | 언락 목록 |

### 3.6 저장 (4개)

| 도구 | 파일 | 설명 |
|------|------|------|
| `save_game(slot)` | tools/save.py | 저장 (1-5) |
| `load_game(slot)` | tools/save.py | 불러오기 |
| `get_save_slots()` | tools/save.py | 슬롯 목록 |
| `delete_save(slot)` | tools/save.py | 삭제 |

### 3.7 기타 (3개)

| 도구 | 파일 | 설명 |
|------|------|------|
| `get_help(topic)` | tools/game.py | 도움말 |
| `get_ranking(mode)` | tools/ranking.py | 랭킹 |
| `get_records()` | tools/ranking.py | 개인 기록 |

---

## 4. DB 스키마

### 4.1 게임 데이터 테이블

| 테이블 | 용도 | 주요 컬럼 |
|--------|------|----------|
| `monsters` | 몬스터 | id, name, hp, atk, def, type, floor_min/max, element, weaknesses |
| `items` | 아이템 | id, name, type, grade, price, stat_*, effect, curse |
| `skills` | 스킬 | id, name, mp_cost, effect, element, classes |
| `events` | 이벤트 | id, type, floor_min/max, effect, choices |
| `classes` | 직업 | id, name, hp, mp, atk, def, special_ability |
| `achievements` | 업적 | id, name, condition, reward_souls, reward_unlock |

### 4.2 유저 데이터 테이블

| 테이블 | 용도 |
|--------|------|
| `profiles` | 영구 프로필 (소울, 통계, 해금 상태) |
| `profile` | 레거시 프로필 (하위 호환성) |
| `upgrades` | 영구 업그레이드 레벨 |
| `unlocks` | 해금된 콘텐츠 |
| `user_achievements` | 달성한 업적 |
| `save_slots` | 저장 슬롯 (1-5) |
| `rankings` | 랭킹 기록 |
| `ascension_progress` | 승천 진행도 |

### 4.3 아이템 등급 (CHECK 제약)

```sql
grade TEXT CHECK(grade IN ('common', 'uncommon', 'rare', 'legendary', 'cursed'))
```

### 4.4 몬스터 타입 (CHECK 제약)

```sql
type TEXT CHECK(type IN ('normal', 'elite', 'boss'))
```

---

## 5. 시드 데이터 요약

| 데이터 | 개수 | 파일 |
|--------|------|------|
| 몬스터 | 30종 | seeds/monsters.py |
| 아이템 | 70+종 | seeds/items.py |
| 스킬 | 25+종 | seeds/skills.py |
| 이벤트 | 14종 | seeds/events.py |
| 업적 | 25+종 | seeds/achievements.py |
| 축복 | 31종 | seeds/blessings.py |
| 듀오 축복 | 10종 | seeds/duo_blessings.py |
| 시너지 | 18종+3종 | seeds/synergies.py |
| 직업 | 6종 | seeds/classes.py |

---

## 6. 상태 관리

### 6.1 GameState (싱글톤)

```python
game = GameState.current()

# 기본 상태
game.player          # 플레이어 (Player)
game.dungeon         # 던전 (Dungeon)
game.floor           # 현재 층 (int)
game.mode            # 게임 모드 (str)

# 전투 상태
game.combat          # 전투 상태 (CombatState | None)
game.in_combat       # 전투 중 여부 (bool)

# v5.0
game.floor_combats        # 이번 층 전투 횟수
game.rest_used_this_floor # 휴식 사용 여부
game.potion_count         # 포션 개수

# v6.0
game.ascension_level # 승천 레벨 (int)
game.ascension       # AscensionManager
```

### 6.2 CombatState (전투 중)

```python
combat = game.combat

# 기본
combat.enemy         # 현재 적 (Monster)
combat.turn          # 현재 턴 (int)
combat.is_boss       # 보스전 여부 (bool)

# v5.0
combat.skill_history # 사용한 스킬 기록 (list)

# v6.0
combat.combo_chain   # ComboChainManager (콤보 체인/궁극기)
combat.boss_gimmick  # BossGimmickState (보스 기믹)
combat.rage_stacks   # 분노의 화신 스택 (int)
combat.death_save_used  # 불멸의 투사 사용 여부 (bool)
```

---

## 7. 코드 패턴 가이드 (v6.9)

### 7.1 SSOT 패턴 (Single Source of Truth)

중복 데이터는 `seeds/` 폴더에 정의하고 다른 파일에서 import:

```python
# seeds/classes.py (SSOT)
CLASS_STATS: dict[str, dict[str, int]] = {
    "warrior": {"hp": 120, "mp": 30, "atk": 12, "def_": 8},
    "archer": {"hp": 90, "mp": 50, "atk": 14, "def_": 4},
    # ...
}
CLASS_NAMES: dict[str, str] = {"warrior": "전사", ...}
DEFAULT_UNLOCKED_CLASSES: list[str] = ["warrior", "archer"]

# config.py, models/player.py에서 import
from seeds.classes import CLASS_STATS, CLASS_NAMES
```

### 7.2 TYPE_CHECKING 패턴 (순환 참조 방지)

런타임에는 import 안 하고 타입 힌트만 사용:

```python
# systems/combat.py, systems/blessing.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.player import Player
    from models.monster import Monster

def process_attack(player: "Player", enemy: "Monster") -> dict:
    # "Player" 문자열 타입 힌트 사용
    ...
```

### 7.3 헬퍼 함수 분리 패턴

긴 함수는 `_` 접두사 헬퍼로 분리:

```python
# tools/combat.py 예시
def _process_boss_gimmick_turn_start(enemy, player, combat) -> str: ...
def _calculate_attack_modifiers(player, enemy, ...) -> tuple: ...
def _execute_player_attack(player, enemy, ...) -> tuple: ...
def _apply_post_attack_effects(player, enemy, ...) -> str: ...
async def _process_victory(game, player, enemy) -> str: ...
def _apply_turn_end_effects(player, enemy, duo_effects, combat) -> str: ...

# 메인 함수
async def attack() -> str:
    # 헬퍼 함수들 호출
    gimmick_msg = _process_boss_gimmick_turn_start(...)
    ...
```

### 7.4 import 규칙

```python
# 1. 표준 라이브러리
import random
from typing import TYPE_CHECKING

# 2. 외부 패키지
from pydantic import BaseModel

# 3. 프로젝트 내부 (절대 경로)
from config import GameConfig
from seeds.classes import CLASS_STATS
from models.player import Player  # 또는 TYPE_CHECKING 내부에서
```

---

## 8. 핵심 시스템 파일

### 8.1 tools/combat.py (1245줄)

전투 관련 MCP 도구 + 헬퍼 함수:

```python
# MCP 도구
async def attack() -> str        # 기본 공격
async def defend() -> str        # 방어
async def flee() -> str          # 도망
async def choose_blessing(choice: int) -> str  # 축복 선택

# 헬퍼 (v6.9 추가)
def _process_boss_gimmick_turn_start(...)
def _calculate_attack_modifiers(...)
def _execute_player_attack(...)
def _apply_post_attack_effects(...)
async def _process_victory(...)
def _apply_turn_end_effects(...)
```

### 8.2 systems/blessing.py

축복 + 듀오 축복 로직:

```python
def apply_blessing(player: "Player", blessing: Blessing) -> dict
def get_random_blessings(count: int, floor: int) -> list[Blessing]
def get_duo_combat_effects(player: "Player") -> dict  # v6.0
def check_active_duos(owned_blessing_ids: set[str]) -> list[DuoBlessing]
```

### 8.3 systems/ascension.py

승천 모드 로직:

```python
class AscensionManager:
    def get_elite_hp_multiplier() -> float
    def get_boss_hp_multiplier() -> float
    def is_shop_potions_disabled() -> bool
    def is_enemy_first_turn() -> bool
    def get_blessing_choices() -> int
    def is_flee_disabled_before_boss() -> bool
    # ...
```

### 8.4 systems/boss_gimmick.py

보스 기믹 로직:

```python
class BossGimmickState:
    gimmick_type: GimmickType
    phase: int
    rage_stacks: int
    minions: list
    # ...

def process_turn_start(state, player, enemy) -> str
def process_on_hit(state, player, enemy, damage) -> str
def process_on_attack(state, player, enemy, damage) -> str
```

---

## 9. 남은 작업 (P2)

| 작업 | 우선순위 | 설명 |
|------|----------|------|
| 단위 테스트 | P2 | pytest로 핵심 로직 테스트 |
| 로깅 시스템 | P2 | print → logging 모듈 전환 |
| 매직 넘버 상수화 | P2 | 하드코딩된 0.15 등 → config.py |

---

## 10. 의존성 그래프

```
server.py
    └── tools/*
            └── systems/*
                    └── models/*
                    └── state/*
                    └── repository/*
                            └── seeds/*
                            └── db/*
```

**의존성 방향**: 상위 → 하위 (역방향 금지)

**예외**: TYPE_CHECKING으로 타입 힌트만 역방향 참조 가능

---

*문서 버전: v6.9 | 최종 업데이트: 2026-01-29*
