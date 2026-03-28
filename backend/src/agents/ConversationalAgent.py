from src.agents.BaseAgent import BaseAgent


class ConversationalAgent(BaseAgent):

    def call(self, state):

        if self.prompt is not None:
            prompt = self.prompt.format(**state)
            result = self.llm.invoke(prompt)
        else:
            raise ValueError("No prompt given")

        return {
            "messages": result,
        }