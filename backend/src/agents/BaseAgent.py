import logging
from abc import ABC

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import ToolNode

logger = logging.getLogger(__name__)


def _content_to_text(content) -> str:
    """Flatten LangChain message content into a plain string.

    Newer providers (Gemini 2.5, Anthropic thinking) return content as a list
    of dicts like [{"type": "text", "text": "..."}, {"type": "thinking", ...}].
    We keep only the user-visible text parts.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") in (None, "text") and "text" in item:
                    parts.append(str(item["text"]))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts).strip()
    return str(content).strip()


class BaseAgent(ABC):

    # Whether to force the model to invoke its tool on the first LLM call.
    # Subclasses can set this to False when the tool is only useful in some
    # situations and the prompt should decide.
    force_tool_use: bool = True

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

    def _bind_chain(self):
        """Bind tools, optionally forcing the model to call the (single) tool.

        Each agent has exactly one tool, so when force_tool_use is True we set
        tool_choice by name to avoid models skipping the tool and answering
        from memory. Agents whose tool is only sometimes relevant override
        force_tool_use = False and let the prompt drive the decision.
        """
        if not self.tools:
            return self.llm

        if not self.force_tool_use:
            return self.llm.bind_tools(self.tools)

        tool_name = getattr(self.tools[0], "name", None)
        if tool_name:
            try:
                return self.llm.bind_tools(self.tools, tool_choice=tool_name)
            except (TypeError, NotImplementedError):
                pass
        return self.llm.bind_tools(self.tools)

    def _invoke_with_tools(self, state, state_key: str) -> dict:
        """Run the LLM, execute any tool calls inline, then re-invoke for a final reply.

        Kept inside a single node so the agents can be fanned out in parallel by
        the graph without round-tripping through shared tool nodes. Errors are
        caught so one failing branch does not abort the whole fan-out.
        """
        if self.prompt is None:
            raise ValueError("Prompt not set")

        try:
            chain = self._bind_chain()
            # Only expose the user's latest HumanMessage to the agent prompt.
            # Other AI messages in state (e.g. Manager's structured extraction)
            # would contaminate the prompt and cause format mimicry.
            last_human = next(
                (m for m in reversed(state.get("messages") or []) if isinstance(m, HumanMessage)),
                None,
            )
            clean_state = dict(state)
            clean_state["messages"] = [last_human] if last_human else []
            prompt_messages = self.prompt.format_messages(**clean_state)
            first = chain.invoke(prompt_messages)
            new_messages = [first]
            final = first

            if self.tools and getattr(first, "tool_calls", None):
                tool_output = ToolNode(self.tools).invoke({"messages": [first]})
                tool_messages = tool_output["messages"]
                new_messages.extend(tool_messages)
                # Second invocation interprets the tool result. Drop tool_choice
                # forcing here so the model is free to summarize instead of
                # re-calling the tool.
                free_chain = self.llm.bind_tools(self.tools)
                final = free_chain.invoke(prompt_messages + new_messages)
                new_messages.append(final)
            elif self.tools:
                logger.warning(
                    "Agent %s did not emit a tool call; returning raw LLM output.",
                    state_key,
                )

            text = _content_to_text(final.content)
            return {"messages": new_messages, state_key: text or None}
        except Exception as exc:
            logger.exception("Agent %s failed: %s", state_key, exc)
            return {"messages": [], state_key: None}

    def call(self, state):
        """
        Method that runs the agent. This method should be overridden.
        """
        pass