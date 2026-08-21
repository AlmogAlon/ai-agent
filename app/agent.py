import logging
import time

from app.llm import generate
from app.memory import append_message, get_history
from app.prompts import build_messages
from app.tools import TOOLS, tool_definitions

MAX_ITERATIONS = 5
LOG_VALUE_LIMIT = 500
logger = logging.getLogger("uvicorn.error")


def _for_log(value: str) -> str:
    compact = value.replace("\n", "\\n")
    if len(compact) <= LOG_VALUE_LIMIT:
        return compact
    return f"{compact[:LOG_VALUE_LIMIT]}... [truncated]"


def run_agent(session_id: str, user_message: str) -> str:
    started_at = time.monotonic()
    history = get_history(session_id)
    input_items = build_messages(history, user_message)
    previous_response_id = None
    logger.info(
        "agent.run_started session_id=%s history_messages=%d",
        session_id,
        len(history),
    )

    final_answer = None

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.info(
            "agent.model_request session_id=%s iteration=%d",
            session_id,
            iteration,
        )
        response = generate(
            input_items=input_items,
            tools=tool_definitions(),
            previous_response_id=previous_response_id,
        )

        calls = [item for item in response.output if item.type == "function_call"]
        logger.info(
            "agent.model_response session_id=%s iteration=%d response_id=%s tool_calls=%d",
            session_id,
            iteration,
            response.id,
            len(calls),
        )
        if not calls:
            final_answer = response.output_text.strip()
            break

        input_items = []
        for call in calls:
            logger.info(
                "agent.tool_started session_id=%s iteration=%d tool=%s call_id=%s arguments=%s",
                session_id,
                iteration,
                call.name,
                call.call_id,
                _for_log(call.arguments),
            )
            tool = TOOLS.get(call.name)
            result = (
                tool.call(call.arguments)
                if tool is not None
                else f"Error: unknown tool '{call.name}'"
            )
            logger.info(
                "agent.tool_completed session_id=%s iteration=%d tool=%s call_id=%s result=%s",
                session_id,
                iteration,
                call.name,
                call.call_id,
                _for_log(result),
            )
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": result,
                }
            )
        previous_response_id = response.id

    if final_answer is None:
        final_answer = "I wasn't able to reach a final answer in time."

    append_message(session_id, "user", user_message)
    append_message(session_id, "assistant", final_answer)
    logger.info(
        "agent.run_completed session_id=%s duration_ms=%d",
        session_id,
        round((time.monotonic() - started_at) * 1000),
    )
    return final_answer
