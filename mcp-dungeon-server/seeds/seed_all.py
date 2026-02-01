"""시드 데이터 전체 실행"""
import asyncio
from repository.database import Database


async def seed_all(force: bool = False) -> dict:
    """
    모든 시드 데이터 삽입

    Args:
        force: True면 기존 데이터 삭제 후 재삽입

    Returns:
        삽입 결과 통계
    """
    db = await Database.connect()
    stats = {}

    if force:
        await _clear_content_tables(db)
        print("[OK] Cleared content tables")

    # 직업 시드
    if await _is_empty(db, "classes"):
        from seeds.classes import seed_classes
        count = await seed_classes(db)
        stats["classes"] = count
        print(f"[OK] Classes: {count}")

    # 몬스터 시드
    if await _is_empty(db, "monsters"):
        from seeds.monsters import seed_monsters
        count = await seed_monsters(db)
        stats["monsters"] = count
        print(f"[OK] Monsters: {count}")

    # 아이템 시드
    if await _is_empty(db, "items"):
        from seeds.items import seed_items
        count = await seed_items(db)
        stats["items"] = count
        print(f"[OK] Items: {count}")

    # 스킬 시드
    if await _is_empty(db, "skills"):
        from seeds.skills import seed_skills
        count = await seed_skills(db)
        stats["skills"] = count
        print(f"[OK] Skills: {count}")

    # 이벤트 시드
    if await _is_empty(db, "events"):
        from seeds.events import seed_events
        count = await seed_events(db)
        stats["events"] = count
        print(f"[OK] Events: {count}")

    # 업적 시드
    if await _is_empty(db, "achievements"):
        from seeds.achievements import seed_achievements
        count = await seed_achievements(db)
        stats["achievements"] = count
        print(f"[OK] Achievements: {count}")

    await db.commit()

    if stats:
        print(f"\n[DONE] Seed completed: {sum(stats.values())} total")
    else:
        print("[INFO] Seed data already exists")

    return stats


async def _is_empty(db, table: str) -> bool:
    """테이블이 비어있는지 확인"""
    cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
    count = (await cursor.fetchone())[0]
    return count == 0


async def _clear_content_tables(db) -> None:
    """콘텐츠 테이블 초기화"""
    tables = [
        "monster_drops",
        "monsters",
        "items",
        "skills",
        "events",
        "achievements",
        "classes",
    ]
    for table in tables:
        await db.execute(f"DELETE FROM {table}")
    await db.commit()


# CLI 실행용
if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    asyncio.run(seed_all(force=force))
