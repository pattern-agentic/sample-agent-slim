from pydantic_settings import SettingsConfigDict
from pattern_agentic_settings import PABaseSettings


class Settings(PABaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGNT_"
    )
    openrouter_api_key: str
    mcp_json_path: str
    llm_model: str

    # SLIM configuration
    slim_local_name: str
    slim_endpoint: str
    slim_auth_secret: str


settings = Settings.load('pa_sample_agent')
