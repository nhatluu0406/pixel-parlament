import asyncio
import httpx
from pydantic import BaseModel

class AgentCreate(BaseModel):
    name: str
    role: str
    sprite_id: str
    efficiency: int = 50
    creativity: int = 50
    grumpiness: int = 50
    loyalty: int = 50

async def test_admin():
    print("Testing Backend APIs...")
    async with httpx.AsyncClient() as client:
        # NOTE: We can't actually easily call the API unless uvicorn is running.
        # But we can import main and call it directly.
        pass

if __name__ == "__main__":
    asyncio.run(test_admin())
