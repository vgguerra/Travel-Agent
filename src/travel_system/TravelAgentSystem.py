import datetime

from langchain_core.messages import HumanMessage

from src.travel_system.agents.BaseAgent import BaseAgent
from src.travel_system.graph.Graph import Graph
from langfuse.langchain import CallbackHandler
import uuid


class TravelAgentSystem:

    def __init__(self,agents: dict[str,BaseAgent],tools):
        self.agents = agents
        self.tools = tools
        self.thread = str(uuid.uuid4())
        self.langfuse_handler = CallbackHandler()

    def _get_config(self):
        return {
            "configurable": {
                "thread_id": self.thread,
            },
            "callbacks": [self.langfuse_handler],
        }

    def cli_mode(self):

        graph = Graph(agents=self.agents, tools=self.tools)
        config = self._get_config()
        assistant = graph.build_graph()

        while True:
            user_input = input("Você: ")
            if user_input.lower() in ["sair", "exit"]:
                print("HelperCHAT: Até logo!")
                break

            state_input = {
                "messages":[HumanMessage(content=user_input)],
                "today": str(datetime.date.today())
            }

            response = assistant.invoke(state_input, config=config)
            assistant_reply = response['messages'][-1]
            print("Assistant:", assistant_reply.content)