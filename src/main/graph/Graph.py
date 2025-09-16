from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.main.agents.BaseAgent import BaseAgent
from src.main.agents.state.AgentState import AgentState


class Graph:

    def __init__(self, agents: dict[str, BaseAgent], tools: list):
        self.agents = agents
        self.tools = tools


    def build_graph(self):

        builder = StateGraph(AgentState)

        for name, agent in self.agents.items():
            builder.add_node(name, agent.call)

        builder.add_node("tools",ToolNode(self.tools))

        builder.set_entry_point("manager_agent")
        builder.set_finish_point("manager_agent")

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
