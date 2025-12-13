from pydantic import field_validator, model_validator
from pydantic_settings import SettingsConfigDict
from pattern_agentic_settings import PABaseSettings


class Settings(PABaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGNT_", extra="ignore")

    # LLM provider keys (set at least one)
    openrouter_api_key: str | None = None
    google_api_key: str | None = None
    llm_model: str

    mcp_json_path: str

    # SLIM configuration
    slim_local_name: str
    slim_endpoint: str
    slim_auth_secret: str

    @field_validator("openrouter_api_key", "google_api_key", mode="before")
    @classmethod
    def _empty_string_to_none(cls, value: str | None):
        # Treat blank env vars as unset
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def _validate_provider(self):
        if not (self.google_api_key or self.openrouter_api_key):
            raise ValueError(
                "Set AGNT_GOOGLE_API_KEY or AGNT_OPENROUTER_API_KEY to choose an LLM provider."
            )
        return self


settings = Settings.load("pa_sample_agent")
