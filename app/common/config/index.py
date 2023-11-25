import os
from dataclasses import dataclass

from local_config import LocalConfig


@dataclass
class AppConfig:
    SevenElevenURL: str
    FamilyMartURL: str
    LawsonURL: str
    access_key: str

def get_config() -> AppConfig:
    env = os.getenv("APP_ENV", "local")

    if env == "local":
        return LocalConfig
#    elif env == "dev":
#        return DevConfig
    else:
        raise ValueError("Invalid environment")
