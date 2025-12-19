import logging
import httpx
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class GrokAIProvider:
    """
    Провайдер для генерации текста через OpenAI
    """
    def __init__(self, config):
        proxy_url = f"socks5h://{config.proxy.user}:{config.proxy.password}@{config.proxy.host}:{config.proxy.port}"
        http_client = httpx.AsyncClient(proxy=proxy_url, timeout=60)
        self.client = AsyncOpenAI(
            api_key=config.x_ai.api_key,
            base_url="https://api.x.ai/v1",
            http_client=http_client,
        )

    async def generate_content(self, model: str, payload: str) -> str:
        try:
            messages = [
                {"role": "system", "content": "Отвечай кратко и по делу на русском языке."},
                {"role": "user", "content": payload},
            ]

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
            )

            text = getattr(response.choices[0].message, "content", "")
            return text

        except httpx.ProxyError:
            logger.exception("Proxy connection failed. Check IP/port and VPN/proxy availability")
            return ""
        except Exception:
            logger.exception("Unexpected error while processing message")
            return ""
