from src.agents.BaseAgent import BaseAgent
from src.agents.state.AgentState import AgentState


class WeatherAgent(BaseAgent):
    """
    Class that represents a Weather Agent that uses the Weather API.
    """

    def  run(self, state: AgentState):

        try:
            chain = self.llm.bind_tools(self.tools,parallel_tool_calls=False)
        except Exception as e:
            raise print(f"ERROR: {e}")

        result = (self.prompt | chain).invoke(state)

        return result