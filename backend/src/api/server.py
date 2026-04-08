"""
FastAPI server for the Travel Agent multi-agent system.
Started automatically by App.py:  uv run python -m src.App
Or directly:                       uv run uvicorn src.api.server:app --reload --port 8000
"""

import datetime
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from src.App import App
from src.TravelAgentSystem import TravelAgentSystem
from src.api.auth import get_current_user
from src.db import chat_service, profile_service
from src.db.migrate import run_migrations

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
    adults: Optional[int] = None
    trip_type: Optional[str] = None
    rooms: Optional[int] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    state: TravelState


class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str


class SessionMessagesResponse(BaseModel):
    session_id: str
    title: str
    messages: list[dict]


class UpdateTitleRequest(BaseModel):
    title: str


class CheckUsernameRequest(BaseModel):
    username: str


class ResolveUsernameRequest(BaseModel):
    username: str


# ---------------------------------------------------------------------------
# In-memory session store (graph instances)
# ---------------------------------------------------------------------------

_INITIAL_STATE = {
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


class SessionStore:
    """Keeps one compiled graph + config per session_id."""

    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def get_or_create(self, session_id: str, agents, tools) -> tuple[tuple, bool]:
        is_new = session_id not in self._sessions
        if is_new:
            system = TravelAgentSystem(agents, tools)
            system.thread = session_id
            graph = system.build_graph()
            self._sessions[session_id] = {
                "graph": graph,
                "config": system._get_config(),
            }
        entry = self._sessions[session_id]
        return (entry["graph"], entry["config"]), is_new

    def remove(self, session_id: str):
        self._sessions.pop(session_id, None)


sessions = SessionStore()
_agents = None
_tools = None


# ---------------------------------------------------------------------------
# App lifespan — build agents once at startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _agents, _tools
    run_migrations()
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
# Routes — health (public)
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()}


# ---------------------------------------------------------------------------
# Routes — auth helpers (public, used before login)
# ---------------------------------------------------------------------------

@app.post("/api/auth/check-username")
async def check_username(req: CheckUsernameRequest):
    exists = profile_service.username_exists(req.username)
    return {"exists": exists}


@app.post("/api/auth/resolve-username")
async def resolve_username(req: ResolveUsernameRequest):
    email = profile_service.get_email_by_username(req.username)
    if not email:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return {"email": email}


# ---------------------------------------------------------------------------
# Routes — chat (authenticated)
# ---------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, user_id: str = Depends(get_current_user)):
    # Resolve or create DB session
    if req.session_id:
        db_session = chat_service.get_session(req.session_id, user_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Sessao nao encontrada")
        session_id = req.session_id
    else:
        db_session = chat_service.create_session(user_id)
        session_id = db_session["session_id"]

    # Persist user message
    chat_service.add_message(session_id, "user", req.message)

    try:
        (graph, config), is_new = sessions.get_or_create(session_id, _agents, _tools)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialise session: {e}")

    state_input = {
        "messages": [HumanMessage(content=req.message)],
        "today": str(datetime.date.today()),
    }
    if is_new:
        state_input.update(_INITIAL_STATE)

    try:
        result = graph.invoke(state_input, config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    reply = result["messages"][-1].content

    # Persist assistant reply
    chat_service.add_message(session_id, "assistant", reply)

    # Auto-title on first exchange
    if not req.session_id:
        title = req.message[:80]
        chat_service.update_session_title(session_id, user_id, title)

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


# ---------------------------------------------------------------------------
# Routes — sessions (authenticated)
# ---------------------------------------------------------------------------

@app.get("/api/sessions", response_model=list[SessionResponse])
async def list_sessions(user_id: str = Depends(get_current_user)):
    rows = chat_service.list_sessions(user_id)
    return [
        SessionResponse(
            session_id=str(r["session_id"]),
            title=r["title"],
            created_at=r["created_at"].isoformat(),
            updated_at=r["updated_at"].isoformat(),
        )
        for r in rows
    ]


@app.get("/api/sessions/{session_id}", response_model=SessionMessagesResponse)
async def get_session_messages(session_id: str, user_id: str = Depends(get_current_user)):
    db_session = chat_service.get_session(session_id, user_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    messages = chat_service.get_messages(session_id)
    return SessionMessagesResponse(
        session_id=str(db_session["session_id"]),
        title=db_session["title"],
        messages=[
            {
                "id": str(m["message_id"]),
                "role": m["role"],
                "content": m["content"],
                "timestamp": m["created_at"].isoformat(),
            }
            for m in messages
        ],
    )


@app.patch("/api/sessions/{session_id}")
async def update_session(
    session_id: str,
    req: UpdateTitleRequest,
    user_id: str = Depends(get_current_user),
):
    updated = chat_service.update_session_title(session_id, user_id, req.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")
    return {"success": True}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, user_id: str = Depends(get_current_user)):
    deleted = chat_service.delete_session(session_id, user_id)
    sessions.remove(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")
    return {"success": True}
