import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.orchestrator import GLOBAL_AGENT_PROMPT, classify_intent


class AgentIntentTests(unittest.TestCase):
    def test_plain_greeting_is_general(self):
        self.assertEqual(classify_intent("你好！"), ("general", "respond"))

    def test_greeting_does_not_hide_product_question(self):
        self.assertEqual(
            classify_intent("你好，你有的最大尺寸的密封是多大？"),
            ("technical_qa", "respond"),
        )


    def test_global_prompt_requires_direct_answers(self):
        self.assertIn("answer directly", GLOBAL_AGENT_PROMPT)
        self.assertIn("根据文档", GLOBAL_AGENT_PROMPT)


if __name__ == "__main__":
    unittest.main()
