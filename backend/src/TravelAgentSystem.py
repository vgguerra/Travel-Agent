import datetime
import uuid

from langchain_core.messages import HumanMessage

from src.agents.BaseAgent import BaseAgent
from src.graph.Graph import Graph


class TravelAgentSystem:

    def __init__(self, agents: dict[str, BaseAgent], tools):
        self.agents = agents
        self.tools = tools
        self.thread = str(uuid.uuid4())

    def _get_config(self):
        return {
            "configurable": {
                "thread_id": self.thread,
            },
        }

    def build_graph(self):
        graph = Graph(agents=self.agents, tools=self.tools)
        return graph.build_graph()

    def cli_mode(self):
        config = self._get_config()
        assistant = self.build_graph()

        while True:
            user_input = input("Você: ")
            if user_input.lower() in ["sair", "exit"]:
                print("TravelAgent: Até logo!")
                break

            state_input = {
                "messages": [HumanMessage(content=user_input)],
                "today": str(datetime.date.today()),
            }

            response = assistant.invoke(state_input, config=config)
            assistant_reply = response["messages"][-1]
            print("TravelAgent:", assistant_reply.content)
