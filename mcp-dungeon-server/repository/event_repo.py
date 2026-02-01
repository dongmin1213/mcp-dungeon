"""이벤트 Repository"""
import json
import random
from typing import Optional
from repository.database import Database


class EventRepository:
    """이벤트 데이터 조회"""

    @staticmethod
    async def get_by_id(event_id: str) -> Optional[dict]:
        """ID로 이벤트 조회"""
        db = await Database.connect()
        cursor = await db.execute(
            "SELECT * FROM events WHERE id = ?", (event_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return EventRepository._parse_event(dict(row))

    @staticmethod
    async def get_by_type(event_type: str, floor: int) -> list[dict]:
        """타입별 이벤트 목록"""
        db = await Database.connect()
        cursor = await db.execute("""
            SELECT * FROM events
            WHERE type = ? AND floor_min <= ? AND floor_max >= ?
        """, (event_type, floor, floor))
        return [EventRepository._parse_event(dict(row)) for row in await cursor.fetchall()]

    @staticmethod
    async def get_random_by_type(event_type: str, floor: int) -> Optional[dict]:
        """타입별 랜덤 이벤트"""
        events = await EventRepository.get_by_type(event_type, floor)
        if not events:
            return None
        return random.choice(events)

    @staticmethod
    async def get_trap(floor: int) -> Optional[dict]:
        """함정 이벤트"""
        return await EventRepository.get_random_by_type("trap", floor)

    @staticmethod
    async def get_treasure(floor: int) -> Optional[dict]:
        """보물 이벤트"""
        return await EventRepository.get_random_by_type("treasure", floor)

    @staticmethod
    async def get_rest(floor: int) -> Optional[dict]:
        """휴식 이벤트"""
        return await EventRepository.get_random_by_type("rest", floor)

    @staticmethod
    async def get_mystery(floor: int) -> Optional[dict]:
        """미스터리 이벤트"""
        return await EventRepository.get_random_by_type("mystery", floor)

    @staticmethod
    def _parse_event(row: dict) -> dict:
        """DB row 파싱 (JSON 필드 변환)"""
        return {
            "id": row["id"],
            "name": row["name"],
            "type": row["type"],
            "description": row["description"],
            "floor_min": row["floor_min"],
            "floor_max": row["floor_max"],
            "effect": json.loads(row["effect"]) if row.get("effect") else None,
            "choices": json.loads(row["choices"]) if row.get("choices") else None,
            "requires": json.loads(row["requires"]) if row.get("requires") else None,
            "rewards": json.loads(row["rewards"]) if row.get("rewards") else None,
        }
