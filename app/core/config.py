from dataclasses import dataclass
import os

import dotenv

dotenv.load_dotenv(dotenv_path=".env")


@dataclass(frozen=True)
class Settings:
    # Load settings from environment variables so the demo is easy to configure.
    database_path: str = os.getenv("DATABASE_PATH", "data/router.db")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    llm_api_key: str = os.getenv("OPEN_ROUTER_API_KEY", os.getenv("LLM_API_KEY", ""))
    llm_model: str = os.getenv("LLM_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
    llm_site_url: str = os.getenv("OPEN_ROUTER_SITE_URL", "")
    llm_title: str = os.getenv("OPEN_ROUTER_TITLE", "")
    # Provider selector: 'openrouter' or 'groq'
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")
    # GROQ configuration (used when llm_provider == 'groq')
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.ai/v1")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "15"))


settings = Settings()
