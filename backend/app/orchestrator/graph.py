from langgraph.graph import StateGraph, END
from app.orchestrator.state import AgentState
from app.orchestrator.nodes import manager_node, worker_node, consensus_node

def route_from_manager(state: AgentState):
    """
    Decides the next node based on the state modified by ManagerNode.
    """
    if state.get("target_agent_to_delete"):
        return "consensus_node"
    elif state.get("current_agent"):
        return "worker_node"
    return END

def build_graph() -> StateGraph:
    """
    Constructs the LangGraph orchestration state machine.
    """
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("manager_node", manager_node)
    workflow.add_node("worker_node", worker_node)
    workflow.add_node("consensus_node", consensus_node)
    
    # Define Edges
    workflow.set_entry_point("manager_node")
    
    workflow.add_conditional_edges(
        "manager_node",
        route_from_manager,
        {
            "worker_node": "worker_node",
            "consensus_node": "consensus_node",
            END: END
        }
    )
    
    # Both worker and consensus nodes end the current cycle
    workflow.add_edge("worker_node", END)
    workflow.add_edge("consensus_node", END)
    
    # Compile the graph
    # Checkpointer can be passed here to persist state if needed
    app = workflow.compile()
    return app

# The compiled orchestrator app
orchestrator = build_graph()
