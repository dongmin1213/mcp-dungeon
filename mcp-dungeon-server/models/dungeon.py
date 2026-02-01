"""던전/방 모델"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RoomType(str, Enum):
    """방 타입"""
    WALL = "wall"
    START = "start"
    EMPTY = "empty"
    MONSTER = "monster"
    TREASURE = "treasure"
    SHOP = "shop"
    REST = "rest"
    TRAP = "trap"
    MYSTERY = "mystery"
    BOSS = "boss"
    EXIT = "exit"
    SECRET = "secret"  # v5.0 비밀 방


# 방 타입별 아이콘
ROOM_ICONS = {
    RoomType.WALL: "█",
    RoomType.START: "S",
    RoomType.EMPTY: "·",
    RoomType.MONSTER: "M",
    RoomType.TREASURE: "T",
    RoomType.SHOP: "P",
    RoomType.REST: "R",
    RoomType.TRAP: "!",
    RoomType.MYSTERY: "?",
    RoomType.BOSS: "B",
    RoomType.EXIT: "E",
    RoomType.SECRET: "★",  # v5.0
}

ROOM_NAMES = {
    RoomType.WALL: "벽",
    RoomType.START: "시작점",
    RoomType.EMPTY: "빈 방",
    RoomType.MONSTER: "몬스터 방",
    RoomType.TREASURE: "보물 방",
    RoomType.SHOP: "상점",
    RoomType.REST: "휴식처",
    RoomType.TRAP: "함정",
    RoomType.MYSTERY: "미스터리",
    RoomType.BOSS: "보스 방",
    RoomType.EXIT: "계단",
    RoomType.SECRET: "비밀 방",  # v5.0
}


class Room(BaseModel):
    """던전 방"""
    x: int
    y: int
    type: RoomType
    visited: bool = False
    cleared: bool = False  # 이벤트 완료 여부 (몬스터 처치, 보물 획득 등)
    event_id: Optional[str] = None  # 이벤트 ID
    monster_id: Optional[str] = None  # 몬스터 ID (몬스터 방일 경우)

    @property
    def icon(self) -> str:
        """맵에 표시할 아이콘 (클리어된 방은 빈 방으로 표시)"""
        if self.cleared and self.type not in [RoomType.SHOP, RoomType.EXIT, RoomType.START]:
            return ROOM_ICONS[RoomType.EMPTY]
        return ROOM_ICONS.get(self.type, "?")

    @property
    def name(self) -> str:
        """방 이름 (ISSUE-004 수정: 클리어 후에도 원래 타입명 + 상태 표시)"""
        base_name = ROOM_NAMES.get(self.type, "알 수 없는 방")
        if self.cleared and self.type not in [RoomType.SHOP, RoomType.EXIT, RoomType.START, RoomType.WALL, RoomType.EMPTY]:
            return f"{base_name} (클리어됨)"
        return base_name

    @property
    def can_enter(self) -> bool:
        """진입 가능 여부"""
        return self.type != RoomType.WALL


class Position(BaseModel):
    """위치"""
    x: int
    y: int

    def __eq__(self, other) -> bool:
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash((self.x, self.y))


class Dungeon(BaseModel):
    """던전 (한 층)"""
    floor: int
    width: int
    height: int
    rooms: list[list[Room]]  # 2D 그리드
    start_pos: Position
    boss_pos: Position
    exit_pos: Position
    current_pos: Position

    @property
    def current_room(self) -> Room:
        """현재 방"""
        return self.rooms[self.current_pos.y][self.current_pos.x]

    def get_room(self, x: int, y: int) -> Optional[Room]:
        """특정 좌표의 방 반환"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.rooms[y][x]
        return None

    def get_adjacent_rooms(self) -> dict[str, Optional[Room]]:
        """인접한 방들 반환"""
        x, y = self.current_pos.x, self.current_pos.y
        return {
            "north": self.get_room(x, y - 1),
            "south": self.get_room(x, y + 1),
            "east": self.get_room(x + 1, y),
            "west": self.get_room(x - 1, y),
        }

    def can_move(self, direction: str) -> bool:
        """해당 방향으로 이동 가능한지"""
        adjacent = self.get_adjacent_rooms()
        room = adjacent.get(direction)
        return room is not None and room.can_enter

    def move(self, direction: str) -> bool:
        """이동. 성공 여부 반환"""
        if not self.can_move(direction):
            return False

        dx, dy = {
            "north": (0, -1),
            "south": (0, 1),
            "east": (1, 0),
            "west": (-1, 0),
        }.get(direction, (0, 0))

        self.current_pos.x += dx
        self.current_pos.y += dy
        self.current_room.visited = True
        return True

    def get_minimap(self, reveal_all: bool = False) -> str:
        """미니맵 문자열 생성"""
        lines = []
        lines.append("┌" + "───┬" * (self.width - 1) + "───┐")

        for y in range(self.height):
            row = "│"
            for x in range(self.width):
                room = self.rooms[y][x]

                # 현재 위치
                if x == self.current_pos.x and y == self.current_pos.y:
                    cell = " @ "
                # 방문했거나 전체 공개
                elif room.visited or reveal_all:
                    cell = f" {room.icon} "
                # 미방문
                else:
                    cell = "   "

                row += cell + "│"
            lines.append(row)

            # 행 구분선
            if y < self.height - 1:
                lines.append("├" + "───┼" * (self.width - 1) + "───┤")

        lines.append("└" + "───┴" * (self.width - 1) + "───┘")
        return "\n".join(lines)
