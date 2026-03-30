from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from src.agents.BaseAgent import BaseAgent
from src.agents.state.AgentState import AgentState


class Graph:

    def __init__(self, agents: dict[str, BaseAgent], tools: dict):
        self.agents = agents
        self.tools = tools

    @staticmethod
    def _manager_condition(state: AgentState):
        required_fields = [
            state.get("departure_city"),
            state.get("destination_city"),
            state.get("departure_date"),
            state.get("return_date"),
            state.get("adults"),
            state.get("trip_type"),
            state.get("rooms"),
        ]

        results = [
            state.get("weather"),
            state.get("tourism"),
            state.get("transport"),
            state.get("accommodation"),
        ]

        if any(v is None for v in required_fields):
            return "end"

        if any(v is not None for v in results):
            return "conversational_agent"

        return "ready"

    @staticmethod
    def _has_tool_call(state: AgentState, tool_name: str) -> bool:
        """Check only the LAST message for a specific tool call."""
        last_msg = state["messages"][-1]
        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            return any(call["name"] == tool_name for call in last_msg.tool_calls)
        return False

    @staticmethod
    def _weather_condition(state: AgentState):
        if Graph._has_tool_call(state, "getWeather"):
            return "weather_tools"
        return "tourism_agent"

    @staticmethod
    def _tourism_condition(state: AgentState):
        if Graph._has_tool_call(state, "getTourismIdeas"):
            return "tourism_tools"
        return "manager_agent"

    def build_graph(self):
        builder = StateGraph(AgentState)

        for name, agent in self.agents.items():
            builder.add_node(name, agent.call)

        builder.add_node("tourism_tools", ToolNode(self.tools["tourism"]))
        builder.add_node("weather_tools", ToolNode(self.tools["weather"]))

        builder.set_entry_point("manager_agent")
        builder.add_conditional_edges("manager_agent", self._manager_condition, {
            "end": "__end__",
            "conversational_agent": "conversational_agent",
            "ready": "weather_agent",
        })

        builder.add_conditional_edges("weather_agent", self._weather_condition, {
            "weather_tools": "weather_tools",
            "tourism_agent": "tourism_agent",
        })
        builder.add_edge("weather_tools", "weather_agent")

        builder.add_conditional_edges("tourism_agent", self._tourism_condition, {
            "tourism_tools": "tourism_tools",
            "manager_agent": "manager_agent",
        })
        builder.add_edge("tourism_tools", "tourism_agent")

        builder.add_edge("conversational_agent", "__end__")

        memory = MemorySaver()
        return builder.compile(checkpointer=memory)
