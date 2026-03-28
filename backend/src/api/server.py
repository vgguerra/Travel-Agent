"""
FastAPI server for the Travel Agent multi-agent system.
Started automatically by App.py:  uv run python -m src.App
Or directly:                       uv run uvicorn src.api.server:app --reload --port 8000
"""

import datetime
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from src.App import App
from src.TravelAgentSystem import TravelAgentSystem

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class TravelState(BaseModel):
    weather: Optional[str] = None
    tourism: Optional[str] = None
    transport: Optional[str] = None
    accommodation: Optional[str] = None
    departure_city: Optional[str] = None
    destination_city: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    adults: Optional[str] = None
    trip_type: Optional[str] = None
    rooms: Optional[int] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    state: TravelState


# ---------------------------------------------------------------------------
# In-memory session store
# ---------------------------------------------------------------------------

class SessionStore:
    """Keeps one compiled graph + config per session_id."""

    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def get_or_create(self, session_id: str, agents, tools) -> tuple:
        if session_id not in self._sessions:
            system = TravelAgentSystem(agents, tools)
            # Give each session its own thread for checkpointing
            system.thread = session_id
            graph = system.build_graph()
            self._sessions[session_id] = {
                "graph": graph,
                "config": system._get_config(),
            }
        entry = self._sessions[session_id]
        return entry["graph"], entry["config"]


sessions = SessionStore()
_agents = None
_tools = None


# ---------------------------------------------------------------------------
# App lifespan — build agents once at startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _agents, _tools
    _agents, _tools = App.build_agents()
    yield


app = FastAPI(
    title="Travel Agent API",
    description="Multi-agent travel planning assistant powered by a local LLM (Ollama)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    try:
        graph, config = sessions.get_or_create(session_id, _agents, _tools)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialise session: {e}")

    state_input = {
        "messages": [HumanMessage(content=req.message)],
        "today": str(datetime.date.today()),
        "weather": None,
        "tourism": None,
        "transport": None,
        "accommodation": None,
        "departure_city": None,
        "destination_city": None,
        "departure_date": None,
        "return_date": None,
        "adults": None,
        "trip_type": None,
        "rooms": None,
    }

    try:
        result = graph.invoke(state_input, config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    reply = result["messages"][-1].content

    travel_state = TravelState(
        weather=result.get("weather"),
        tourism=result.get("tourism"),
        transport=result.get("transport"),
        accommodation=result.get("accommodation"),
        departure_city=result.get("departure_city"),
        destination_city=result.get("destination_city"),
        departure_date=result.get("departure_date"),
        return_date=result.get("return_date"),
        adults=result.get("adults"),
        trip_type=result.get("trip_type"),
        rooms=result.get("rooms"),
    )

    return ChatResponse(session_id=session_id, reply=reply, state=travel_state)


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    sessions._sessions.pop(session_id, None)
    return {"deleted": session_id}
