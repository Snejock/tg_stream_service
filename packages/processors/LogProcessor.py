import logging
from telethon import events

from packages.processors.BaseProcessor import BaseProcessor

logger = logging.getLogger(__name__)


class LogProcessor(BaseProcessor):
    def __init__(self, event: events.NewMessage.Event) -> None:
        super().__init__(event)

    async def run(self):
        chat = await self.event.get_chat()

        username = getattr(chat, "username", "Unknown")
        incoming_msg_txt = self.event.message.message

        logger.info("[%s]: %s", username, incoming_msg_txt)
