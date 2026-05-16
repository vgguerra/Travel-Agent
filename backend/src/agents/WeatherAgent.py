from src.agents.BaseAgent import BaseAgent
from src.agents.state.AgentState import AgentState


class WeatherAgent(BaseAgent):
    """
    Class that represents a Weather Agent that uses the Weather API.
    """

    def call(self, state: AgentState):
        return self._invoke_with_tools(state, "weather")
