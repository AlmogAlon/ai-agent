import json
import unittest

from app.tools import TOOLS, tool_definitions


class ToolTests(unittest.TestCase):
    def test_calculator_has_a_strict_function_definition(self):
        definition = tool_definitions()[0]

        self.assertEqual(definition["type"], "function")
        self.assertEqual(definition["name"], "calculator")
        self.assertTrue(definition["strict"])
        self.assertFalse(definition["parameters"]["additionalProperties"])

    def test_calculator_accepts_json_arguments(self):
        result = TOOLS["calculator"].call(json.dumps({"expression": "123 * 456"}))

        self.assertEqual(result, "56088")

    def test_tool_returns_an_error_for_invalid_arguments(self):
        result = TOOLS["calculator"].call("not-json")

        self.assertIn("Error calling calculator", result)


if __name__ == "__main__":
    unittest.main()
