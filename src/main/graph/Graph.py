from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.main.agents.BaseAgent import BaseAgent
from src.main.agents.state.AgentState import AgentState


class Graph:

    def __init__(self, agents: dict[str, BaseAgent], tools: list):
        self.agents = agents
        self.tools = tools


    @staticmethod
    def _check_required_fields(state: AgentState):
        required_fields = [
            state["departure_city"],
            state["destination_city"],
            state["departure_date"],
            state["return_date"],
            state["adults"],
            state["trip_type"],
            state["rooms"],
        ]

        required_fields2 = [
            state["weather"],
            state["tourism"],
            state["transport"],
            state["accommodation"]
        ]

        if any(v is None for v in required_fields):
            return "end"

        if any(v is not None for v in required_fields2):
            return "end"

        return "ready"

    def build_graph(self):

        builder = StateGraph(AgentState)

        for name, agent in self.agents.items():
            builder.add_node(name, agent.call)

        builder.add_node("tools",ToolNode(self.tools))

        builder.set_entry_point("manager_agent")

        builder.add_conditional_edges(
            "manager_agent",
            self._check_required_fields,
            {
                "end": "__end__",
                "ready": "tourism_agent",
            },
        )

        builder.add_edge("tourism_agent", "accomodation_agent")
        builder.add_edge("accomodation_agent", "transport_agent")
        builder.add_edge("transport_agent", "weather_agent")
        builder.add_edge("weather_agent", "manager_agent")

        # builder.set_entry_point("tourism_agent")
        # builder.add_conditional_edges("tourism_agent", tools_condition)
        # builder.add_edge("tools", "tourism_agent")

        # builder.set_entry_point("transport_agent")
        # builder.add_conditional_edges("transport_agent", tools_condition)
        # builder.add_edge("tools", "transport_agent")

        # builder.set_entry_point("accomodation_agent")
        # builder.add_conditional_edges("accomodation_agent", tools_condition)
        # builder.add_edge("tools","accomodation_agent")

        # builder.set_entry_point("weather_agent")
        # builder.add_conditional_edges("weather_agent", tools_condition)
        # builder.add_edge("tools", "weather_agent")

        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)

        return graph
