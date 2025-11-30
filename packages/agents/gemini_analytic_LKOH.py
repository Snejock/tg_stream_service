import logging
from telethon import events

from packages.processors.GeminiAnalysisCHProcessor import GeminiAnalysisCHProcessor
from packages.decorators.agent_registration import agent_registration

logger = logging.getLogger(__name__)
AI_MODEL_NAME = "gemini-2.5-flash"
PROMPT = (
    "Ты — старший финансовый аналитик по российскому фондовому рынку (MOEX), специализирующийся на нефтегазовом секторе и компании ПАО «Лукойл» (LKOH). "
    "Проанализируй новость ниже и оцени влияние новости на срок одну неделю на стоимость акций компании ПАО «Лукойл» (LKOH) на российском фондовом рынке (MOEX). "
    "Твоя задача — выдать ответ строго в формате JSON без лишних слов и markdown-разметки. "
    "\nФормат JSON: "
    "\n{"
    "\n  'impact_score': <число от -100 до 100, где -100 — полный крах, 0 — нейтрально, +100 — взрывной рост>, "
    "\n  'confidence': <число от 0 до 100, показывающее насколько ты уверен в оценке"
    "\n  'reasoning': <обоснование>"
    "\n}"
    "\nНовость: "
)
SOURCE_SYSTEM = "tgs"
TRG_TABLE_NAME = "ods_tgs.posts"


@agent_registration("gemini_analytic_LKOH")
async def gemini_analytic_LKOH_entrypoint(
        event: events.NewMessage.Event,
        **providers
    ) -> None:
    """
    Агент анализирует сообщения из новостного канала и производит оценку влияния данной новости на стоимость акций
    компании ПАО «Лукойл» (LKOH) на российском фондовом рынке (MOEX).
    Результат анализа десериализуется, валидируется и записывается в базу данных (Clickhouse).
    """

    try:
        agent = GeminiAnalysisCHProcessor(
            event=event,
            ai_model_name=AI_MODEL_NAME,
            prompt=PROMPT,
            source_system=SOURCE_SYSTEM,
            trg_table_name=TRG_TABLE_NAME,
            **providers
        )
        await agent.run()

    except TypeError as e:
        logger.exception("Dependency injection error: arguments mismatch")
    except Exception as e:
        logger.exception("Fatal error in gemini_analytic_LKOH_entrypoint execution")
