from datetime import datetime
from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(dict):

    messages: Annotated[list[AnyMessage], add_messages]
    today: str | None