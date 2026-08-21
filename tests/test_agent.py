import unittest
from types import SimpleNamespace
from unittest.mock import call, patch

from app.agent import run_agent


class AgentTests(unittest.TestCase):
    @patch("app.agent.append_message")
    @patch("app.agent.get_history", return_value=[])
    @patch("app.agent.generate")
    def test_executes_a_native_tool_call_and_returns_the_final_answer(
        self, generate, _get_history, append_message
    ):
        tool_call = SimpleNamespace(
            type="function_call",
            name="calculator",
            arguments='{"expression":"123 * 456"}',
            call_id="call-123",
        )
        generate.side_effect = [
            SimpleNamespace(id="response-1", output=[tool_call], output_text=""),
            SimpleNamespace(id="response-2", output=[], output_text="123 × 456 = 56088"),
        ]

        answer = run_agent("session-1", "What is 123 * 456?")

        self.assertEqual(answer, "123 × 456 = 56088")
        second_request = generate.call_args_list[1].kwargs
        self.assertEqual(second_request["previous_response_id"], "response-1")
        self.assertEqual(
            second_request["input_items"],
            [
                {
                    "type": "function_call_output",
                    "call_id": "call-123",
                    "output": "56088",
                }
            ],
        )
        append_message.assert_has_calls(
            [
                call("session-1", "user", "What is 123 * 456?"),
                call("session-1", "assistant", "123 × 456 = 56088"),
            ]
        )


if __name__ == "__main__":
    unittest.main()
