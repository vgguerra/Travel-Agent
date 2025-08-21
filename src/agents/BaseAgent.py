from abc import abstractmethod, ABC

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class BaseAgent(ABC):

    """
    Abstract class that contains all of an Agent will be needed
    """

    def __init__(self, llm=None, tools=None):
        self.prompt = None
        self.llm = llm
        self.tools = tools

    def set_prompt(self, path: str):

        with open(path, "r", encoding="utf-8") as f:
            instructions = f.read()
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", instructions),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @abstractmethod
    def run(self, state):
        """
        Method that runs the agent. This method should be overridden.
        """
        pass