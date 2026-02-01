"""게임 저장/불러오기 시스템"""
import json
from datetime import datetime
from typing import Optional, Any
from state.game_state import GameState


class SaveData:
    """저장 데이터 구조"""

    @staticmethod
    def serialize_game(game: GameState) -> dict:
        """게임 상태를 직렬화"""
        return {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "player": {
                "name": game.player.name,
                "class_id": game.player.class_type,
                "level": game.player.level,
                "exp": game.player.exp,
                "hp": game.player.hp,
                "max_hp": game.player.max_hp,
                "mp": game.player.mp,
                "max_mp": game.player.max_mp,
                "atk": game.player.atk,
                "def_": game.player.def_,
                "gold": game.player.gold,
                "crit_chance": game.player.crit_chance,
                "inventory": game.player.inventory,
                "equipment": game.player.equipment,
                "skills": game.player.skills,
            },
            "dungeon": {
                "floor": game.dungeon.floor,
                "width": game.dungeon.width,
                "height": game.dungeon.height,
                "rooms": _serialize_rooms(game.dungeon.rooms),
                "current_pos": [game.dungeon.current_pos.x, game.dungeon.current_pos.y],
                "start_pos": [game.dungeon.start_pos.x, game.dungeon.start_pos.y],
                "boss_pos": [game.dungeon.boss_pos.x, game.dungeon.boss_pos.y],
                "exit_pos": [game.dungeon.exit_pos.x, game.dungeon.exit_pos.y],
            },
            "stats": {
                "floor": game.floor,
                "monsters_killed": game.monsters_killed,
                "gold_earned": game.gold_earned,
                "souls_earned": game.souls_earned,
                "play_time": game.play_time,
            },
            "mode": getattr(game, "mode", "normal"),
        }

    @staticmethod
    def deserialize_game(data: dict) -> dict:
        """저장 데이터를 게임 상태로 변환"""
        return data


def _serialize_rooms(rooms: list[list]) -> dict:
    """방 데이터 직렬화 (2D 리스트 → dict)"""
    result = {}
    for y, row in enumerate(rooms):
        for x, room in enumerate(row):
            key = f"{x},{y}"
            result[key] = {
                "type": room.type.value if hasattr(room.type, 'value') else str(room.type),
                "cleared": room.cleared,
                "visited": room.visited,
                "event_id": room.event_id,
                "monster_id": room.monster_id,
            }
    return result


def _deserialize_rooms(data: dict) -> dict:
    """방 데이터 역직렬화"""
    result = {}
    for key, room_data in data.items():
        x, y = map(int, key.split(","))
        result[(x, y)] = room_data
    return result


class SaveSlot:
    """저장 슬롯"""
    def __init__(self, slot_id: int, data: Optional[dict] = None):
        self.slot_id = slot_id
        self.data = data
        self.saved_at = None
        self.summary = None

        if data:
            self.saved_at = data.get("saved_at")
            self.summary = self._create_summary(data)

    def _create_summary(self, data: dict) -> dict:
        """저장 데이터 요약"""
        player = data.get("player", {})
        stats = data.get("stats", {})
        return {
            "name": player.get("name", "???"),
            "class_id": player.get("class_id", "warrior"),
            "level": player.get("level", 1),
            "hp": player.get("hp", 0),
            "max_hp": player.get("max_hp", 0),
            "gold": player.get("gold", 0),
            "floor": stats.get("floor", 1),
            "play_time": stats.get("play_time", 0),
            "mode": data.get("mode", "normal"),
        }

    def is_empty(self) -> bool:
        return self.data is None
