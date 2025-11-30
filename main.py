import logging

from packages.Application import Application
from packages.logger.logging_setup import logging_setup

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        logging_setup(log_file_path="log/tg_stream_service.log", level=logging.INFO)
        app = Application()
        app.run()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping...")
