"""저장 데이터 저장소"""
import json
from typing import Optional
from datetime import datetime
from systems.save_load import SaveSlot


class SaveRepository:
    """저장 데이터 CRUD"""

    MAX_SLOTS = 5

    def __init__(self, db):
        self.db = db

    async def get_slot(self, slot_id: int) -> SaveSlot:
        """저장 슬롯 조회"""
        if slot_id < 1 or slot_id > self.MAX_SLOTS:
            return SaveSlot(slot_id)

        cursor = await self.db.execute(
            "SELECT data FROM save_slots WHERE slot_id = ?",
            (slot_id,)
        )
        row = await cursor.fetchone()

        if row:
            data = json.loads(row[0])
            return SaveSlot(slot_id, data)
        return SaveSlot(slot_id)

    async def save_slot(self, slot_id: int, data: dict) -> bool:
        """저장 슬롯에 저장"""
        if slot_id < 1 or slot_id > self.MAX_SLOTS:
            return False

        await self.db.execute("""
            INSERT INTO save_slots (slot_id, data, saved_at)
            VALUES (?, ?, ?)
            ON CONFLICT(slot_id) DO UPDATE SET
                data = excluded.data,
                saved_at = excluded.saved_at
        """, (
            slot_id,
            json.dumps(data),
            datetime.now().isoformat()
        ))
        await self.db.commit()
        return True

    async def delete_slot(self, slot_id: int) -> bool:
        """저장 슬롯 삭제"""
        if slot_id < 1 or slot_id > self.MAX_SLOTS:
            return False

        await self.db.execute(
            "DELETE FROM save_slots WHERE slot_id = ?",
            (slot_id,)
        )
        await self.db.commit()
        return True

    async def get_all_slots(self) -> list[SaveSlot]:
        """모든 저장 슬롯 조회"""
        slots = []
        for i in range(1, self.MAX_SLOTS + 1):
            slot = await self.get_slot(i)
            slots.append(slot)
        return slots


async def create_save_table(db) -> None:
    """저장 슬롯 테이블 생성"""
    await db.execute("""
        CREATE TABLE IF NOT EXISTS save_slots (
            slot_id INTEGER PRIMARY KEY,
            data TEXT NOT NULL,
            saved_at TEXT NOT NULL
        )
    """)
    await db.commit()
