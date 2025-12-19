import logging
import httpx
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiAIProvider:
    """
    Провайдер для генерации текста через Google AI Studio
    """

    def __init__(self, config):
        proxy_url = f"socks5h://{config.proxy.user}:{config.proxy.password}@{config.proxy.host}:{config.proxy.port}"
        http_options = types.HttpOptions(async_client_args={'proxy': proxy_url})
        self.client = genai.Client(api_key=config.google_ai.api_key, http_options=http_options)

    async def generate_content(self, model: str, payload: str) -> str:
        try:
            # Асинхронный запрос на генерацию контента
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=payload,
            )

            text = getattr(response, "text", None)
            if not text and hasattr(response, "candidates"):
                try:
                    text = "".join(p.text for p in response.candidates[0].content.parts)
                except (IndexError, AttributeError):
                    text = str(response)

            return text or ""

        except httpx.ProxyError:
            logger.exception("Proxy connection failed. Check IP/port and VPN/proxy availability")
            return ""
        except Exception:
            logger.exception("Unexpected error while processing message")
            return ""