# AGENTS.md

Notes for AI coding agents (Claude Code, Cursor, etc.) working on Travel-Agent.

## What this is

Multi-agent travel assistant. Seven specialized agents orchestrated by LangGraph, LLM running locally via Ollama. Backend FastAPI, frontend Next.js 16 + Supabase. Personal portfolio project, in active development.

See [README.md](./README.md) and [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) for the full picture.

## Stack

- Backend: Python 3.12 · FastAPI · LangGraph · langchain-ollama · Langfuse · psycopg2
- Frontend: Next.js 16 · TypeScript · Tailwind · Framer Motion · Supabase
- LLM: Ollama (qwen2.5:7b) by default
- Database / Auth: Supabase (PostgreSQL + RLS)

## Key paths

- `backend/src/agents/` — agent classes (Manager, Weather, Tourism, Transport, Accomodation, Budget, Conversational, Base)
- `backend/src/graph/Graph.py` — LangGraph StateGraph
- `backend/src/tools/` — `@tool` wrappers for external APIs
- `backend/src/api/` — FastAPI server + auth middleware
- `backend/src/db/` — chat persistence + profile services
- `frontend/src/app/` — Next.js pages
- `frontend/src/components/` — UI components
- `frontend/src/hooks/useChat.ts` — chat streaming hook
- `frontend/src/contexts/AuthContext.tsx` — Supabase Auth

## Commands

Backend:

```bash
cd backend
uv sync
uv run uvicorn src.api.server:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Ollama:

```bash
ollama pull qwen2.5:7b
ollama serve
```

## Conventions

- Commits: lowercase imperative, conventional style (`fix:`, `feat:`, `docs:`, `refactor:`)
- Do not include `Co-Authored-By` in commits
- Type hints everywhere in Python; strict TypeScript on the frontend
- Agents inherit from `BaseAgent`; tools use LangChain's `@tool` decorator
- All Supabase tables have RLS enabled — keep it that way when adding new tables
- New agents: create `MyAgent.py` in `agents/`, add prompt in `prompts/`, register in `App.build_agents()` and wire into `Graph.build_graph()`
- New tools: create wrapper in `tools/` and pass to the corresponding agent in `App.build_agents()`

## Don't

- Don't commit `.env` files
- Don't bypass the auth middleware in routes that should require login
- Don't break the StateGraph contract — agents read from and write to specific keys defined in the state
- Don't add a new external API call without timeout + error handling

## Frontend specifics

Next.js 16 has breaking changes vs earlier versions. See `frontend/AGENTS.md` for the rules that apply specifically to the frontend.

## Roadmap

See [docs/ROADMAP.md](./docs/ROADMAP.md). Short version: dynamic tool-use, persistent memory across sessions, agent evaluation harness, real-time tool-call UI, multi-provider LLM, public deploy.

## Skills (project conventions)

Reusable rules live under [.claude/skills/](./.claude/skills/). They are Claude Code SKILL.md files but the content is plain Markdown — any AI agent can read them as project guidelines.

| Skill | Read when | File |
|---|---|---|
| `conventional-commits` | Writing or reviewing a commit message | [.claude/skills/conventional-commits/SKILL.md](./.claude/skills/conventional-commits/SKILL.md) |
| `code-review` | Reviewing a PR or self-reviewing before opening one | [.claude/skills/code-review/SKILL.md](./.claude/skills/code-review/SKILL.md) |
| `writing-python-tests` | Adding or debugging Python tests | [.claude/skills/writing-python-tests/SKILL.md](./.claude/skills/writing-python-tests/SKILL.md) |

If a project rule in this file conflicts with a skill, this file wins.
