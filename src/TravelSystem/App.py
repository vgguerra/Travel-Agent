from langchain_core.messages import HumanMessage

from src.agents.BaseAgent import BaseAgent
from src.graph.Graph import Graph
from langfuse.langchain import CallbackHandler
import uuid
from dotenv import load_dotenv

load_dotenv()

class App:

    graph: Graph = None
    agents: dict[str,BaseAgent] = None
    tools : list = None
    langfuse_handler: CallbackHandler = None
    thread : str = None

    def __init__(self,agents: dict[str,BaseAgent],tools: list):
        self.agents = agents
        self.tools = tools
        self.langfuse_handler = CallbackHandler()
        self.thread = str(uuid.uuid4())

    def get_config(self):
        return {
            "configurable": {
                "thread_id": self.thread,
            },
            "callbacks": [self.langfuse_handler]
        }

    def cli_mode(self):
        self.graph = Graph(self.agents, self.tools)
        config = self.get_config()
        assistant = self.graph.build_graph()
        while True:
            user_input = input("Você: ")
            if user_input.lower() in ["sair", "exit"]:
                print("HelperCHAT: Até logo!")
                break
            response = assistant.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
            assistant_reply = response['messages'][-1]
            print("Assistant:", assistant_reply.content)