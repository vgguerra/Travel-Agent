import re

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from src.agents.BaseAgent import BaseAgent
from src.agents.state.AgentState import AgentState


PARALLEL_AGENTS = [
    "weather_agent",
    "tourism_agent",
    "transport_agent",
    "accomodation_agent",
]

# Match a message that is only a greeting/social pleasantry — no trip data
# possible to extract, so we skip the manager LLM call entirely.
GREETING_PATTERN = re.compile(
    r"^\s*("
    r"ol[aá]+|oi+|hey+|hi+|hello+|"
    r"bom\s*dia|boa\s*tarde|boa\s*noite|"
    r"tudo\s*be[mn]|tudo\s*bom|"
    r"e\s*a[íi]|salve|opa|"
    r"obrigad[oa]|valeu|"
    r"tchau|at[eé]\s*logo"
    r")[\s!?.,]*$",
    re.IGNORECASE,
)


class Graph:

    def __init__(self, agents: dict[str, BaseAgent], tools: dict):
        self.agents = agents
        self.tools = tools

    @staticmethod
    def _entry_route(state: AgentState):
        """Skip the manager extraction LLM call for trivial greetings."""
        msgs = state.get("messages") or []
        last_human = next(
            (m.content for m in reversed(msgs) if isinstance(m, HumanMessage)),
            None,
        )
        if isinstance(last_human, str) and GREETING_PATTERN.match(last_human):
            return "conversational_agent"
        return "manager_agent"

    @staticmethod
    def _manager_route(state: AgentState):
        required_fields = [
            state.get("departure_city"),
            state.get("destination_city"),
            state.get("departure_date"),
            state.get("return_date"),
            state.get("adults"),
            state.get("trip_type"),
            state.get("rooms"),
        ]

        # Required data not yet collected — let conversational greet / ask.
        if any(v is None for v in required_fields):
            return "conversational_agent"

        results = [
            state.get("weather"),
            state.get("tourism"),
            state.get("transport"),
            state.get("accommodation"),
        ]

        # Plan already computed — go straight to the conversational reply.
        if any(v is not None for v in results):
            return "conversational_agent"

        # Required data present, no plan yet — fan out to the 4 agents.
        return PARALLEL_AGENTS

    def build_graph(self):
        builder = StateGraph(AgentState)

        for name, agent in self.agents.items():
            builder.add_node(name, agent.call)

        builder.set_conditional_entry_point(self._entry_route)
        builder.add_conditional_edges("manager_agent", self._manager_route)

        for agent_name in PARALLEL_AGENTS:
            builder.add_edge(agent_name, "conversational_agent")

        builder.add_edge("conversational_agent", "__end__")

        memory = MemorySaver()
        return builder.compile(checkpointer=memory)
