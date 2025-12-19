import logging
from telethon import events

from packages.decorators.agent_registration import agent_registration
from packages.processors.GrokReplyProcessor import GrokReplyProcessor

logger = logging.getLogger(__name__)
AI_MODEL_NAME = "grok-4"
PROMPT = (
    "Отвечай так, будто ты старый морской пират. Сообщения должны быть не больше 2-3 предложений. "
    "Отвечай на следующее сообщение:"
)
SOURCE_SYSTEM = "tgs"


@agent_registration("pirate")
async def pirate_entrypoint(
        event: events.NewMessage.Event,
        **providers
    ) -> None:

    try:
        agent = GrokReplyProcessor(
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
