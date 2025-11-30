from typing import Dict, List
from pydantic import BaseModel, Field


class TelegramConfig(BaseModel):
    api_id: int
    api_hash: str
    session_name: str
    chats: Dict[str, str | List[str]] = Field(default_factory=dict)

class ProxyConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str

class ClickhouseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    secure: bool

class GoogleAIConfig(BaseModel):
    api_key: str

class AppConfig(BaseModel):
    telegram: TelegramConfig
    proxy: ProxyConfig
    google_ai: GoogleAIConfig
    clickhouse: ClickhouseConfig
