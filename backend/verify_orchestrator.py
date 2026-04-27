import asyncio
from langchain_core.messages import HumanMessage
from app.orchestrator.graph import orchestrator
from app.core.config import settings
from app.core.llm import ModelFactory

async def test_worker_routing():
    print("--- Test: Normal Worker Routing ---")
    
    state = {
        "messages": [HumanMessage(content="Hello, can you help me write a Python script?")],
        "current_agent": None,
        "active_workers": [
            {"id": "agent_1", "name": "Agent 1"}
        ],
        "target_agent_to_delete": None,
        "consensus_votes": [],
        "consensus_result": None
    }
    
    print(f"Initial Messages: {state['messages'][0].content}")
    # Run the graph
    try:
        final_state = await orchestrator.ainvoke(state)
        print(f"Routed to Agent: {final_state.get('current_agent')}")
        print(f"Response: {final_state['messages'][-1].content}")
    except Exception as e:
        print(f"Error during graph execution: {e}")

async def test_consensus_voting():
    print("\n--- Test: Consensus Protocol ---")
    
    state = {
        "messages": [HumanMessage(content="Please delete agent Grumpy_Bob.")],
        "current_agent": None,
        "active_workers": [
            {"id": "agent_1", "name": "Agent 1"},
            {"id": "agent_2", "name": "Agent 2"}
        ],
        "target_agent_to_delete": None, # Should be extracted by manager_node
        "consensus_votes": [],
        "consensus_result": None
    }
    
    try:
        final_state = await orchestrator.ainvoke(state)
        print(f"Target to delete: {final_state.get('target_agent_to_delete')}")
        print(f"Consensus Result: {final_state.get('consensus_result')}")
        print("Votes:")
        for vote in final_state.get('consensus_votes', []):
            print(f" - {vote['agent_id']}: {vote['vote']} ({vote['reason']})")
        print(f"Output Message:\n{final_state['messages'][-1].content}")
    except Exception as e:
        print(f"Error during graph execution: {e}")

async def main():
    ModelFactory.setup()
    await test_worker_routing()
    await test_consensus_voting()

if __name__ == "__main__":
    asyncio.run(main())
