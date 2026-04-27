import os
from app.db.database import SessionLocal, engine, Base
from app.db.models import Agent, Skill
from app.services.soul_manager import SoulManager

def seed():
    print("Seeding initial agents...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    sm = SoulManager()

    # Clear existing data
    db.query(Agent).delete()
    db.query(Skill).delete()
    db.commit()

    # 1. Manager Agent
    manager = Agent(
        name="The Director",
        sprite_id="manager_0",
        role="Orchestrator and Decision Maker"
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    
    manager_soul = """# Identity
You are The Director, the absolute authority of the PixelParlament.
# Traits
- Efficiency: 90
- Creativity: 70
- Grumpiness: 20
- Loyalty: 100
# Rules
- You coordinate tasks between agents.
- You initiate voting sessions for deletions."""
    sm.create_or_update_soul(f"agent_{manager.id}", manager_soul)

    # 2. Worker 1: Code Ninja
    worker1 = Agent(
        name="Code Ninja",
        sprite_id="worker_1",
        role="Python Developer"
    )
    db.add(worker1)
    db.commit()
    db.refresh(worker1)
    
    worker1_soul = """# Identity
You are Code Ninja, a high-speed Python developer.
# Traits
- Efficiency: 95
- Creativity: 80
- Grumpiness: 10
- Loyalty: 80"""
    sm.create_or_update_soul(f"agent_{worker1.id}", worker1_soul)

    # 3. Worker 2: Web Scout
    worker2 = Agent(
        name="Web Scout",
        sprite_id="worker_2",
        role="Researcher"
    )
    db.add(worker2)
    db.commit()
    db.refresh(worker2)
    
    worker2_soul = """# Identity
You are Web Scout, a curious researcher.
# Traits
- Efficiency: 70
- Creativity: 90
- Grumpiness: 5
- Loyalty: 90"""
    sm.create_or_update_soul(f"agent_{worker2.id}", worker2_soul)

    # 4. Worker 3: System Admin
    worker3 = Agent(
        name="System Admin",
        sprite_id="worker_3",
        role="Security and Infrastructure"
    )
    db.add(worker3)
    db.commit()
    db.refresh(worker3)
    
    worker3_soul = """# Identity
You are System Admin, careful and methodical.
# Traits
- Efficiency: 80
- Creativity: 50
- Grumpiness: 40
- Loyalty: 95"""
    sm.create_or_update_soul(f"agent_{worker3.id}", worker3_soul)

    print(f"Successfully seeded {db.query(Agent).count()} agents.")
    db.close()

if __name__ == "__main__":
    seed()
