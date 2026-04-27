import asyncio
import os
from app.db.database import get_db, engine
from app.db.models import Agent, Skill
from app.services.soul_manager import SoulManager
from app.core.llm import ModelFactory
from app.core.config import settings

async def main():
    print("--- Verifying Database ---")
    from app.db.database import Base
    Base.metadata.create_all(bind=engine)
    
    # Add a mock agent and skill
    db = next(get_db())
    try:
        new_skill = Skill(name="test_skill", description="A test skill")
        db.add(new_skill)
        db.commit()
        
        new_agent = Agent(name="TestAgent", sprite_id="agent_1", role="Tester")
        new_agent.skills.append(new_skill)
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        
        print(f"Created Agent: {new_agent.name} with Skill: {new_agent.skills[0].name}")
    except Exception as e:
        print("DB already initialized or error:", e)
        db.rollback()
        
    print("\n--- Verifying SoulManager ---")
    sm = SoulManager()
    agent_id = "agent_1"
    
    mock_soul_content = """# Identity
You are a test agent.
# Traits
- Efficiency: 100
- Grumpiness: 0"""
    
    sm.create_or_update_soul(agent_id, mock_soul_content)
    retrieved_content = sm.get_soul(agent_id)
    print(f"Retrieved soul:\n{retrieved_content}")
    print("\nGenerated System Message:")
    print(sm.generate_system_message(agent_id, "This is the base system message."))

    print("\n--- Verifying ModelFactory Setup ---")
    ModelFactory.setup()
    print(f"LiteLLM base set to: {settings.OLLAMA_API_BASE}")
    print("Default Model:", ModelFactory.get_default_model())

if __name__ == "__main__":
    asyncio.run(main())
