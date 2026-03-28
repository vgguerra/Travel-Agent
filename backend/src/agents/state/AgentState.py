from datetime import datetime
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):

    messages: Annotated[list[AnyMessage], add_messages]
    today: str | None
    weather: str | None
    tourism: str | None
    transport: str | None
    accommodation: str | None

    departure_city: str | None
    destination_city: str | None
    departure_date: str | None
    return_date: str | None
    adults: str | None
    trip_type: str | None
    rooms: int | None