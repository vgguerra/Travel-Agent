from src.agents.BaseAgent import BaseAgent
from src.agents.state.AgentState import AgentState


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
            prompt = self.prompt.format(**state)
            result = chain.invoke(prompt)
        else:
            raise ValueError("No prompt given")



        return {
            "messages": result,
            "weather": result.content.strip()
        }