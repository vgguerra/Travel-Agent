from src.main.agents.BaseAgent import BaseAgent
from src.main.agents.state.AgentState import AgentState


class TransportAgent(BaseAgent):

    def call(self, state: AgentState):

        try:
            chain = self.llm.bind_tools(self.tools)

            if self.prompt is not None:
                result = (self.prompt | chain).invoke(state)
            else:
                raise ValueError("Prompt was not given")

            return {
                "messages": result
            }

        except Exception as e:
            raise ValueError(f"ERROR: {e}")