import os
from pathlib import Path
from typing import Optional
from app.core.config import settings

class SoulManager:
    """
    Manages the soul.md files for agents, which dictate their personality and rules.
    """
    
    def __init__(self):
        self.souls_dir = Path(settings.SOULS_DIR)
        self.souls_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_agent_soul_dir(self, agent_id: str) -> Path:
        agent_dir = self.souls_dir / str(agent_id)
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir
        
    def _get_agent_soul_path(self, agent_id: str) -> Path:
        return self._get_agent_soul_dir(agent_id) / "soul.md"

    def create_or_update_soul(self, agent_id: str, content: str) -> None:
        """Writes the soul.md file for a specific agent."""
        soul_path = self._get_agent_soul_path(agent_id)
        with open(soul_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    def get_soul(self, agent_id: str) -> Optional[str]:
        """Reads the soul.md file for an agent. Returns None if it doesn't exist."""
        soul_path = self._get_agent_soul_path(agent_id)
        if not soul_path.exists():
            return None
        with open(soul_path, "r", encoding="utf-8") as f:
            return f.read()
            
    def generate_system_message(self, agent_id: str, base_system_message: str = "") -> str:
        """
        Injects the soul content into the system message.
        """
        soul_content = self.get_soul(agent_id)
        if not soul_content:
            return base_system_message
            
        return f"{soul_content}\n\n{base_system_message}".strip()
