import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.service import (
    KnowledgeBase,
    KnowledgeChunk,
    RagService,
    _is_specification_page,
    _split_page,
    _tokenize,
    route_question,
)


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
        self.assertNotIn("Ausome_Catalog_EN.pdf", context.prompt)
        self.assertIn("Do not mention citations", context.prompt)
        self.assertIn("Never invent a model", context.prompt)
        self.assertIn("Answer supported questions directly", context.prompt)
        self.assertIn("根据目前信息", context.prompt)


class CatalogSpecificationTests(unittest.TestCase):
    def test_ocr_spaced_chinese_is_searchable_as_words(self):
        tokens = _tokenize("心 规 格 表\n订 货 号 内 径 外 径 宽 度")

        self.assertIn("规格", tokens)
        self.assertIn("内径", tokens)
        self.assertIn("外径", tokens)
        self.assertIn("宽度", tokens)

    def test_dense_order_code_page_is_detected_without_ocr_heading(self):
        page = "APM000170 17 35 8\nAPM000190 19 40 6\nAPM000200 20 44 12\nAPM000220 22 42 12"

        self.assertTrue(_is_specification_page(page))

    def test_specification_page_is_kept_as_one_chunk(self):
        page = "ASC 骨架油封\n规 格 表\n" + ("ASC000400 40 52 8\n" * 200)

        self.assertTrue(_is_specification_page(page))
        self.assertEqual(_split_page(page, preserve_table=True), [page])

    def test_model_and_dimensions_prioritize_matching_specification_page(self):
        knowledge_base = KnowledgeBase(Path("."), Path("unused.json"))
        knowledge_base._chunks = [
            KnowledgeChunk(
                domain="ausome", language="zh", source="catalog.pdf", page=8,
                text="ASC 骨架油封 规 格 表\nASC120400 40 62 8\nASC130400 40 62 10",
            ),
            KnowledgeChunk(
                domain="ausome", language="zh", source="catalog.pdf", page=20,
                text="ATB 外骨架油封 规 格 表\nATB000400 40 62 10",
            ),
        ]
        knowledge_base._token_counts = [
            __import__("collections").Counter(_tokenize(chunk.text))
            for chunk in knowledge_base._chunks
        ]
        knowledge_base._prepare_statistics(knowledge_base._chunks)

        results = knowledge_base.search("ASC 内径40 外径62 宽度10", "ausome", limit=1)

        self.assertEqual(results[0].page, 8)

    def test_size_selection_prompt_has_table_guardrails(self):
        context = RagService(FakeKnowledgeBase()).retrieve("ASC 有哪些尺寸？")

        self.assertIn("label shaft/inside diameter d", context.prompt)
        self.assertIn("Never transpose columns", context.prompt)


class WebsiteKnowledgeTests(unittest.TestCase):
    def test_website_json_is_loaded_and_searchable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            knowledge_dir = Path(temp_dir)
            website_path = knowledge_dir / "Ausome_Website_Content.rag.json"
            website_path.write_text(json.dumps({
                "chunks": [{
                    "language": "zh",
                    "page": 1,
                    "text": "Ausome 网站内容\n工厂位于中国南京，配备多条油封生产线。",
                }],
            }, ensure_ascii=False), encoding="utf-8")
            knowledge_base = KnowledgeBase(
                knowledge_dir,
                knowledge_dir / "rag-cache.json",
            )

            results = knowledge_base.search("工厂在哪里？", "ausome", limit=1)

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].source, website_path.name)
            self.assertEqual(results[0].language, "zh")
            self.assertIn("南京", results[0].text)


class KnowledgeCacheTests(unittest.TestCase):
    def test_fingerprint_uses_content_not_modification_time(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            knowledge_dir = Path(temp_dir)
            website_path = knowledge_dir / "Ausome_Website_Content.rag.json"
            website_path.write_text('{"chunks": []}', encoding="utf-8")
            knowledge_base = KnowledgeBase(
                knowledge_dir,
                knowledge_dir / "rag-cache.json",
            )

            original = knowledge_base._fingerprint([website_path])
            stat = website_path.stat()
            os.utime(
                website_path,
                ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000),
            )

            self.assertEqual(
                knowledge_base._fingerprint([website_path]),
                original,
            )


if __name__ == "__main__":
    unittest.main()
