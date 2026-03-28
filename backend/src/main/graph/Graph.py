from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.main.agents.BaseAgent import BaseAgent
from src.main.agents.state.AgentState import AgentState


class Graph:

    def __init__(self, agents: dict[str, BaseAgent], tools: dict):
        self.agents = agents
        self.tools = tools

    @staticmethod
    def _manager_condition(state: AgentState):

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
            return "conversational_agent"

        return "ready"

    @staticmethod
    def _tourism_condition(state: AgentState):
        for msg in state["messages"]:
            # só processa mensagens do tipo AIMessage
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for call in msg.tool_calls:
                    if call["name"] == "getTourismIdeas":
                        return "tourism_tools"
        return "manager_agent"

    @staticmethod
    def _weather_condition(state: AgentState):
        for msg in state["messages"]:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for call in msg.tool_calls:
                    if call["name"] == "getWeather":
                        return "weather_tools"
        return "manager_agent"

    def build_graph(self):

        builder = StateGraph(AgentState)

        # Agents nodes
        for name, agent in self.agents.items():
            builder.add_node(name, agent.call)

        # Auxiliary node
        def ready_dispatcher(state: AgentState):
            return state
        builder.add_node("ready_dispatcher",ready_dispatcher)

        # Tools nodes
        builder.add_node("tourism_tools",ToolNode(self.tools["tourism"]))
        builder.add_node("weather_tools",ToolNode(self.tools["weather"]))

        # Edges logic

        builder.set_entry_point("manager_agent")
        builder.add_conditional_edges("manager_agent",self._manager_condition,{
            "end": "__end__",
            "conversational_agent": "conversational_agent",
            "ready": "ready_dispatcher",
        })

        # builder.add_edge("ready_dispatcher","tourism_agent")
        # builder.add_edge("ready_dispatcher", "weather_agent")

        # Weather logic
        builder.add_conditional_edges("weather_agent",self._weather_condition,{
            "weather_tools": "weather_tools",
            "manager_agent": "manager_agent",
        })
        builder.add_edge("weather_tools","weather_agent")

        # Tourism Logic
        builder.add_conditional_edges("tourism_agent", self._tourism_condition,{
            "tourism_tools": "tourism_tools",
            "manager_agent": "manager_agent"
        })
        builder.add_edge("tourism_tools", "tourism_agent")

        # builder.set_entry_point("manager_agent")
        #
        # builder.add_conditional_edges("manager_agent", self._manager_condition, {
        #     "end": "__end__",
        #     "ready": {
        #         "tourism_agent",
        #         "weather_agent",
        #     },
        # })
        #
        # Weather logic
        # builder.add_conditional_edges("weather_agent",self._weather_condition,{
        #     "weather_tools": "weather_tools",
        #     "manager_agent": "manager_agent",
        # })
        # builder.add_edge("weather_tools","weather_agent")
        #
        # # Tourism Logic
        # builder.add_conditional_edges("tourism_agent", self._tourism_condition,{
        #     "tourism_tools": "tourism_tools",
        #     "manager_agent": "manager_agent"
        # })
        # builder.add_edge("tourism_tools", "tourism_agent")




        # builder.set_entry_point("tourism_agent")
        # builder.add_conditional_edges("tourism_agent",tools_condition)
        # builder.add_edge("tools","tourism_agent")

        # builder.set_entry_point("weather_agent")
        # builder.add_conditional_edges("weather_agent", tools_condition)
        # builder.add_edge("tools", "weather_agent")

        # builder.set_entry_point("transport_agent")
        # builder.add_conditional_edges("transport_agent", tools_condition)
        # builder.add_edge("tools", "transport_agent")

        # builder.set_entry_point("accomodation_agent")
        # builder.add_conditional_edges("accomodation_agent", tools_condition)
        # builder.add_edge("tools","accomodation_agent")

        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)

        return graph