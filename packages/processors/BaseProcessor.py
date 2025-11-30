from telethon import events


class BaseProcessor:
    """
    Базовый класс процессора обработки событий в телеграм.
    Инициализирует контекст события и конфигурацию.
    """
    def __init__(self, event: events.NewMessage.Event):
        self.event = event
        self.client = event.client
