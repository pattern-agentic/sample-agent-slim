import json
import logging
import os

import json
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
import langchain.agents
from .config import Settings
from .agent import SampleAgent

logger = logging.getLogger(__name__)


class AgentBuilder:
    def _load_mcp_config(self, mcp_json_path: str):
        if mcp_json_path:
            try:
                with open(mcp_json_path, 'r') as mcp_file:
                    mcp_json_str = mcp_file.read()
                    return json.loads(mcp_json_str)
            except Exception as exc:
                logger.warning(f"Could not read mcp conf at path {mcp_json_path}: {exc}", exc_info=True)

        logger.info("mcp_json_path is empty, no MCP tools will be used")
        return None

    async def create(self, settings: Settings) -> SampleAgent:
        mcp_conf = self._load_mcp_config(settings.mcp_json_path)
        mcp_client = MultiServerMCPClient(mcp_conf)

        tools = await mcp_client.get_tools()
        impl = langchain.agents.create_agent(
            ChatOpenAI(
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                model=settings.llm_model
            ),
            tools,
        )

        return SampleAgent(impl)


agent_builder = AgentBuilder()
