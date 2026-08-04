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


class BrokenKnowledgeBase:
    def search(self, _question, _domain, *, limit):
        raise OSError("PDF is damaged")


class FakeEmbeddingIndex:
    def __init__(self, scores, route="oilseals"):
        self.scores = scores
        self.route_domain = route

    def similarities(self, _question, _chunks):
        return self.scores

    def route(self, _question):
        return self.route_domain


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

    def test_order_code_never_uses_the_semantic_domain_router(self):
        self.assertEqual(
            route_question(
                "ASC000400 dimensions",
                semantic_router=lambda _question: "oilseals",
            ),
            "ausome",
        )

    def test_avc_model_routes_to_ausome_catalog(self):
        self.assertEqual(route_question("你们公司有AVC油封吗？"), "ausome")
    def test_semantic_router_handles_other_languages(self):
        router = lambda _question: "oilseals"

        self.assertEqual(
            route_question(
                "¿Por qué falla un retén del eje?",
                semantic_router=router,
            ),
            "oilseals",
        )

    def test_non_runtime_retrieval_error_degrades_without_raising(self):
        with self.assertLogs("app.rag.service", level="ERROR"):
            context = RagService(BrokenKnowledgeBase()).retrieve(
                "What is an oil seal?"
            )

        self.assertIsNone(context)

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

    def test_specification_page_is_split_on_rows_with_bounded_overlap(self):
        page = "ASC 骨架油封\n规 格 表\n" + ("ASC000400 40 52 8\n" * 200)

        self.assertTrue(_is_specification_page(page))
        chunks = _split_page(
            page,
            size=40,
            overlap=8,
            preserve_table=True,
            token_counter=lambda value: len(value.split()) + 2,
        )

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk.split()) + 2 <= 40 for chunk in chunks))
        self.assertTrue(all(chunk.startswith("ASC") for chunk in chunks[1:]))

    def test_regular_page_uses_token_windows_instead_of_character_windows(self):
        page = " ".join(f"word{index}" for index in range(80))

        chunks = _split_page(
            page,
            size=30,
            overlap=6,
            token_counter=lambda value: len(value.split()) + 2,
        )

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk.split()) + 2 <= 30 for chunk in chunks))
        self.assertTrue(set(chunks[0].split()) & set(chunks[1].split()))

    def test_size_range_expands_to_four_adjacent_chunks_on_the_same_page(self):
        knowledge_base = KnowledgeBase(
            Path("."),
            Path("unused.json"),
            FakeEmbeddingIndex([0.99, 0.95, 0.3, 0.2, 0.1]),
        )
        knowledge_base._chunks = [KnowledgeChunk(
            domain="ausome", language="zh", source="catalog.pdf", page=16,
            text="ATA 双骨架油封规格表介绍",
        )] + [
            KnowledgeChunk(
                domain="ausome", language="zh", source="catalog.pdf", page=17,
                text=f"ATA 规格表\nATA00050{index} {50 + index} 70 10",
            )
            for index in range(4)
        ]
        knowledge_base._token_counts = [
            __import__("collections").Counter(_tokenize(chunk.text))
            for chunk in knowledge_base._chunks
        ]
        knowledge_base._prepare_statistics(knowledge_base._chunks)

        results = knowledge_base.search("ATA 有哪些尺寸？", "ausome", limit=5)

        self.assertEqual([chunk.page for chunk in results[:4]], [17, 17, 17, 17])

    def test_regular_question_limits_each_page_to_two_chunks(self):
        knowledge_base = KnowledgeBase(
            Path("."),
            Path("unused.json"),
            FakeEmbeddingIndex([0.95, 0.9, 0.85, 0.8]),
        )
        knowledge_base._chunks = [
            KnowledgeChunk(
                domain="oilseals", language="en", source="guide.pdf", page=3,
                text=f"Oil seal installation guidance section {index}",
            )
            for index in range(3)
        ] + [KnowledgeChunk(
            domain="oilseals", language="en", source="guide.pdf", page=4,
            text="Oil seal installation checklist",
        )]
        knowledge_base._token_counts = [
            __import__("collections").Counter(_tokenize(chunk.text))
            for chunk in knowledge_base._chunks
        ]
        knowledge_base._prepare_statistics(knowledge_base._chunks)

        results = knowledge_base.search("oil seal installation", "oilseals", limit=4)

        self.assertEqual(sum(chunk.page == 3 for chunk in results), 2)

    def test_overlapping_order_code_rows_are_sent_only_once(self):
        class OverlappingKnowledgeBase:
            def search(self, _question, _domain, *, limit):
                return [
                    KnowledgeChunk(
                        domain="ausome", language="zh",
                        source="catalog.pdf", page=17,
                        text=(
                            "ATA 规格表\n"
                            "ATA000500 50 65 10\n"
                            "ATA100500 50 80 10"
                        ),
                    ),
                    KnowledgeChunk(
                        domain="ausome", language="zh",
                        source="catalog.pdf", page=17,
                        text="ATA100500 50 80 10\nATA000600 60 80 8",
                    ),
                ]

        context = RagService(OverlappingKnowledgeBase()).retrieve(
            "ATA 有哪些尺寸？"
        )

        self.assertEqual(context.prompt.count("ATA100500 50 80 10"), 1)


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


    def test_semantic_retrieval_can_return_a_cross_language_match(self):
        knowledge_base = KnowledgeBase(
            Path("."),
            Path("unused.json"),
            FakeEmbeddingIndex([0.91, 0.15]),
        )
        knowledge_base._chunks = [
            KnowledgeChunk(
                domain="oilseals", language="zh", source="guide.pdf", page=3,
                text="旋转轴密封安装时应保护密封唇口。",
            ),
            KnowledgeChunk(
                domain="oilseals", language="en", source="guide.pdf", page=4,
                text="Chemical storage guidance.",
            ),
        ]
        knowledge_base._token_counts = [
            __import__("collections").Counter(_tokenize(chunk.text))
            for chunk in knowledge_base._chunks
        ]
        knowledge_base._prepare_statistics(knowledge_base._chunks)

        results = knowledge_base.search(
            "オイルシールを正しく取り付ける方法は？",
            "oilseals",
            limit=1,
        )

        self.assertEqual(results[0].page, 3)

    def test_lexical_search_survives_embedding_failure(self):
        knowledge_base = KnowledgeBase(
            Path("."),
            Path("unused.json"),
            FakeEmbeddingIndex(None),
        )
        knowledge_base._chunks = [
            KnowledgeChunk(
                domain="oilseals", language="en", source="guide.pdf", page=6,
                text="Oil seal installation requires a clean shaft.",
            ),
        ]
        knowledge_base._token_counts = [
            __import__("collections").Counter(_tokenize(chunk.text))
            for chunk in knowledge_base._chunks
        ]
        knowledge_base._prepare_statistics(knowledge_base._chunks)

        results = knowledge_base.search("oil seal installation", "oilseals")

        self.assertEqual(results[0].page, 6)

    def test_exact_order_code_beats_semantic_ranking(self):
        knowledge_base = KnowledgeBase(
            Path("."),
            Path("unused.json"),
            FakeEmbeddingIndex([0.2, 0.99]),
        )
        knowledge_base._chunks = [
            KnowledgeChunk(
                domain="ausome", language="en", source="catalog.pdf", page=8,
                text="ASC000400 40 62 8",
            ),
            KnowledgeChunk(
                domain="ausome", language="en", source="catalog.pdf", page=20,
                text="ASC product installation overview",
            ),
        ]
        knowledge_base._token_counts = [
            __import__("collections").Counter(_tokenize(chunk.text))
            for chunk in knowledge_base._chunks
        ]
        knowledge_base._prepare_statistics(knowledge_base._chunks)

        results = knowledge_base.search("ASC000400", "ausome", limit=1)

        self.assertEqual(results[0].page, 8)


    def test_order_code_falls_back_to_its_model_family_when_ocr_loses_code(self):
        knowledge_base = KnowledgeBase(
            Path("."),
            Path("unused.json"),
            FakeEmbeddingIndex([0.1, 0.99]),
        )
        knowledge_base._chunks = [
            KnowledgeChunk(
                domain="ausome", language="zh", source="catalog.pdf", page=8,
                text="骨架油封 ASC 规格表\nASCO00400 40 62 8",
            ),
            KnowledgeChunk(
                domain="ausome", language="zh", source="catalog.pdf", page=20,
                text="骨架油封 ATB 规格表",
            ),
        ]
        knowledge_base._token_counts = [
            __import__("collections").Counter(_tokenize(chunk.text))
            for chunk in knowledge_base._chunks
        ]
        knowledge_base._prepare_statistics(knowledge_base._chunks)

        results = knowledge_base.search("ASC000400的尺寸", "ausome", limit=1)

        self.assertEqual(results[0].page, 8)

    def test_avc_question_prioritizes_avc_catalog_page(self):
        knowledge_base = KnowledgeBase(
            Path("."),
            Path("unused.json"),
            FakeEmbeddingIndex([0.1, 0.99]),
        )
        knowledge_base._chunks = [
            KnowledgeChunk(
                domain="ausome", language="zh", source="catalog.pdf", page=18,
                text="无弹簧脂密封 AVC、AVB 规格表",
            ),
            KnowledgeChunk(
                domain="ausome", language="zh", source="catalog.pdf", page=3,
                text="公司介绍和常用油封材料",
            ),
        ]
        knowledge_base._token_counts = [
            __import__("collections").Counter(_tokenize(chunk.text))
            for chunk in knowledge_base._chunks
        ]
        knowledge_base._prepare_statistics(knowledge_base._chunks)

        results = knowledge_base.search("你们公司有avc油封吗？", "ausome", limit=1)

        self.assertEqual(results[0].page, 18)

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
    def test_runtime_does_not_rebuild_a_missing_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            knowledge_dir = Path(temp_dir)
            (knowledge_dir / "Ausome_Website_Content.rag.json").write_text(
                '{"chunks": []}', encoding="utf-8"
            )
            knowledge_base = KnowledgeBase(
                knowledge_dir,
                knowledge_dir / "missing-cache.json",
                build_missing=False,
            )

            with self.assertRaisesRegex(RuntimeError, "run prebuild_rag.py"):
                knowledge_base.warm_up()

            self.assertFalse((knowledge_dir / "missing-cache.json").exists())

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
