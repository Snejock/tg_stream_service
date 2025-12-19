import logging
from datetime import datetime
from telethon import events

from packages.processors.BaseProcessor import BaseProcessor
from packages.providers import ClickhouseProvider, GeminiAIProvider, TelegramProvider

logger = logging.getLogger(__name__)


class GeminiReplyCHProcessor(BaseProcessor):
    def __init__(self,
                 event: events.NewMessage.Event,
                 ai_model_name: str,
                 prompt: str,
                 source_system: str,
                 trg_table_name: str,
                 gemini_provider: GeminiAIProvider,
                 ch_provider: ClickhouseProvider,
                 tg_provider: TelegramProvider,
                 **kwargs
                 ):
        super().__init__(event)
        self.source_system = source_system
        self.gemini_provider = gemini_provider
        self.ch_provider = ch_provider
        self.tg_provider = tg_provider
        self.ai_model_name = ai_model_name
        self.trg_table_name = trg_table_name
        self.prompt = prompt
        self.incoming_msg_txt:str | None = None
        self.ai_generated_txt:str | None = None

    async def run(self):
        chat = await self.event.get_chat()

        loaded_dttm = datetime.now()
        username = getattr(chat, "username", "Unknown")
        incoming_msg_txt = self.event.message.message
        logger.info("[%s]: %s", username, incoming_msg_txt)

        payload = f"{self.prompt} '{incoming_msg_txt}'"

        # Генерация ответа с помощью AI
        self.ai_generated_txt = await self.gemini_provider.generate_content(self.ai_model_name, payload)

        if not self.ai_generated_txt:
            logger.warning(f"[{username}] AI generated text is empty")
            return

        logger.info("[%s]: %s", self.ai_model_name, self.ai_generated_txt)

        # Отправка сгенерированного сообщения в чат
        await self.tg_provider.send_message(chat_id=self.event.chat_id, text=self.ai_generated_txt)

        data = [
            loaded_dttm,
            self.source_system or "",
            self.event.message.date,
            self.event.chat_id,
            self.event.chat.username or "",
            self.event.message.id,
            self.event.message.message or "",
            self.event.is_channel,
            self.event.is_group,
            self.event.is_private,
            self.ai_generated_txt or "",
            self.ai_model_name or ""
        ]

        # Сохранение данных в Clickhouse
        await self.ch_provider.async_insert(
            table=self.trg_table_name,
            data=data,
            columns=[
                'loaded_dttm',
                "source_system",
                "created_dttm",
                "chat_id",
                "chat_nm",
                "message_id",
                "message_txt",
                "channel_flg",
                "group_flg",
                "private_flg",
                "ai_generated_txt",
                "ai_model_name"
            ]
        )
