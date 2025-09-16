from src.main.agents.BaseAgent import BaseAgent
from src.main.agents.state.AgentState import AgentState


class AccomodationAgent(BaseAgent):

    def call(self, state: AgentState):

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
            "accommodation": result.content.strip()
        }