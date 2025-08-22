from src.travel_system.agents.BaseAgent import BaseAgent
from src.travel_system.agents.state.AgentState import AgentState


class WeatherAgent(BaseAgent):
    """
    Class that represents a Weather Agent that uses the Weather API.
    """

    def  run(self, state: AgentState):
        try:
            chain = self.llm.bind_tools(self.tools)
        except Exception as e:
            raise print(f"ERROR: {e}")

        if self.prompt is not None:
            result = (self.prompt | chain).invoke(state)
        else:
            raise print("No prompt given")



        return {
            "messages": result,
        }