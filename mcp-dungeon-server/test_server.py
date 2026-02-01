"""Server test script"""
import asyncio
import sys
import io

# Windows console UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def test():
    # DB init
    from repository.database import Database
    from seeds.seed_all import seed_all

    print("Initializing DB...")
    await Database.connect()
    print("DB connected")

    print("Seeding data...")
    await seed_all()
    print("Seed done")

    # Check tool registration
    from server import server
    print(f"Server name: {server.name}")

    # Simple tool test
    from tools import game
    result = await game.get_status()
    print(f"\nget_status test:")
    print(result[:300] if len(result) > 300 else result)

    print("\n[SUCCESS] Server test passed!")

if __name__ == "__main__":
    asyncio.run(test())
