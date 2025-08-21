from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.agents.BaseAgent import BaseAgent
from src.agents.state.AgentState import AgentState


class Graph:

    def __init__(self, agents: dict[str, BaseAgent], tools):
        self.agents = agents
        self.tools = tools

    def build_graph(self):

        builder = StateGraph(AgentState)

        for name, agent in self.agents.items():
            builder.add_node(name, agent.run)

        builder.add_node("tools",ToolNode(self.tools))

        builder.set_entry_point("weather_agent")
        builder.add_conditional_edges("weather_agent", tools_condition)

        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)

        return graph
