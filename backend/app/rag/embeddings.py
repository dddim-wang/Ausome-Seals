import base64
import hashlib
import json
import logging
import threading
import warnings
from array import array
from pathlib import Path
from typing import Protocol, Sequence


logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
_VECTOR_INDEX_VERSION = 1

_DOMAIN_ANCHORS = {
    "ausome": (
        "Ausome company, product catalog, model, quotation and order code",
        "奥斯姆公司、产品目录、型号、报价和订货号",
        "Empresa Ausome, catálogo de productos, modelo, cotización y código de pedido",
        "Entreprise Ausome, catalogue de produits, modèle, devis et référence de commande",
        "Ausome Firma, Produktkatalog, Modell, Angebot und Bestellnummer",
        "Ausome社、製品カタログ、型番、見積もり、注文番号",
        "Компания Ausome, каталог продукции, модель, предложение и код заказа",
    ),
    "oilseals": (
        "General oil seal knowledge: principle, installation, failure, leakage and material selection",
        "油封基础知识：工作原理、安装、失效、泄漏和材料选型",
        "Conocimientos sobre retenes de aceite: principio, instalación, fallos, fugas y materiales",
        "Connaissances sur les joints d'étanchéité: principe, installation, panne, fuite et matériau",
        "Wellendichtring-Grundlagen: Funktion, Einbau, Ausfall, Leckage und Werkstoffauswahl",
        "オイルシールの基礎知識：原理、取り付け、故障、漏れ、材料の選定",
        "Общие сведения о сальниках: принцип работы, установка, утечки, неисправности и выбор материала",
    ),
}


class EmbeddableChunk(Protocol):
    domain: str
    language: str
    source: str
    page: int
    text: str


def _normalize(values: Sequence[float]) -> list[float]:
    magnitude = sum(float(value) ** 2 for value in values) ** 0.5
    if not magnitude:
        return [0.0 for _ in values]
    return [float(value) / magnitude for value in values]


def _chunk_fingerprint(chunks: Sequence[EmbeddableChunk]) -> str:
    digest = hashlib.sha256()
    for chunk in chunks:
        digest.update(
            f"{chunk.domain}\0{chunk.language}\0{chunk.source}\0"
            f"{chunk.page}\0{chunk.text}\0".encode("utf-8")
        )
    return digest.hexdigest()


class MultilingualEmbeddingIndex:
    """Optional FastEmbed-backed semantic index with a lexical-safe fallback."""

    def __init__(
        self,
        cache_path: Path,
        *,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        model_cache_dir: Path | None = None,
        threads: int | None = None,
        build_missing: bool = False,
    ):
        self.cache_path = cache_path
        self.model_name = model_name
        self.model_cache_dir = model_cache_dir
        self.threads = threads
        self.build_missing = build_missing
        self._model = None
        self._vectors: list[list[float]] | None = None
        self._vector_fingerprint: str | None = None
        self._anchors: dict[str, list[list[float]]] | None = None
        self._query_vectors: dict[str, list[float]] = {}
        self._disabled = False
        self._lock = threading.Lock()

    def _get_model(self):
        if self._disabled:
            return None
        if self._model is not None:
            return self._model
        try:
            from fastembed import TextEmbedding

            cache_dir = (
                str(self.model_cache_dir) if self.model_cache_dir is not None else None
            )
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=r"The model .* now uses mean pooling.*",
                    category=UserWarning,
                )
                self._model = TextEmbedding(
                    model_name=self.model_name,
                    cache_dir=cache_dir,
                    threads=self.threads,
                )
            return self._model
        except Exception:
            self._disabled = True
            logger.exception(
                "Multilingual embeddings are unavailable; using lexical RAG only"
            )
            return None

    def _embed(self, texts: Sequence[str]) -> list[list[float]] | None:
        model = self._get_model()
        if model is None:
            return None
        try:
            return [_normalize(vector) for vector in model.embed(list(texts))]
        except Exception:
            self._disabled = True
            logger.exception(
                "Embedding generation failed; using lexical RAG only"
            )
            return None

    def _embed_query(self, text: str) -> list[float] | None:
        key = text.strip().lower()
        cached = self._query_vectors.get(key)
        if cached is not None:
            return cached
        vectors = self._embed([key])
        if not vectors:
            return None
        if len(self._query_vectors) >= 64:
            self._query_vectors.pop(next(iter(self._query_vectors)))
        self._query_vectors[key] = vectors[0]
        return vectors[0]

    def _read_cache(
        self, chunks: Sequence[EmbeddableChunk]
    ) -> list[list[float]] | None:
        if not self.cache_path.exists():
            return None
        expected_fingerprint = _chunk_fingerprint(chunks)
        try:
            payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
            if (
                payload.get("version") != _VECTOR_INDEX_VERSION
                or payload.get("model") != self.model_name
                or payload.get("chunk_fingerprint") != expected_fingerprint
                or payload.get("chunk_count") != len(chunks)
            ):
                return None
            dimension = int(payload["dimension"])
            raw = base64.b64decode(payload["vectors"])
            flat = array("f")
            flat.frombytes(raw)
            if len(flat) != len(chunks) * dimension:
                return None
            vectors = [
                list(flat[offset:offset + dimension])
                for offset in range(0, len(flat), dimension)
            ]
            self._vector_fingerprint = expected_fingerprint
            return vectors
        except (OSError, ValueError, TypeError, KeyError):
            logger.warning("RAG vector cache is invalid; using lexical RAG", exc_info=True)
            return None

    def _write_cache(
        self,
        chunks: Sequence[EmbeddableChunk],
        vectors: Sequence[Sequence[float]],
    ) -> None:
        dimension = len(vectors[0]) if vectors else 0
        flat = array("f")
        for vector in vectors:
            if len(vector) != dimension:
                raise ValueError("Embedding vectors have inconsistent dimensions")
            flat.extend(vector)
        payload = {
            "version": _VECTOR_INDEX_VERSION,
            "model": self.model_name,
            "dimension": dimension,
            "chunk_count": len(chunks),
            "chunk_fingerprint": _chunk_fingerprint(chunks),
            "vectors": base64.b64encode(flat.tobytes()).decode("ascii"),
        }
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.cache_path.with_suffix(self.cache_path.suffix + ".tmp")
        temporary_path.write_text(
            json.dumps(payload, separators=(",", ":")),
            encoding="utf-8",
        )
        temporary_path.replace(self.cache_path)

    def ensure_loaded(
        self,
        chunks: Sequence[EmbeddableChunk],
        *,
        force_build: bool = False,
    ) -> bool:
        fingerprint = _chunk_fingerprint(chunks)
        if (
            self._vectors is not None
            and self._vector_fingerprint == fingerprint
        ):
            return True
        with self._lock:
            if (
                self._vectors is not None
                and self._vector_fingerprint == fingerprint
            ):
                return True
            vectors = self._read_cache(chunks)
            if vectors is None and (force_build or self.build_missing):
                vectors = self._embed([chunk.text for chunk in chunks])
                if vectors is not None:
                    self._write_cache(chunks, vectors)
                    self._vector_fingerprint = fingerprint
            if vectors is None:
                return False
            self._vectors = vectors
            self._vector_fingerprint = fingerprint
            return True

    def build(self, chunks: Sequence[EmbeddableChunk]) -> int:
        if self._get_model() is None:
            raise RuntimeError("Unable to load the multilingual embedding model")
        if not self.ensure_loaded(chunks, force_build=True):
            raise RuntimeError("Unable to build the multilingual embedding index")
        return len(self._vectors or ())

    def similarities(
        self,
        query: str,
        chunks: Sequence[EmbeddableChunk],
    ) -> list[float] | None:
        if not self.ensure_loaded(chunks):
            return None
        query_vector = self._embed_query(query)
        if query_vector is None:
            return None
        return [
            sum(left * right for left, right in zip(query_vector, vector))
            for vector in self._vectors or ()
        ]

    def route(self, question: str) -> str | None:
        if self._anchors is None:
            anchor_texts = [
                anchor
                for anchors in _DOMAIN_ANCHORS.values()
                for anchor in anchors
            ]
            vectors = self._embed(anchor_texts)
            if vectors is None:
                return None
            self._anchors = {}
            offset = 0
            for domain, anchors in _DOMAIN_ANCHORS.items():
                self._anchors[domain] = vectors[offset:offset + len(anchors)]
                offset += len(anchors)
        query_vector = self._embed_query(question)
        if query_vector is None:
            return None
        scores = {
            domain: max(
                sum(left * right for left, right in zip(query_vector, anchor))
                for anchor in anchors
            )
            for domain, anchors in self._anchors.items()
        }
        return max(scores, key=scores.get)

