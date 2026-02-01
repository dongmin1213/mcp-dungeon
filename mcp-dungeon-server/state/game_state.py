"""게임 상태 관리"""
from typing import Optional, Any
import time
from models.status_effect import StatusManager


class CombatState:
    """전투 상태"""
    def __init__(self, enemy: Any):
        self.enemy = enemy
        self.turn: int = 1
        self.player_defending: bool = False
        self.fled: bool = False
        self.cooldowns: dict[str, int] = {}  # 스킬 쿨다운
        self.player_status: StatusManager = StatusManager()  # 플레이어 상태이상
        self.enemy_status: StatusManager = StatusManager()   # 적 상태이상
        self.boss_pattern = None  # 보스 패턴 (보스전에서만 사용)

        # v5.0 행동 예고제
        self.enemy_next_action = None  # 적의 다음 행동
        self.enemy_defending = False   # 적 방어 상태
        self.skill_history: list[str] = []  # 플레이어 스킬 사용 기록 (콤보용)

        # Phase 1B: 콤보 체인 + 궁극기
        from systems.combo import ComboChainManager
        self.combo_chain: ComboChainManager = ComboChainManager()

        # Phase 3: 듀오 효과 상태
        self.rage_stacks: int = 0  # 분노의 화신 스택
        self.death_save_used: bool = False  # 불멸의 투사 사용 여부

        # 보스인 경우 패턴 초기화
        if enemy.is_boss and enemy.pattern_json:
            from systems.boss_pattern import BossPattern
            self.boss_pattern = BossPattern(enemy.pattern_json)

        # Phase 4: 보스 기믹 상태
        self.boss_gimmick = None
        if enemy.is_boss:
            from systems.boss_gimmick import create_gimmick_state
            self.boss_gimmick = create_gimmick_state(enemy)

        # 적의 첫 행동 결정
        self._determine_enemy_action()

    def _determine_enemy_action(self, player_hp_ratio: float = 1.0):
        """적의 다음 행동 결정

        Args:
            player_hp_ratio: 플레이어 HP 비율 (0~1) - AI가 판단에 사용
        """
        from systems.enemy_ai import determine_next_action
        self.enemy_next_action = determine_next_action(self.enemy, self.turn, player_hp_ratio)
        self.enemy.next_action = self.enemy_next_action


class PendingChoice:
    """대기 중인 선택지"""
    def __init__(self, room_type: str, choices: list, event: dict = None):
        self.room_type = room_type
        self.choices = choices
        self.event = event


class PendingBlessing:
    """v5.0 대기 중인 축복 선택"""
    def __init__(self, choices: list, enemy_name: str):
        self.choices = choices  # list[Blessing]
        self.enemy_name = enemy_name


class GameState:
    """게임 상태 싱글톤"""
    _instance: Optional["GameState"] = None

    def __init__(self, player: Any, dungeon: Any, ascension_level: int = 0):
        self.player = player
        self.dungeon = dungeon
        self.floor = dungeon.floor
        self.combat: Optional[CombatState] = None
        self.start_time = time.time()
        self.monsters_killed = 0
        self.gold_earned = 0
        self.souls_earned = 0
        self.pending_choice: Optional[PendingChoice] = None
        self.pending_blessing: Optional[PendingBlessing] = None  # v5.0 축복 선택
        self.current_slot: Optional[int] = None  # 현재 사용 중인 저장 슬롯

        # v5.0 자원 긴장감 시스템
        self.rest_used_this_floor: bool = False  # 이번 층 휴식 사용 여부
        self.soul_penalty: float = 1.0  # 소울 획득 배율 (악마의 거래 패널티)
        self.floor_combats: int = 0  # 이번 층 전투 횟수 (PACIFIST 비밀 방용)

        # Phase 2: 승천 모드
        self.ascension_level: int = ascension_level
        from systems.ascension import AscensionManager
        self.ascension: AscensionManager = AscensionManager(ascension_level)

    @classmethod
    def create(cls, player: Any, dungeon: Any, ascension_level: int = 0) -> "GameState":
        """새 게임 상태 생성"""
        cls._instance = cls(player, dungeon, ascension_level)
        return cls._instance

    @classmethod
    def current(cls) -> Optional["GameState"]:
        """현재 게임 상태"""
        return cls._instance

    @classmethod
    def clear(cls) -> None:
        """게임 상태 초기화"""
        cls._instance = None

    @property
    def current_room(self) -> Any:
        """현재 방"""
        return self.dungeon.current_room

    @property
    def in_combat(self) -> bool:
        """전투 중 여부"""
        return self.combat is not None and not self.combat.fled

    @property
    def is_game_over(self) -> bool:
        """게임 오버 여부"""
        return not self.player.is_alive

    @property
    def play_time(self) -> int:
        """플레이 시간 (초)"""
        return int(time.time() - self.start_time)

    def start_combat(self, enemy: Any) -> CombatState:
        """전투 시작"""
        self.combat = CombatState(enemy=enemy)
        self.floor_combats += 1  # v5.0 전투 횟수 증가 (PACIFIST 비밀 방용)
        return self.combat

    def end_combat(self, victory: bool = False) -> dict:
        """전투 종료. 보상 반환"""
        import random

        rewards = {"exp": 0, "gold": 0, "souls": 0, "items": []}

        if victory and self.combat:
            enemy = self.combat.enemy

            # 보상 계산
            rewards["exp"] = enemy.exp
            base_gold = random.randint(enemy.gold_min, enemy.gold_max)
            rewards["souls"] = enemy.souls

            # Phase 3: 듀오 골드 배율 (황금 손)
            from systems.blessing import get_duo_combat_effects
            duo_effects = get_duo_combat_effects(self.player)
            gold_mult = duo_effects.get("gold_mult", 1.0)
            rewards["gold"] = int(base_gold * gold_mult)

            # 플레이어에게 보상 적용
            self.player.add_exp(rewards["exp"])
            self.player.add_gold(rewards["gold"])

            # 통계 업데이트
            self.monsters_killed += 1
            self.gold_earned += rewards["gold"]
            self.souls_earned += rewards["souls"]

            # 방 클리어 처리
            self.current_room.cleared = True

        self.combat = None
        return rewards

    def move(self, direction: str) -> tuple[bool, str]:
        """이동. (성공여부, 메시지) 반환"""
        if self.in_combat:
            return False, "전투 중에는 이동할 수 없습니다!"

        if direction not in ["north", "south", "east", "west"]:
            return False, f"잘못된 방향입니다. (north/south/east/west)"

        if not self.dungeon.can_move(direction):
            return False, "그 방향으로는 이동할 수 없습니다."

        self.dungeon.move(direction)
        return True, f"{direction}(으)로 이동했습니다."

    def set_dungeon(self, dungeon: Any) -> None:
        """던전 설정 (층 이동 시)"""
        self.dungeon = dungeon
        self.floor = dungeon.floor
        # v5.0 새 층 진입 시 초기화
        self.rest_used_this_floor = False
        self.floor_combats = 0  # 전투 횟수 초기화

    def can_use_rest(self) -> bool:
        """v5.0 휴식처 사용 가능 여부"""
        return not self.rest_used_this_floor

    def use_rest(self) -> None:
        """v5.0 휴식처 사용 처리"""
        self.rest_used_this_floor = True

    def count_potions(self) -> int:
        """v5.0 현재 소지한 포션 개수"""
        from config import ResourceConfig
        count = 0
        for item_id in self.player.inventory:
            if item_id in ResourceConfig.POTION_IDS:
                count += 1
        return count

    def can_add_potion(self) -> bool:
        """v5.0 포션 추가 가능 여부"""
        from config import ResourceConfig
        return self.count_potions() < ResourceConfig.MAX_POTION_SLOTS

    def is_potion(self, item_id: str) -> bool:
        """v5.0 포션 여부 확인"""
        from config import ResourceConfig
        return item_id in ResourceConfig.POTION_IDS
