import logging
from telethon import events

from packages.processors.GeminiReplyProcessor import GeminiReplyProcessor
from packages.decorators.agent_registration import agent_registration

logger = logging.getLogger(__name__)
AI_MODEL_NAME = "gemini-2.5-flash"
PROMPT = (
    "Отвечай так, будто ты Детектив-нуар 1940-х. Сообщения должны быть не больше 2-3 предложений. "
    "Отвечай на следующее сообщение:"
)
SOURCE_SYSTEM = "tgs"


@agent_registration("noir_detective")
async def noir_detective_entrypoint(
        event: events.NewMessage.Event,
        **providers
    ) -> None:
    """
    Агент отвечает на входящие сообщения в чате в стиле детективов-нуар 1940-х годов.
    Осторожно, есть побочные эффекты в виде повышения тревожности и депрессии.
    """

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
        logger.exception("Fatal error in noir_detective_entrypoint execution")
