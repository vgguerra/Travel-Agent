from src.main.agents.BaseAgent import BaseAgent
from src.main.agents.state.AgentState import AgentState


class WeatherAgent(BaseAgent):
    """
    Class that represents a Weather Agent that uses the Weather API.
    """

    def  call(self, state: AgentState):
        try:
            chain = self.llm.bind_tools(self.tools)
        except Exception as e:
            raise ValueError(f"ERROR: {e}")

        if self.prompt is not None:
            result = (self.prompt | chain).invoke(state)
        else:
            raise ValueError("No prompt given")



        return {
            "messages": result,
        }