"""MCP 서버 실행 래퍼 - 에러 로깅"""
import sys
import traceback

LOG_FILE = r"C:\Users\DamonKim\Desktop\claude\Side\3.mcp-dungeon\mcp-dungeon-server\server_error.log"

try:
    # 원래 서버 실행
    import asyncio
    from mcp.server.fastmcp import FastMCP
    from repository.database import Database
    from seeds.seed_all import seed_all

    # server.py의 내용을 직접 import
    from server import server, init_db

    # DB 초기화
    asyncio.run(init_db())

    # MCP 서버 실행
    server.run()

except Exception as e:
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"Error: {e}\n\n")
        f.write(traceback.format_exc())
    raise
