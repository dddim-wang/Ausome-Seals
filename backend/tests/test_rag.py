import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.service import KnowledgeChunk, RagService, route_question


class FakeKnowledgeBase:
    def __init__(self):
        self.domain = None

    def search(self, question, domain, *, limit):
        self.domain = domain
        return [KnowledgeChunk(
            domain=domain,
            language="en",
            source="Ausome_Catalog_EN.pdf" if domain == "ausome" else "Oilseal_EN.pdf",
            page=7,
            text="Reference text for the selected knowledge domain.",
        )]


class RagRoutingTests(unittest.TestCase):
    def test_routes_company_and_product_models_to_ausome(self):
        self.assertEqual(route_question("Tell me about Ausome"), "ausome")
        self.assertEqual(route_question("What pressure can ASC handle?"), "ausome")
        self.assertEqual(route_question("Ausome 有哪些产品型号？"), "ausome")

    def test_routes_generic_oil_seal_questions_to_industry_library(self):
        self.assertEqual(route_question("油封为什么会泄漏？"), "oilseals")
        self.assertEqual(route_question("What is an oil seal?"), "oilseals")
        self.assertEqual(route_question("How should an oil seal be installed?"), "oilseals")

    def test_product_context_is_preserved_for_follow_up_questions(self):
        self.assertEqual(
            route_question("What material does it use?", "Tell me about the ASC model"),
            "ausome",
        )

    def test_context_contains_source_label_and_domain_guardrail(self):
        knowledge_base = FakeKnowledgeBase()
        context = RagService(knowledge_base).retrieve("What pressure can ASC handle?")

        self.assertIsNotNone(context)
        self.assertEqual(context.domain, "ausome")
        self.assertEqual(knowledge_base.domain, "ausome")
        self.assertIn("[Ausome_Catalog_EN.pdf p.7]", context.prompt)
        self.assertIn("Never invent a model", context.prompt)


if __name__ == "__main__":
    unittest.main()
