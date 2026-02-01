"""던전 생성 시스템"""
import random
from collections import deque
from models.dungeon import Dungeon, Room, RoomType, Position

# 맵 크기 (층별) - v4.0: 5층 구조
MAP_SIZES = {
    1: (4, 4),   # 하수도
    2: (4, 5),   # 지하 감옥
    3: (5, 5),   # 마석 광산
    4: (5, 5),   # 심연의 사원
    5: (6, 5),   # 최종 심층부
}

# 층별 목표 방 개수 - v4.0: 5층 구조
ROOM_COUNTS = {
    1: (8, 10),   # 하수도: 간결한 입문
    2: (10, 12),  # 지하 감옥
    3: (12, 15),  # 마석 광산
    4: (14, 17),  # 심연의 사원
    5: (16, 20),  # 최종 심층부
}

# 이벤트 확률 - v4.0: 몬스터↑, 보물↓
EVENT_RATIOS = {
    "monster": 0.45,   # 40% → 45%
    "treasure": 0.12,  # 20% → 12% (보물 감소)
    "trap": 0.18,      # 15% → 18% (함정 증가)
    "shop": 0.10,
    "rest": 0.10,
    "mystery": 0.05,
}


def generate_dungeon(floor: int) -> Dungeon:
    """
    Random Walk 기반 던전 생성

    Args:
        floor: 층 번호 (1~5) - v4.0 기준

    Returns:
        생성된 던전
    """
    width, height = MAP_SIZES.get(floor, (5, 5))
    min_rooms, max_rooms = ROOM_COUNTS.get(floor, (14, 18))
    target_rooms = random.randint(min_rooms, max_rooms)

    # 1. 모든 셀을 벽으로 초기화
    rooms: list[list[Room]] = [
        [Room(x=x, y=y, type=RoomType.WALL) for x in range(width)]
        for y in range(height)
    ]

    # 2. 시작점 배치 (좌상단 1/4 영역)
    start_x = random.randint(0, width // 4)
    start_y = random.randint(0, height // 4)
    rooms[start_y][start_x] = Room(x=start_x, y=start_y, type=RoomType.START, visited=True)

    generated_positions = [(start_x, start_y)]

    # 3. Random Walk로 방 생성
    current = (start_x, start_y)
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    attempts = 0
    max_attempts = target_rooms * 10

    while len(generated_positions) < target_rooms and attempts < max_attempts:
        attempts += 1
        dx, dy = random.choice(directions)
        nx, ny = current[0] + dx, current[1] + dy

        if 0 <= nx < width and 0 <= ny < height:
            if rooms[ny][nx].type == RoomType.WALL:
                rooms[ny][nx] = Room(x=nx, y=ny, type=RoomType.EMPTY)
                generated_positions.append((nx, ny))
            current = (nx, ny)

    # 4. 보스방 배치 (시작점에서 가장 먼 방)
    # v4.0: 1~4층 50% 확률, 5층 100% 확률
    has_boss = floor >= 5 or random.random() < 0.5

    boss_pos = max(
        generated_positions[1:],  # 시작점 제외
        key=lambda p: abs(p[0] - start_x) + abs(p[1] - start_y),
        default=(width - 1, height - 1)
    )

    if has_boss:
        rooms[boss_pos[1]][boss_pos[0]] = Room(x=boss_pos[0], y=boss_pos[1], type=RoomType.BOSS)
    else:
        # 1층 보스 없는 경우: 계단만 배치
        rooms[boss_pos[1]][boss_pos[0]] = Room(x=boss_pos[0], y=boss_pos[1], type=RoomType.EXIT)

    # 5. 계단 배치 (보스방 인접, 보스가 있을 때만)
    if has_boss:
        exit_pos = _place_adjacent(rooms, boss_pos, RoomType.EXIT, width, height)
        if exit_pos is None:
            # 인접 공간이 없으면 보스방 위치에 계단도 함께
            exit_pos = boss_pos
    else:
        # 보스 없으면 boss_pos가 곧 exit_pos
        exit_pos = boss_pos

    # 6. 경로 보장 검증
    if not _has_path(rooms, (start_x, start_y), boss_pos, width, height):
        _connect_rooms(rooms, (start_x, start_y), boss_pos, width, height)

    # 7. 이벤트 방 배치
    _assign_room_events(rooms, generated_positions, start_x, start_y, boss_pos, exit_pos)

    return Dungeon(
        floor=floor,
        width=width,
        height=height,
        rooms=rooms,
        start_pos=Position(x=start_x, y=start_y),
        boss_pos=Position(x=boss_pos[0], y=boss_pos[1]),
        exit_pos=Position(x=exit_pos[0], y=exit_pos[1]),
        current_pos=Position(x=start_x, y=start_y),
    )


def _place_adjacent(
    rooms: list[list[Room]],
    pos: tuple[int, int],
    room_type: RoomType,
    width: int,
    height: int
) -> tuple[int, int] | None:
    """인접한 빈 공간에 방 배치"""
    x, y = pos
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            if rooms[ny][nx].type == RoomType.WALL:
                rooms[ny][nx] = Room(x=nx, y=ny, type=room_type)
                return (nx, ny)
            elif rooms[ny][nx].type == RoomType.EMPTY:
                rooms[ny][nx].type = room_type
                return (nx, ny)
    return None


def _has_path(
    rooms: list[list[Room]],
    start: tuple[int, int],
    end: tuple[int, int],
    width: int,
    height: int
) -> bool:
    """BFS로 경로 존재 확인"""
    visited = set()
    queue = deque([start])

    while queue:
        x, y = queue.popleft()
        if (x, y) == end:
            return True
        if (x, y) in visited:
            continue
        visited.add((x, y))

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if rooms[ny][nx].type != RoomType.WALL:
                    queue.append((nx, ny))

    return False


def _connect_rooms(
    rooms: list[list[Room]],
    start: tuple[int, int],
    end: tuple[int, int],
    width: int,
    height: int
) -> None:
    """두 방 사이 경로 생성 (L자 형태)"""
    x1, y1 = start
    x2, y2 = end

    # 수평 이동
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if rooms[y1][x].type == RoomType.WALL:
            rooms[y1][x] = Room(x=x, y=y1, type=RoomType.EMPTY)

    # 수직 이동
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if rooms[y][x2].type == RoomType.WALL:
            rooms[y][x2] = Room(x=x2, y=y, type=RoomType.EMPTY)


def _assign_room_events(
    rooms: list[list[Room]],
    positions: list[tuple[int, int]],
    start_x: int,
    start_y: int,
    boss_pos: tuple[int, int],
    exit_pos: tuple[int, int]
) -> None:
    """빈 방에 이벤트 타입 할당"""
    # 이벤트 할당 대상 방 필터링
    empty_rooms = [
        (x, y) for x, y in positions
        if rooms[y][x].type == RoomType.EMPTY
        and (x, y) != (start_x, start_y)
        and (x, y) != boss_pos
        and (x, y) != exit_pos
    ]

    if not empty_rooms:
        return

    # 이벤트 타입별 개수 계산
    total = len(empty_rooms)
    event_counts = {
        RoomType.MONSTER: int(total * EVENT_RATIOS["monster"]),
        RoomType.TREASURE: int(total * EVENT_RATIOS["treasure"]),
        RoomType.TRAP: int(total * EVENT_RATIOS["trap"]),
        RoomType.SHOP: max(1, int(total * EVENT_RATIOS["shop"])),  # 최소 1개
        RoomType.REST: max(1, int(total * EVENT_RATIOS["rest"])),  # 최소 1개
        RoomType.MYSTERY: int(total * EVENT_RATIOS["mystery"]),
    }

    # 이벤트 리스트 생성
    events = []
    for event_type, count in event_counts.items():
        events.extend([event_type] * count)

    # 남은 방은 몬스터로 채움
    while len(events) < total:
        events.append(RoomType.MONSTER)

    # 셔플 후 할당
    random.shuffle(events)
    random.shuffle(empty_rooms)

    for (x, y), event_type in zip(empty_rooms, events):
        rooms[y][x].type = event_type
