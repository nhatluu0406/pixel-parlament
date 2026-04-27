from typing import Annotated, Sequence, TypedDict, Optional, List, Dict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Represents the state of our LangGraph orchestrator.
    """
    # Messages in the current conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # The currently active worker handling the request
    current_agent: Optional[str]
    
    # List of available agents (for routing/consensus)
    active_workers: List[Dict[str, str]]
    
    # Used during consensus protocol to track votes
    target_agent_to_delete: Optional[str]
    consensus_votes: List[Dict[str, str]] # e.g., [{"agent_id": "1", "vote": "YES", "reason": "..."}]
    consensus_result: Optional[str] # "APPROVED" or "REJECTED"
