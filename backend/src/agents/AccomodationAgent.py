from src.agents.BaseAgent import BaseAgent
from src.agents.state.AgentState import AgentState


class AccomodationAgent(BaseAgent):

    def call(self, state: AgentState):

        try:
            chain = self.llm.bind_tools(self.tools)
        except Exception as e:
            raise print(f"ERROR: {e}")

        if self.prompt is not None:
            prompt = self.prompt.format_messages(**state)
            result = chain.invoke(prompt)
        else:
            raise print("No prompt given")

        return {
            "messages": result,
            "accommodation": result.content.strip()
        }