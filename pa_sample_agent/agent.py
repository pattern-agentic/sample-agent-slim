import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SampleAgent:

    def __init__(self, agent_impl):
        self.agent_impl = agent_impl

    async def ask(self, question: str, system_prompt: Optional[str]):
        messages = []
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}]

        messages.append({"role": "user", "content": question})
        response = await self.agent_impl.ainvoke(
            {"messages": messages}
        )
        try:
            return response['messages'][-1].content
        except Exception as exc:
            logger.error(str(exc), exc_info=True)
            return str(response)
