import logging

logger = logging.getLogger(__name__)


class SampleAgent:

    def __init__(self, agent_impl):
        self.agent_impl = agent_impl

    async def ask(self, question: str):
        response = await self.agent_impl.ainvoke(
            {"messages": [{"role": "user", "content": question}]}
        )
        try:
            return response['messages'][-1].content
        except Exception as exc:
            logger.error(str(exc), exc_info=True)
            return str(response)
