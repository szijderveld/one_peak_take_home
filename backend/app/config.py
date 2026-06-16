from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, loaded from environment / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Pulse Competitor Intelligence API
    pulse_api_key: str = ""
    pulse_base_url: str = "https://dev.onepeak.tech"

    # Anthropic
    anthropic_api_key: str = ""
    # Models chosen per use case (see plan): judgement work on Sonnet, the
    # mechanical batched blurbs on Haiku.
    narrative_model: str = "claude-sonnet-4-6"
    blurb_model: str = "claude-haiku-4-5"
    chat_model: str = "claude-sonnet-4-6"

    # A competitor counts as a "credible peer" (part of the space) above this
    # similarity score. Tunable; 0.6 matches the design's "60% similarity bar".
    similarity_threshold: float = 0.6

    @property
    def ai_enabled(self) -> bool:
        return bool(self.anthropic_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
