from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import engine, Base, get_db, SessionLocal
from app.db.models import Agent, Skill
from app.api.websocket import manager
from app.services.soul_manager import SoulManager
from app.orchestrator.graph import orchestrator
from langchain_core.messages import HumanMessage
import httpx
from app.core.llm import ModelFactory

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

soul_manager = SoulManager()

# --- Seed default agents on startup ---
DEFAULT_AGENTS = [
    {"name": "The Director", "role": "Manager / Orchestrator", "sprite_id": "agent_0"},
    {"name": "Code Ninja", "role": "File Manager & Coder", "sprite_id": "agent_1"},
    {"name": "Web Scout", "role": "Web Search Specialist", "sprite_id": "agent_2"},
    {"name": "Sys Admin", "role": "System Administration", "sprite_id": "agent_3"},
]

@app.on_event("startup")
def startup_event():
    # Initialize LiteLLM settings
    ModelFactory.setup()
    
    db = SessionLocal()
    try:
        if db.query(Agent).count() == 0:
            for data in DEFAULT_AGENTS:
                agent = Agent(
                    name=data["name"],
                    role=data["role"],
                    sprite_id=data["sprite_id"],
                    status="idle"
                )
                db.add(agent)
            db.commit()
            print(f"[SEED] Created {len(DEFAULT_AGENTS)} default agents.")
        else:
            print(f"[SEED] Agents already exist, skipping seed.")
    finally:
        db.close()

# --- WebSocket ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Agent CRUD ---
@app.get("/api/agents")
def get_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    return [{"id": a.id, "name": a.name, "role": a.role, "sprite_id": a.sprite_id, "status": a.status or "idle"} for a in agents]

@app.post("/api/agents")
def create_agent(payload: dict = Body(...), db: Session = Depends(get_db)):
    new_agent = Agent(
        name=payload.get("name"),
        role=payload.get("role"),
        sprite_id=payload.get("sprite_id", "agent_1"),
        status="idle"
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    # Initialize soul file
    soul_content = f"""# {new_agent.name}
## Identity
Role: {new_agent.role}

## Traits
- Efficiency: {payload.get('efficiency', 50)}
- Creativity: {payload.get('creativity', 50)}
- Grumpiness: {payload.get('grumpiness', 50)}
"""
    soul_manager.create_or_update_soul(str(new_agent.id), soul_content)

    return {"id": new_agent.id, "name": new_agent.name, "role": new_agent.role, "sprite_id": new_agent.sprite_id, "status": new_agent.status}

# --- Chat ---
@app.post("/api/chat")
async def chat_with_manager(payload: dict = Body(...)):
    user_msg = payload.get("message")

    db = SessionLocal()
    agents = db.query(Agent).all()
    active_workers = [{"id": str(a.id), "name": a.name, "role": a.role} for a in agents]
    db.close()

    initial_state = {
        "messages": [HumanMessage(content=user_msg)],
        "active_workers": active_workers,
        "current_agent": None,
        "target_agent_to_delete": None,
        "consensus_votes": [],
        "consensus_result": None
    }

    await orchestrator.ainvoke(initial_state)
    return {"status": "processing"}

# --- Test Broadcast ---
@app.post("/test-broadcast")
async def test_broadcast(msg: dict):
    await manager.broadcast(msg)
    return {"status": "sent"}

# --- LLM Model Management ---
@app.get("/api/llm/models")
async def get_llm_models():
    models = []
    # Fetch Ollama models
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.OLLAMA_API_BASE}/api/tags")
            data = response.json()
            models.extend([f"ollama/{m['name']}" for m in data.get("models", [])])
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")

    # Add popular NVIDIA NIM models
    models.extend([
        "nvidia_nim/meta/llama-3.1-8b-instruct",
        "nvidia_nim/meta/llama-3.1-70b-instruct",
        "nvidia_nim/nvidia/llama-3.1-nemotron-70b-instruct",
        "nvidia_nim/mistralai/mixtral-8x7b-instruct-v0.1",
        "nvidia_nim/google/gemma-2-9b-it",
        "nvidia_nim/google/gemma-2-27b-it"
    ])
    return models

@app.get("/api/llm/current")
def get_current_model():
    return {"model": ModelFactory.get_current_model()}

@app.post("/api/llm/current")
def set_current_model(payload: dict = Body(...)):
    model_name = payload.get("model")
    if model_name:
        ModelFactory.set_current_model(model_name)
        return {"status": "updated", "model": model_name}
    return {"error": "No model name provided"}

@app.get("/api/llm/config")
def get_llm_config():
    return {
        "ollama_api_base": settings.OLLAMA_API_BASE,
        "nvidia_api_base": settings.NVIDIA_API_BASE,
        "has_nvidia_key": bool(settings.NVIDIA_API_KEY)
    }

@app.post("/api/llm/config")
def update_llm_config(payload: dict = Body(...)):
    if "ollama_api_base" in payload:
        settings.OLLAMA_API_BASE = payload["ollama_api_base"]
    if "nvidia_api_base" in payload:
        settings.NVIDIA_API_BASE = payload["nvidia_api_base"]
    if "nvidia_api_key" in payload:
        settings.NVIDIA_API_KEY = payload["nvidia_api_key"]
    return {"status": "updated"}
