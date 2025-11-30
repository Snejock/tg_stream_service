from packages.decorators.agent_registration import agent_fn, agent_registry
import importlib
import pkgutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
__all__ = ["agent_registry", "agent_fn"]
_pkg_path = Path(__file__).parent
_pkg_name = __name__


# Автоматический импорт всех *.py-файлов в текущем пакете (кроме начинающихся с подчёркивания)
for m in pkgutil.iter_modules([str(_pkg_path)]):
    if m.ispkg:
        continue
    if m.name.startswith("_"):
        continue
    try:
        importlib.import_module(f"{_pkg_name}.{m.name}")
    except Exception as e:
        logger.exception(f"Failed to import agent module {m.name}")


# Сделать модули доступными при `from packages.agents import *`
# __all__ += [m.name for m in pkgutil.iter_modules([str(_pkg_path)])
#             if not m.ispkg and not m.name.startswith("_")]
