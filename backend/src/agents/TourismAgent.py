from src.agents.BaseAgent import BaseAgent
from src.agents.state.AgentState import AgentState


class TourismAgent(BaseAgent):

    def call(self, state: AgentState):

        try:
            chain = self.llm.bind_tools(self.tools)

            if self.prompt is not None:
                prompt = self.prompt.format_messages(**state)
                result = chain.invoke(prompt)
            else:
                raise ValueError("Prompt was not given")

            return {
                "messages": result,
                "tourism": result.content.strip()
            }

        except Exception as e:
            raise ValueError(f"ERROR: {e}")