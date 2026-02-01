"""MCP 던전 서버 - 진입점"""
import asyncio
from mcp.server.fastmcp import FastMCP
from typing import Optional

from repository.database import Database
from seeds.seed_all import seed_all
from tools import game, combat, inventory, shop, skill, help as help_tool
from tools import meta, save, ranking

# MCP 서버 인스턴스 생성
server = FastMCP("mcp-dungeon")


# ===== 게임 진행 도구 등록 =====

@server.tool()
async def start_game(player_name: str = "", ascension: int = 0) -> str:
    """
    새로운 던전 탐험을 시작합니다.
    직업은 전사/궁수 중 랜덤으로 선택됩니다.

    Args:
        player_name: 플레이어 이름 (빈 문자열이면 세이브 확인)
        ascension: 승천 레벨 (0-10, 기본 0). 높을수록 어려움
    """
    return await game.start_game(player_name, ascension)


@server.tool()
async def get_status() -> str:
    """현재 게임 상태를 확인합니다."""
    return await game.get_status()


@server.tool()
async def move(direction: str) -> str:
    """
    지정한 방향으로 이동합니다.

    Args:
        direction: 이동 방향 (north/south/east/west)
    """
    return await game.move(direction)


@server.tool()
async def interact(choice: int = 0) -> str:
    """
    현재 방과 상호작용합니다.

    Args:
        choice: 선택지 번호 (1, 2, 3 등). 0이면 선택지 표시
    """
    return await game.interact(choice)


@server.tool()
async def get_map() -> str:
    """현재 층의 미니맵을 확인합니다."""
    return await game.get_map()


# ===== 전투 도구 등록 =====

@server.tool()
async def attack() -> str:
    """적을 공격합니다."""
    return await combat.attack()


@server.tool()
async def defend() -> str:
    """방어 자세를 취합니다. 이번 턴 받는 데미지가 50% 감소합니다."""
    return await combat.defend()


@server.tool()
async def flee() -> str:
    """전투에서 도망칩니다. 보스전에서는 도망칠 수 없습니다."""
    return await combat.flee()


@server.tool()
async def choose_blessing(choice: int) -> str:
    """
    전투 승리 후 축복을 선택합니다.

    Args:
        choice: 선택 번호 (1, 2, 3)
    """
    return await combat.choose_blessing(choice)


@server.tool()
async def use_skill(skill_id: str) -> str:
    """
    스킬을 사용합니다.

    Args:
        skill_id: 스킬 ID
    """
    return await skill.use_skill(skill_id)


@server.tool()
async def get_skills() -> str:
    """보유한 스킬 목록을 확인합니다."""
    return await skill.get_skills()


# ===== 인벤토리 도구 등록 =====

@server.tool()
async def get_inventory() -> str:
    """인벤토리를 확인합니다."""
    return await inventory.get_inventory()


@server.tool()
async def use_item(item_id: str) -> str:
    """
    소비 아이템을 사용합니다.

    Args:
        item_id: 아이템 ID
    """
    return await inventory.use_item(item_id)


@server.tool()
async def equip(item_id: str) -> str:
    """
    아이템을 장착합니다.

    Args:
        item_id: 아이템 ID
    """
    return await inventory.equip(item_id)


@server.tool()
async def unequip(slot: str) -> str:
    """
    장비를 해제합니다.

    Args:
        slot: 장비 슬롯 (weapon/armor/helmet/accessory1/accessory2)
    """
    return await inventory.unequip(slot)


# ===== 상점 도구 등록 =====

@server.tool()
async def shop_list() -> str:
    """상점 목록을 확인합니다."""
    return await shop.shop_list()


@server.tool()
async def buy(item_id: str) -> str:
    """
    아이템을 구매합니다.

    Args:
        item_id: 아이템 ID
    """
    return await shop.buy(item_id)


@server.tool()
async def sell(item_id: str) -> str:
    """
    아이템을 판매합니다. (구매가의 50%)

    Args:
        item_id: 아이템 ID
    """
    return await shop.sell(item_id)


# ===== 도움말 도구 등록 =====

@server.tool()
async def get_help(topic: str = "") -> str:
    """
    게임 도움말을 확인합니다.

    Args:
        topic: 도움말 주제 (commands/combat/skills/items/classes/status/dungeon)
    """
    return await help_tool.get_help(topic)


# ===== 메타 프로그레션 도구 등록 (Phase 4) =====

@server.tool()
async def get_profile() -> str:
    """플레이어 프로필과 영구 통계를 확인합니다."""
    return await meta.get_profile()


@server.tool()
async def get_souls() -> str:
    """소울 정보와 구매 가능한 업그레이드를 확인합니다."""
    return await meta.get_souls()


@server.tool()
async def upgrade(upgrade_id: str) -> str:
    """
    소울을 사용하여 영구 업그레이드를 구매합니다.

    Args:
        upgrade_id: 업그레이드 ID (max_hp/max_mp/atk/def/crit/gold/exp/potion/starting_gold/soul)
    """
    return await meta.upgrade(upgrade_id)


@server.tool()
async def unlock(unlock_id: str) -> str:
    """
    직업, 모드, 아이템을 해금합니다.

    Args:
        unlock_id: 해금할 대상 ID
    """
    return await meta.unlock(unlock_id)


@server.tool()
async def get_achievements() -> str:
    """업적 목록과 진행 상황을 확인합니다."""
    return await meta.get_achievements()


@server.tool()
async def get_unlocks() -> str:
    """해금 가능한 콘텐츠 목록을 확인합니다."""
    return await meta.get_unlocks()


# ===== 저장/불러오기 도구 등록 (Phase 5) =====

@server.tool()
async def save_game(slot: int = 0) -> str:
    """
    현재 게임을 저장합니다.

    Args:
        slot: 저장 슬롯 번호 (1-5, 0이면 현재 플레이 슬롯 사용)
    """
    return await save.save_game(slot)


@server.tool()
async def load_game(slot: int = 1) -> str:
    """
    저장된 게임을 불러옵니다.

    Args:
        slot: 저장 슬롯 번호 (1-5)
    """
    return await save.load_game(slot)


@server.tool()
async def get_save_slots() -> str:
    """저장 슬롯 목록을 확인합니다."""
    return await save.get_save_slots()


@server.tool()
async def delete_save(slot: int) -> str:
    """
    저장 슬롯을 삭제합니다.

    Args:
        slot: 삭제할 슬롯 번호 (1-5)
    """
    return await save.delete_save(slot)


# ===== 랭킹 도구 등록 (Phase 5) =====

@server.tool()
async def get_ranking(mode: Optional[str] = None) -> str:
    """
    랭킹을 조회합니다.

    Args:
        mode: 모드 필터 (normal/hard/hell/infinite 또는 비워두면 전체)
    """
    return await ranking.get_ranking(mode)


@server.tool()
async def get_records() -> str:
    """개인 플레이 기록을 확인합니다."""
    return await ranking.get_records()


# ===== 서버 실행 =====

async def init_db():
    """DB 초기화 및 시드"""
    await Database.connect()
    await seed_all()


if __name__ == "__main__":
    # DB 초기화
    asyncio.run(init_db())

    # MCP 서버 실행 (stdio 모드)
    server.run()
