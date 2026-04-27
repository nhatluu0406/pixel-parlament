# 🎭 PROJECT: PIXEL-ART AGENTIC GOVERNANCE SYSTEM

## 1. Technical Stack (The Engine)
- **Backend**: Python 3.14+ (managed by `uv`).
- **Orchestration**: LangGraph (State Machine) for complex workflows.
- **LLM Gateway**: LiteLLM (unified API for local Ollama).
- **Primary Model (Local)**: `ollama/qwen2.5:1.5b` (used for both Manager and Workers).
- **Communication**: FastAPI + WebSockets for real-time live logging.
- **Frontend**: Next.js 15, Tailwind CSS, Framer Motion (for Pixel Animations), NES.css (UI Style). Supported language: Vietnamese (Be Vietnam Pro font).

## 2. Manager-Worker Architecture
- **Manager Agent (The Orchestrator)**:
    - Analyzes user requests using `The Director` persona.
    - Decomposes tasks into sub-tasks.
    - Dispatches tasks to Workers based on their Skills and Personality (Soul).
- **Worker Agents (The Executors)**:
    - Specialized in specific tasks (File Manager, Web Search, etc.).
    - Managed and commanded by the Manager.

## 3. Persistence & State Management
- **Database**: SQLite (managed by SQLAlchemy).
- **Agent Status**: Persistent `status` field in DB (`idle`, `working`, `thinking`, `voting`).
- **State Restoration**: Frontend fetches current status on mount to ensure continuity across page navigation.

## 4. The Soul System (Personality Engine)
- **Storage**: Each agent has a dedicated folder `/backend/souls/{agent_id}/`.
- **Primary File**: `soul.md` - Markdown file containing:
    - `Identity`: Role, tone of voice, and background.
    - `Traits`: Sliders/Values (Efficiency, Creativity, Grumpiness).
- **Dynamic Injection**: `soul.md` content is prepended to the System Prompt of every LLM call.

## 5. Skill Registry (Tool-Calling)
- **Discovery**: Automatic function discovery via `@tool` decorator.
- **Available Skills**:
    - `web_search`: Retrieve real-time information.
    - `file_manager`: Read/Write operations in `/workspace`.
- **Assignment**: Users assign skills to Agents via the Admin UI.

## 6. Governance & Consensus Protocol (The Parliament)
- **Agent Deletion Rule**: An Agent can ONLY be deleted if there is 100% consensus among ALL current Agents.
- **Voting Process**:
    1. **Trigger**: User requests deletion via UI.
    2. **Debate**: Manager opens a `VotingSession` node in LangGraph.
    3. **Vote**: Agents generate a JSON response based on their souls.

## 7. Pixel-Art UI Specifications
- **Main View (The Office)**:
    - Background: `office_bg.png` (2D Pixel Office).
    - Agent Sprites: Sliced from `office_sprites.png` (4x4 grid: Front, Back, Right, Left frames).
    - Animations: CSS `object-position` transitions via `framer-motion`.
- **Side Panel (The Terminal)**:
    - Real-time scrolling logs (NES.css).
    - Detailed Routing: Manager broadcasts specific assignment details (e.g., "Giao việc cho [Name]: [Task]").
- **Admin Dash**: Create Agents, manage LLM model selection (Ollama), and configure model parameters.

## 8. Execution Flow
- Use `uv` for Python dependencies.
- WebSocket schema: `{"agent_id": "str", "action": "str", "message": "str", "sprite_state": "str"}`.