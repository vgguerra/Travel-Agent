from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(dict):
    """
    Class that represents a state of the agents.
    """
    messages: Annotated[list[AnyMessage], add_messages]