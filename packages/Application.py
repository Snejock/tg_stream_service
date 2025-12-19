import asyncio
import logging
import yaml
from functools import partial
from telethon import TelegramClient, events
from telethon.errors import RPCError

from config.schema import AppConfig
from packages.agents import agent_registry
from packages.providers import ClickhouseProvider, GeminiAIProvider, TelegramProvider, GrokAIProvider

logger = logging.getLogger(__name__)


class Application:
    def __init__(self, config_path: str = "./config/config.yml"):
        logger.info("Initialize applications...")

        self.config = self._load_config(config_path)
        self.routing = self._normalize_routing(self.config.telegram.chats)

        if not self.routing.keys():
            logger.error("The list of chats is empty, specify them in the config")
            raise ValueError("Chats for listining are not specified")

        self.tg_client = TelegramClient(
            self.config.telegram.session_name,
            self.config.telegram.api_id,
            self.config.telegram.api_hash
        )

        logger.debug("Initializing Providers...")
        self.gemini_provider = GeminiAIProvider(config=self.config)
        self.grok_provider = GrokAIProvider(config=self.config)
        self.ch_provider = ClickhouseProvider(config=self.config)
        self.tg_provider = TelegramProvider(config=self.config, client=self.tg_client)

        self._setup_agents()
        logger.info("All components have been successfully initialized")

    async def main_process(self):
        logger.info("Launching the Clickhouse client...")
        await self.ch_provider.connect()
        logger.info("Launching the Telegram client...")

        try:
            await self.tg_client.start()
            logger.info("Telegram client launched")
            logger.info(f"Waiting for new posts in chats: {self.routing.keys()}")
            await self.tg_client.run_until_disconnected()

        except RPCError:
            logger.error(f"Telegram API error")
        except asyncio.CancelledError:
            logger.info("Application stopping...")
        except Exception:
            logger.exception(f"Unexpected error")


    def run(self):
        asyncio.run(self.main_process())

    def _setup_agents(self):
        """
        На основе данных маршрутизации (self.routing) и добавляет обработчики событий
        в клиент Telethon.

        Если агент не найден в реестре, выводит предупреждение и пропускает его.
        Использует `partial` для передачи готовых инстансов провайдеров в функции обработки.
        """
        for chat, agents in self.routing.items():
            for agt in agents:
                agent_fn = agent_registry.get(agt)
                if not agent_fn:
                    logger.warning(
                        f"Agent '{agt}' not found. Available agents: {list(agent_registry.keys())}")
                    continue

                agent_handler = partial(
                    agent_fn,
                    gemini_provider=self.gemini_provider,
                    grok_provider=self.grok_provider,
                    ch_provider=self.ch_provider,
                    tg_provider=self.tg_provider
                )

                # Регистрируется отдельный agent_handler для каждой пары (agent, chat) только на входящие сообщения
                self.tg_client.add_event_handler(agent_handler, events.NewMessage(chats=chat, incoming=True))
        logger.info(self._format_routing_log(self.routing))

    @staticmethod
    def _load_config(path: str) -> AppConfig:
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                return AppConfig(**data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {path}")

    @staticmethod
    def _normalize_routing(chats: dict) -> dict[str, list[str]]:
        """
        Приводит конфигурацию маршрутизации к каноническому виду: {chat_id: [agents]}.

        Гарантирует, что значением всегда является список строк.
        Логика преобразования:
        - None -> пустой список []
        - str -> список из одного элемента [str]
        - list/tuple -> список уникальных строк (удаляет дубликаты)

        :param chats: Исходный словарь маршрутизации из конфигурационного файла.
        :return: Нормализованный словарь, готовый к использованию в Application.
        :raises ValueError: Если встретился неподдерживаемый тип данных.
        """
        normalized_routing: dict[str, list[str]] = {}
        for chat, agents in chats.items():
            if agents is None:
                normalized_routing[chat] = []
            elif isinstance(agents, str):
                normalized_routing[chat] = [agents]
            elif isinstance(agents, list | tuple):
                normalized_routing[chat] = list({str(a) for a in agents})
            else:
                raise ValueError(f"Routing[{chat}] must be a string or list of strings")
        return normalized_routing

    @staticmethod
    def _format_routing_log(routing: dict[str, list[str]]) -> str:
        lines = ["Routing:"]
        for chat in sorted(routing):
            agents = routing[chat]
            lines.append(f"  - {chat}: {', '.join(agents) if agents else '(no agents)'}")
        return "\n".join(lines)
