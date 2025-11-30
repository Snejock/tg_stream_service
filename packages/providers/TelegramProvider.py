import logging


logger = logging.getLogger(__name__)

class TelegramProvider:
    """
    Провайдер для взаимодействия с Telegram API (Telethon).
    """

    def __init__(self, config, client):
        self.config = config
        self.client = client

    async def send_message(self, chat_id, text: str):
        try:
            await self.client.send_message(
                entity=chat_id,
                message=text
            )
        except Exception:
            logger.exception(f"TelegramProvider error")
