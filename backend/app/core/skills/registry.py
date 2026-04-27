from typing import List, Dict, Callable
from langchain_core.tools import BaseTool
from app.core.skills.tools import web_search, file_manager, code_interpreter

class SkillRegistry:
    """
    Central registry for mapping skill names to their tool implementations.
    """
    
    _tools: Dict[str, BaseTool] = {
        "web_search": web_search,
        "file_manager": file_manager,
        "code_interpreter": code_interpreter
    }
    
    @classmethod
    def get_tool(cls, skill_name: str) -> BaseTool:
        """Fetch a specific tool by name."""
        tool = cls._tools.get(skill_name)
        if not tool:
            raise ValueError(f"Skill '{skill_name}' not found in registry.")
        return tool
        
    @classmethod
    def get_tools_for_agent(cls, skill_names: List[str]) -> List[BaseTool]:
        """Fetch a list of tools based on skill names assigned to an agent."""
        tools = []
        for name in skill_names:
            try:
                tools.append(cls.get_tool(name))
            except ValueError as e:
                print(f"Warning: {e}")
        return tools

    @classmethod
    def get_all_tools(cls) -> List[BaseTool]:
        """Return all registered tools."""
        return list(cls._tools.values())
