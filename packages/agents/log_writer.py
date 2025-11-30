import logging
from telethon import events

from packages.processors.LogProcessor import LogProcessor
from packages.decorators.agent_registration import agent_registration

logger = logging.getLogger(__name__)


@agent_registration("log_writer")
async def log_writer_entrypoint(
        event: events.NewMessage.Event,
        **providers) -> None:
    """
    Агент выполняет логирование всех входящих сообщений в соответствии с настройками logger.
    По-умолчанию пишет лог в консоль (stdout) и файл log/tg_stream_service.log.
    """
    try:
        agent = LogProcessor(event)
        await agent.run()

    except TypeError as e:
        logger.exception("Dependency injection error: arguments mismatch")
    except Exception as e:
        logger.exception("Fatal error in log_writer_entrypoint execution")
