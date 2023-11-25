import os

from common.config.index import AppConfig

LocalConfig = AppConfig(
    SevenElevenURL="https://example.com/api",
    FamilyMartURL="https://example.com/api",
    LawsonURL="https://example.com/api",
    access_key=os.getenv("API_KEY", "dummy")
)
