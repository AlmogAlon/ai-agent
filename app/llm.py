import os

from openai import OpenAI

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-mini")


def generate(
    input_items: list[dict],
    tools: list[dict],
    previous_response_id: str | None = None,
    max_output_tokens: int = 256,
):
    client = OpenAI()
    request = {
        "model": OPENAI_MODEL,
        "input": input_items,
        "tools": tools,
        "max_output_tokens": max_output_tokens,
    }
    if previous_response_id is not None:
        request["previous_response_id"] = previous_response_id
    return client.responses.create(**request)
