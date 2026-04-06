from pydantic_settings import SettingsConfigDict
from pattern_agentic_settings import PABaseSettings


class Settings(PABaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGNT_",
        extra="ignore",  # allow other AGNT_* vars (e.g., SLIM) without failing validation
    )
    openrouter_api_key: str
    mcp_json_path: str
    llm_model: str
    slim_local_name: str | None = None
    slim_endpoint: str | None = None
    slim_auth_secret: str | None = None
    system_prompt: str | None = None
    enable_legacy_handler: bool = False


settings = Settings.load('pa_sample_agent')
