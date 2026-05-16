from src.agents.BaseAgent import BaseAgent
from src.agents.state.AgentState import AgentState


class TransportAgent(BaseAgent):

    def call(self, state: AgentState):
        return self._invoke_with_tools(state, "transport")
