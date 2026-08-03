from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from nodes import SpecializedAgents

class MultiAgentBuilder:
    """
    Assembles node linkage and compiles asynchronous communication graph network.
    """
    @staticmethod
    def build_graph(agents: SpecializedAgents):
        workflow = StateGraph(AgentState)

        workflow.add_node("MediaOptimizer", agents.media_optimization_agent_node)
        workflow.add_node("ValidationAgent", agents.validation_agent_node)
        workflow.add_node("RAGVerifier", agents.rag_verifier_node)
        workflow.add_node("PrescriptionAgent", agents.prescription_agent_node)
        workflow.add_node("ErrorFallBack", agents.error_fallback_node)

        #Execution topology path
        workflow.set_entry_point("MediaOptimizer")
        workflow.add_edge("MediaOptimizer", "ValidationAgent")

        workflow.add_conditional_edges("ValidationAgent",
                                       agents.conditional_router,
                                       {
                                           "rag_node": "RAGVerifier",
                                           "error_node": "ErrorFallBack",
                                        }
                                       )
        # Add state transactions
        workflow.add_edge("RAGVerifier", "PrescriptionAgent")
        workflow.add_edge("PrescriptionAgent", END)
        workflow.add_edge("ErrorFallBack", END)

        # Memory checkpoint to allows cross-node state storage
        checkpointer = MemorySaver()
        return workflow.compile(checkpointer = checkpointer)

