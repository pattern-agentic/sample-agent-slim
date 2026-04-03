from pydantic_settings import SettingsConfigDict
from pattern_agentic_settings import PABaseSettings


class Settings(PABaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGNT_"
    )
    openrouter_api_key: str
    mcp_json_path: str
    llm_model: str


settings = Settings.load('pa_sample_agent')
