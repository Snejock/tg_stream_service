import logging

from packages.Application import Application
from packages.logger.logger_setup import logger_setup

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        logger_setup(log_file_path="log/tg_stream_service.log", level=logging.INFO)
        app = Application()
        app.run()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping...")
