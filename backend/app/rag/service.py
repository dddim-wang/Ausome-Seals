import json
import logging
import math
import os
import re
import threading
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


logger = logging.getLogger(__name__)

_INDEX_VERSION = 4
_CJK_RE = re.compile(r"[\u3400-\u9fff]+")
_WORD_RE = re.compile(r"[a-z0-9]+(?:[-_/][a-z0-9]+)*", re.IGNORECASE)
_AUSOME_MODEL_RE = re.compile(
    r"\b(?:ASC|ATC|ASBB|ASB|ATB|ATA|ASA|AJFR|AJFL|AVAX|AVA|AVS|AVL|AVE|"
    r"ARME|ARM|AWTT|AWT|AOKC3|AMOY|AMOD|AMOX|AMO|APM)\b",
    re.IGNORECASE,
)
_AUSOME_ORDER_CODE_RE = re.compile(
    r"\b(?:ASC|ATC|ASBB|ASB|ATB|ATA|ASA|AJFR|AJFL|AVAX|AVA|AVS|AVL|AVE|"
    r"ARME|ARM|AWTT|AWT|AOKC3|AMOY|AMOD|AMOX|AMO|APM)[A-Z0-9/-]{3,}\b",
    re.IGNORECASE,
)
_SPECIFICATION_MARKERS = ("规格表", "订货号", "ref.no", "ref no")

_AUSOME_MARKERS = (
    "ausome", "奥斯姆", "奥斯姆密封", "贵司", "你们公司", "你们的", "公司介绍", "公司信息",
    "产品型号", "具体型号", "产品目录", "产品规格", "报价", "询价", "company profile",
    "your company", "your product", "product model", "catalog", "quotation",
)
_INDUSTRY_MARKERS = (
    "什么是油封", "油封是什么", "密封原理", "工作原理", "如何选", "怎么选", "选型方法",
    "安装方法", "如何安装", "失效", "泄漏原因", "材料区别", "材质区别", "行业", "标准",
    "what is an oil seal", "sealing principle", "working principle", "how to select",
    "selection guide", "installation", "failure", "leakage", "material comparison",
)
_QUERY_EXPANSIONS = {
    "公司": "company profile manufacturer production research development sales service",
    "地址": "address location",
    "成立": "founded established history",
    "认证": "certification quality",
    "产品": "product oil seal type",
    "型号": "model type designation",
    "规格": "specification dimensions parameters",
    "尺寸": "dimensions shaft diameter bore width",
    "材料": "material elastomer nbr fkm ptfe",
    "材质": "material elastomer nbr fkm ptfe",
    "温度": "temperature",
    "压力": "pressure",
    "转速": "speed rotation rpm",
    "速度": "speed rotation rpm",
    "介质": "fluid medium oil grease water chemical",
    "用途": "application use equipment",
    "结构": "construction structure lip spring case",
    "原理": "principle mechanism sealing",
    "安装": "installation mounting shaft housing",
    "失效": "failure damage leakage cause",
    "泄漏": "leakage failure cause",
    "选型": "selection choose operating conditions",
    "油封": "oil seal rotary shaft seal",
}


@dataclass(frozen=True)
class KnowledgeChunk:
    domain: str
    language: str
    source: str
    page: int
    text: str


@dataclass(frozen=True)
class SourceReference:
    source: str
    page: int
    domain: str
    language: str


@dataclass(frozen=True)
class RagContext:
    domain: str
    prompt: str
    sources: tuple[SourceReference, ...]


def _language_from_name(name: str) -> str:
    return "zh" if "_CN" in name.upper() else "en"


def _domain_from_name(name: str) -> str | None:
    lowered = name.lower()
    if lowered.startswith("ausome"):
        return "ausome"
    if lowered.startswith("oilseal") or lowered.startswith("oilseals"):
        return "oilseals"
    return None


def _clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_specification_page(text: str) -> bool:
    compact = re.sub(r"\s+", "", text).lower()
    has_heading = any(marker in compact for marker in _SPECIFICATION_MARKERS)
    # Some OCR pages lose the table heading while retaining dozens of order codes.
    has_dense_order_codes = len(_AUSOME_ORDER_CODE_RE.findall(text)) >= 4
    return has_heading or has_dense_order_codes


def _split_page(
    text: str,
    *,
    size: int = 1400,
    overlap: int = 220,
    preserve_table: bool = False,
) -> list[str]:
    # Catalog spreads contain several parallel order-number / d / D / b columns.
    # Keep specification pages atomic so a code is not split from its dimensions.
    if preserve_table:
        return [text] if text else []
    if len(text) <= size:
        return [text] if text else []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = max(text.rfind("\n", start + size // 2, end), text.rfind("。", start + size // 2, end))
            if boundary > start:
                end = boundary + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks


def _tokenize(text: str) -> list[str]:
    lowered = text.lower()
    tokens = _WORD_RE.findall(lowered)
    for line in lowered.splitlines():
        # OCR often emits Chinese as "规 格 表" and "内 径". Join CJK runs
        # without concatenating the numeric cells in a specification row.
        sequence = "".join(_CJK_RE.findall(line))
        if sequence:
            tokens.append(sequence)
            tokens.extend(
                sequence[index:index + 2] for index in range(len(sequence) - 1)
            )
    return tokens


def _expanded_query(query: str) -> str:
    additions = [terms for marker, terms in _QUERY_EXPANSIONS.items() if marker in query]
    return f"{query} {' '.join(additions)}"


def route_question(question: str, conversation_context: str = "") -> str:
    combined = f"{conversation_context}\n{question}".lower()
    if _AUSOME_MODEL_RE.search(combined):
        return "ausome"
    if any(marker in combined for marker in _AUSOME_MARKERS):
        return "ausome"
    if any(marker in question.lower() for marker in _INDUSTRY_MARKERS):
        return "oilseals"
    # Generic oil-seal questions belong to the industry guide; the company catalog
    # remains the safer default for product-oriented website conversations.
    if "油封" in question or "oil seal" in question.lower():
        return "oilseals"
    return "ausome"


class KnowledgeBase:
    def __init__(self, knowledge_dir: Path, cache_path: Path):
        self.knowledge_dir = knowledge_dir
        self.cache_path = cache_path
        self._chunks: list[KnowledgeChunk] | None = None
        self._token_counts: list[Counter[str]] = []
        self._document_frequencies: dict[str, dict[str, int]] = {}
        self._domain_sizes: dict[str, int] = {}
        self._lock = threading.Lock()

    def _knowledge_files(self) -> list[Path]:
        return sorted(
            path for path in self.knowledge_dir.iterdir()
            if path.suffix.lower() in {".pdf", ".json"}
            if _domain_from_name(path.name) is not None
        )

    def _fingerprint(self, paths: list[Path]) -> list[dict]:
        return [
            {"name": path.name, "size": path.stat().st_size, "mtime_ns": path.stat().st_mtime_ns}
            for path in paths
        ]

    def _read_cache(self, fingerprint: list[dict]) -> list[KnowledgeChunk] | None:
        if not self.cache_path.exists():
            return None
        try:
            payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
            if payload.get("version") != _INDEX_VERSION or payload.get("fingerprint") != fingerprint:
                return None
            return [KnowledgeChunk(**item) for item in payload.get("chunks", [])]
        except (OSError, ValueError, TypeError):
            logger.warning("RAG cache is invalid and will be rebuilt", exc_info=True)
            return None

    def _build(self, paths: list[Path], fingerprint: list[dict]) -> list[KnowledgeChunk]:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("pypdf is required to build the RAG knowledge index") from exc

        chunks: list[KnowledgeChunk] = []
        for path in paths:
            domain = _domain_from_name(path.name)
            if domain is None:
                continue
            if path.suffix.lower() == ".json":
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    for item in payload.get("chunks", []):
                        text = _clean_text(str(item.get("text", "")))
                        language = str(item.get("language", "en")).lower()
                        if (
                            not text
                            or language not in {
                                "de", "en", "es", "fr", "id", "ja", "ru", "zh",
                            }
                        ):
                            continue
                        chunks.append(KnowledgeChunk(
                            domain=domain,
                            language=language,
                            source=path.name,
                            page=int(item.get("page", 1)),
                            text=text,
                        ))
                except (OSError, ValueError, TypeError):
                    logger.warning(
                        "Website RAG content is invalid and will be skipped: %s",
                        path,
                        exc_info=True,
                    )
                continue
            reader = PdfReader(path)
            for page_number, page in enumerate(reader.pages, start=1):
                text = _clean_text(page.extract_text() or "")
                preserve_table = domain == "ausome" and _is_specification_page(text)
                for part in _split_page(text, preserve_table=preserve_table):
                    chunks.append(KnowledgeChunk(
                        domain=domain,
                        language=_language_from_name(path.name),
                        source=path.name,
                        page=page_number,
                        text=part,
                    ))

        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": _INDEX_VERSION,
            "fingerprint": fingerprint,
            "chunks": [asdict(chunk) for chunk in chunks],
        }
        self.cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return chunks

    def _ensure_loaded(self) -> None:
        if self._chunks is not None:
            return
        with self._lock:
            if self._chunks is not None:
                return
            paths = self._knowledge_files()
            if not paths:
                raise RuntimeError(f"No supported knowledge PDFs found in {self.knowledge_dir}")
            fingerprint = self._fingerprint(paths)
            chunks = self._read_cache(fingerprint) or self._build(paths, fingerprint)
            self._chunks = chunks
            self._token_counts = [Counter(_tokenize(chunk.text)) for chunk in chunks]
            self._prepare_statistics(chunks)

    def _prepare_statistics(self, chunks: list[KnowledgeChunk]) -> None:
        frequencies: dict[str, Counter[str]] = {}
        sizes: Counter[str] = Counter()
        for chunk, counts in zip(chunks, self._token_counts):
            sizes[chunk.domain] += 1
            domain_df = frequencies.setdefault(chunk.domain, Counter())
            domain_df.update(counts.keys())
        self._document_frequencies = {
            domain: dict(counts) for domain, counts in frequencies.items()
        }
        self._domain_sizes = dict(sizes)

    def search(self, question: str, domain: str, *, limit: int = 5) -> list[KnowledgeChunk]:
        self._ensure_loaded()
        assert self._chunks is not None
        query = _expanded_query(question)
        query_tokens = Counter(_tokenize(query))
        exact_models = {match.group(0).lower() for match in _AUSOME_MODEL_RE.finditer(query)}
        exact_order_codes = {
            match.group(0).lower() for match in _AUSOME_ORDER_CODE_RE.finditer(query)
        }
        query_numbers = {
            token for token in _WORD_RE.findall(query.lower()) if token.isdigit()
        }
        domain_size = max(self._domain_sizes.get(domain, 1), 1)
        domain_df = self._document_frequencies.get(domain, {})
        scores: list[tuple[float, int]] = []

        for index, (chunk, counts) in enumerate(zip(self._chunks, self._token_counts)):
            if chunk.domain != domain:
                continue
            length_norm = 1.2 + 0.75 * (sum(counts.values()) / 250)
            score = 0.0
            for token, query_weight in query_tokens.items():
                frequency = counts.get(token, 0)
                if not frequency:
                    continue
                document_frequency = domain_df.get(token, 0)
                inverse_frequency = math.log(1 + (domain_size - document_frequency + 0.5) / (document_frequency + 0.5))
                score += query_weight * inverse_frequency * ((frequency * 2.2) / (frequency + length_norm))
            lowered_chunk = chunk.text.lower()
            score += sum(22.0 for model in exact_models if model in lowered_chunk)
            score += sum(36.0 for code in exact_order_codes if code in lowered_chunk)
            if exact_models and _is_specification_page(chunk.text):
                score += 8.0
            if exact_models and query_numbers:
                matched_numbers = sum(
                    1 for number in query_numbers
                    if re.search(rf"(?<!\d){re.escape(number)}(?!\d)", lowered_chunk)
                )
                score += matched_numbers * 3.5
            if _CJK_RE.search(question) and chunk.language == "zh":
                score *= 1.12
            elif not _CJK_RE.search(question) and chunk.language == "en":
                score *= 1.06
            if score > 0:
                scores.append((score, index))

        scores.sort(reverse=True)
        selected: list[KnowledgeChunk] = []
        seen: set[tuple[str, int]] = set()
        for _score, index in scores:
            chunk = self._chunks[index]
            identity = (chunk.source, chunk.page)
            if identity in seen:
                continue
            selected.append(chunk)
            seen.add(identity)
            if len(selected) >= limit:
                break
        return selected


class RagService:
    def __init__(self, knowledge_base: KnowledgeBase, *, result_limit: int = 5):
        self.knowledge_base = knowledge_base
        self.result_limit = result_limit

    def retrieve(self, question: str, conversation_context: str = "") -> RagContext | None:
        domain = route_question(question, conversation_context)
        search_query = f"{conversation_context}\n{question}".strip()
        try:
            chunks = self.knowledge_base.search(search_query, domain, limit=self.result_limit)
        except RuntimeError:
            logger.exception("RAG retrieval is unavailable")
            return None
        if not chunks:
            return None

        domain_description = (
            "Ausome website and product catalog"
            if domain == "ausome"
            else "general oil-seal industry reference"
        )
        excerpts = []
        references = []
        for index, chunk in enumerate(chunks, start=1):
            excerpt_limit = 6000 if _is_specification_page(chunk.text) else 1800
            excerpts.append(f"Reference excerpt {index}\n{chunk.text[:excerpt_limit]}")
            references.append(SourceReference(
                source=chunk.source,
                page=chunk.page,
                domain=chunk.domain,
                language=chunk.language,
            ))

        prompt = (
            "You are the Ausome Seals knowledge assistant. Answer in the same language as the user's latest message.\n"
            f"The retrieval route for this question is: {domain_description}.\n"
            "Use the excerpts below as the factual basis for product, company, and technical claims. "
            "Answer supported questions directly without introducing the answer with phrases such as "
            "'according to the available information', 'based on the documents', 'the catalog shows', "
            "'根据目前信息', '根据文档', or '根据目录'. Do not mention citations, source filenames, "
            "page numbers, the knowledge base, or the retrieved excerpts. If the excerpts do not contain enough "
            "information, say that the current documents cannot confirm it and ask for the missing operating "
            "conditions. Never invent a model, dimension, pressure, temperature, certification, company fact, "
            "or availability. Do not present products from the general industry reference as Ausome products. "
            "For size selection, preserve each catalog row as a unit: state the exact model or order number and "
            "label shaft/inside diameter d, outside diameter D, and width b explicitly. Never transpose columns "
            "or infer an unreadable OCR value. If a row is ambiguous, say so and ask the customer to confirm the "
            "catalog page or provide d x D x b.\n\n"
            "Retrieved excerpts:\n" + "\n\n".join(excerpts)
        )
        return RagContext(domain=domain, prompt=prompt, sources=tuple(references))


def find_knowledge_directory() -> Path | None:
    backend_dir = Path(__file__).resolve().parents[2]
    configured = os.getenv("RAG_KNOWLEDGE_DIR", "").strip()
    candidates = []
    if configured:
        path = Path(configured)
        candidates.append(path if path.is_absolute() else backend_dir / path)
    candidates.extend((
        backend_dir / "knowledge",
        backend_dir.parent / "knowledge",
        backend_dir / "tests" / "knowledge",
    ))
    for candidate in candidates:
        if candidate.is_dir() and any(candidate.glob("*.pdf")):
            return candidate
    return None


def create_rag_service() -> RagService | None:
    knowledge_dir = find_knowledge_directory()
    if knowledge_dir is None:
        logger.warning("RAG is enabled but no knowledge directory was found")
        return None
    backend_dir = Path(__file__).resolve().parents[2]
    configured_cache = os.getenv("RAG_CACHE_PATH", "").strip()
    cache_path = Path(configured_cache) if configured_cache else backend_dir / ".cache" / "rag-index.json"
    if not cache_path.is_absolute():
        cache_path = backend_dir / cache_path
    result_limit = int(os.getenv("RAG_RESULT_LIMIT", "5"))
    return RagService(KnowledgeBase(knowledge_dir, cache_path), result_limit=result_limit)
