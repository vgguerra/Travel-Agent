from src.agents.BaseAgent import BaseAgent
from src.agents.state.AgentState import AgentState


class WeatherAgent(BaseAgent):
    """
    Class that represents a Weather Agent that uses the Weather API.

    The forecast tool only covers the next 5 days. Trip planning typically
    happens weeks or months in advance, so we let the prompt decide whether
    to call the tool (near-future trips) or describe seasonal climate from
    knowledge (everything else).
    """

    force_tool_use = False

    def call(self, state: AgentState):
        return self._invoke_with_tools(state, "weather")
