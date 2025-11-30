import logging
from telethon import events

from packages.processors.GeminiReplyProcessor import GeminiReplyProcessor
from packages.decorators.agent_registration import agent_registration

logger = logging.getLogger(__name__)
AI_MODEL_NAME = "gemini-2.5-flash"
PROMPT = (
    "Отвечай мне так, будто ты добрый учитель английского языка, который обучает ребёнка 10 лет. "
    "Используй простые объяснения, примеры, игровые элементы. Всегда хвали ребёнка за успехи, даже небольшие. "
    "Помогай учить английский язык в дружелюбной и поддерживающей манере. "
    "Твои ответы не должны превышать более 5 предложений. "
    "Отвечай на следующее сообщение:"
)
SOURCE_SYSTEM = "tgs"


@agent_registration("english_teacher")
async def english_teacher_entrypoint(
        event: events.NewMessage.Event,
        **providers
    ) -> None:
    try:
        agent = GeminiReplyProcessor(
            event=event,
            ai_model_name=AI_MODEL_NAME,
            prompt=PROMPT,
            source_system=SOURCE_SYSTEM,
            **providers
        )
        await agent.run()

    except TypeError as e:
        logger.exception("Dependency injection error: arguments mismatch")
    except Exception as e:
        logger.exception("Fatal error in english_teacher_entrypoint execution")
