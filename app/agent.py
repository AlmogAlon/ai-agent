from app.llm import generate
from app.memory import append_message, get_history
from app.prompts import build_messages
from app.tools import TOOLS, tool_definitions

MAX_ITERATIONS = 5


def run_agent(session_id: str, user_message: str) -> str:
    history = get_history(session_id)
    input_items = build_messages(history, user_message)
    previous_response_id = None

    final_answer = None

    for _ in range(MAX_ITERATIONS):
        response = generate(
            input_items=input_items,
            tools=tool_definitions(),
            previous_response_id=previous_response_id,
        )

        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            final_answer = response.output_text.strip()
            break

        input_items = []
        for call in calls:
            tool = TOOLS.get(call.name)
            result = (
                tool.call(call.arguments)
                if tool is not None
                else f"Error: unknown tool '{call.name}'"
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
    return final_answer
