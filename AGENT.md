# AGENT.md — Kreuzberg Langflow Component Bundle

> **For:** Claude, GitHub Copilot, OpenAI Codex, or any AI coding agent
> implementing issues in this repository.
>
> Read this document in full before touching any code. It contains the
> conventions, architecture decisions, and quality requirements needed to
> produce correct, reviewable output on the first attempt.

---

## Project in One Sentence

Build a suite of Langflow custom component nodes that wrap **Kreuzberg**
document-processing capabilities (extraction, OCR, chunking, embeddings,
post-processing) and integrate seamlessly with **SurrealDB** as a vector store.

---

## Repository Layout

```
components/
  kreuzberg/
    __init__.py              # register all components here
    kreuzberg_types.py       # TypedDicts / dataclasses for schemas
    kreuzberg_utils.py       # shared helpers (normalize, hash_id, merge_metadata)
    kreuzberg_errors.py      # KreuzbergComponentError + subclasses
    kreuzberg_cache.py       # CacheBackend + RunReport
    nodes/
      file_loader.py         # Issue 1.1
      bytes_loader.py        # Issue 1.2
      extract.py             # Issue 2.1
      batch_extract.py       # Issue 2.3
      quality_processing.py  # Issue 3.1
      language_detection.py  # Issue 3.2
      token_reduction.py     # Issue 3.3
      keyword_extraction.py  # Issue 3.4
      chunker.py             # Issue 4.1
      chunker_page_safe.py   # Issue 4.2
      embeddings.py          # Issue 5.1
      embedding_router.py    # Issue 5.2
      surrealdb_store.py     # Issue 6.1
      surrealdb_adapter.py   # Issue 6.2
      post_processor.py      # Issue 7.2
      validator.py           # Issue 7.3
      http_extract.py        # Issue 8.1
      mcp_caller.py          # Issue 8.2
      rag_prep.py            # Issue 9.1

tests/
  fixtures/                  # small PDF, DOCX, PNG, HTML (< 100 KB total)
  unit/                      # per-component unit tests
  integration/               # end-to-end pipeline tests

flows/
  flow_single_ingest.json
  flow_batch_ingest.json
  flow_query_retrieve.json

docs/
  metadata_schema.md
  ocr_setup.md
  caching.md
  surrealdb_integration.md
  gotchas.md

README.md
SKILLS.md
AGENT.md                     # this file
```

---

## Canonical Data Contracts

Every component exchanges **Langflow `Data` objects**. The keys below are
the only keys that should be set at each stage. Do not invent new top-level
keys without updating `docs/metadata_schema.md`.

### DocumentSource (output of loader components)
```python
{
  "bytes": bytes,          # raw file bytes
  "filename": str,         # original filename
  "mime": str,             # MIME type
  "source_id": str,        # hash_id(filename, sha256(bytes))
  "source_uri": str | None # original path or URL
}
```

### ExtractedDocument (output of extraction components)
```python
{
  "text": str,                     # extracted text
  "metadata": {
    "source_id": str,
    "filename": str,
    "mime": str,
    "page_count": int | None,
    "ocr_used": bool,
    "ocr_backend": str | None,
    "extraction_duration_ms": int,
    "format": str,                 # "text" | "markdown" | "structured"
  },
  "tables": list[dict] | None,
  "images": list[dict] | None,
  "pages": list[Data] | None       # only if page_tracking=True
}
```

### Chunk (output of chunking components)
```python
{
  "text": str,
  "id": str,               # hash_id(source_id, offset_start, offset_end, chunk_index)
  "metadata": {
    "source_id": str,
    "filename": str,
    "chunk_index": int,
    "chunk_total": int,
    "offset_start": int,
    "offset_end": int,
    "page": int | None,
    # ...inherits all parent doc metadata
  }
}
```

### EmbeddingRecord (optional output of embeddings component)
```python
{
  "id": str,               # == chunk.id
  "vector": list[float],
  "text": str,
  "metadata": dict         # == chunk.metadata
}
```

---

## Shared Utilities You Must Use

All utilities live in `kreuzberg_utils.py`. **Do not re-implement these inline.**

```python
from kreuzberg.kreuzberg_utils import (
    normalize_to_list,    # (data_or_list) -> list[Data]
    ensure_metadata_dict, # (data) -> dict
    hash_id,              # (*parts: str) -> str  (SHA256, hex, first 32 chars)
    merge_metadata,       # (base, extra, policy="overwrite"|"keep"|"raise") -> dict
)
```

---

## Error Handling Rules

1. **Never let a raw library exception reach the Langflow UI.**
2. Always wrap extraction calls in `try/except` and re-raise as the correct
   `KreuzbergComponentError` subclass.
3. Every exception must have a `hint` property:
   ```python
   raise OCRBackendMissingError(
       "Tesseract not found on PATH.",
       hint="Install with: apt-get install tesseract-ocr  or  brew install tesseract",
   )
   ```
4. Error subclasses (all in `kreuzberg_errors.py`):
   - `UnsupportedFormatError`
   - `OCRBackendMissingError`
   - `CorruptDocumentError`
   - `ExtractionTimeoutError`
   - `RemoteExtractionError`

---

## Implementing a Component — Step-by-Step

Follow this exact sequence for every new component:

### Step 1 — Read the issue
Read the GitHub issue carefully. Note the exact input names, types, defaults,
and the acceptance criteria. These are your spec.

### Step 2 — Find a comparable existing Langflow component
Look in the Langflow source for a component with similar behavior
(e.g., a file loader, a chunker, an embedder). Copy its structural pattern:
- Class declaration + `display_name`, `description`, `icon`
- `inputs = [...]` list with `Input(...)` objects
- `outputs = [...]` list with `Output(...)` objects
- `build(self, ...)` method signature matching output order

### Step 3 — Write tests first (TDD)
Before implementing, write tests in `tests/unit/test_<component>.py`:
```python
def test_happy_path(): ...
def test_empty_input(): ...
def test_invalid_type(): ...
def test_id_is_deterministic(): ...
```
Use fixtures from `tests/fixtures/` — never generate random content in tests.

### Step 4 — Implement the component
- Place logic in `nodes/<component>.py`
- Heavy lifting (API calls, processing) goes in the adapter layer, not in
  the component class `build()` method
- `build()` should: validate inputs → call adapter → normalize outputs → return

### Step 5 — Register the component
Add the class to `components/kreuzberg/__init__.py`:
```python
from .nodes.my_component import MyComponent
__all__ = [..., "MyComponent"]
```

### Step 6 — Update docs
- Add any new metadata keys to `docs/metadata_schema.md`
- Update component docstring (it appears as tooltip in Langflow UI)
- Update a sample flow JSON if wiring changed

---

## Input/Output Naming Conventions

| Concept | Input name | Output name |
|---------|-----------|-------------|
| Single document | `document_source` | `document` |
| Multiple documents | `document_sources` | `documents` |
| Chunks | `chunks` | `chunks` |
| Embeddings | `embeddings` | `embeddings` |
| Passthrough chunks (embed node) | — | `chunks_passthrough` |
| Operation report | — | `run_report` / `batch_report` / `chunking_report` |
| Search results | — | `search_results` |

Use these names consistently across **all** components. Never use abbreviations
like `docs` (conflicts with Python built-in), `embs`, or `src`.

---

## Determinism Requirements

These are not optional — tests will fail if you skip them:

| What | Requirement |
|------|-------------|
| `hash_id(*parts)` | Must return identical output for identical args, forever |
| Chunk IDs | Must be identical on second run with same input + settings |
| Chunk ordering | Must be identical on second run (no sets, no dict iteration) |
| `embeddings[i]` | Must always correspond to `chunks[i]` — assert in tests |
| Batch output order | Must match input order (not completion order) |

---

## SurrealDB Connection Config

Connection parameters come from environment variables. Never accept raw
credentials as component inputs visible in the UI.

```
SURREALDB_URL=ws://localhost:8000/rpc
SURREALDB_USER=root
SURREALDB_PASS=root
SURREALDB_NAMESPACE=default
SURREALDB_DATABASE=default
```

The component should read these at `build()` time using `os.environ.get()`
and raise a clear `KreuzbergComponentError` if required vars are missing.

---

## Caching Pattern

Use the shared `CacheBackend` from `kreuzberg_cache.py`:

```python
cache = CacheBackend(cache_dir=self.cache_dir, enabled=self.enable_cache)
key = hash_id("embeddings", model_name, chunk.id)
cached = cache.get(key)
if cached is not None:
    vector = json.loads(cached)
else:
    vector = embed_one(chunk.text)
    cache.set(key, json.dumps(vector).encode())
```

Always report cache hits/misses in `RunReport`.

---

## Advanced / Basic Input Split Rules

**Basic (always visible, ≤ 5 inputs):**
- The primary data input (document, chunks, etc.)
- The most important behavior selector (strategy, model, format)
- Size / count parameter (chunk_size, batch_size, top_k)

**Advanced (collapsed by default):**
- OCR backend, OCR languages
- Cache settings (cache_dir, enable_cache)
- Concurrency, timeouts, retries
- Toggle flags that most users won't need (extract_tables, pdf_hierarchy, etc.)
- ID strategy, metadata filter overrides

In Langflow, use `advanced=True` on `Input(...)` objects for advanced fields.

---

## What Good Output Looks Like

### ✅ Correct: adapter handles extraction, component orchestrates
```python
# nodes/extract.py
class KreuzbergExtractComponent(Component):
    def build(self, document_source: Data, ...) -> Data:
        adapter = ExtractionAdapter(ocr_mode=self.ocr_mode, ...)
        try:
            result = adapter.extract(document_source)
        except Exception as exc:
            raise map_kreuzberg_error(exc)
        return normalize_extracted(result)
```

### ❌ Wrong: raw Kreuzberg call inside build(), no error mapping
```python
def build(self, document_source: Data, ...) -> Data:
    result = kreuzberg.extract(document_source.data["bytes"])  # crashes raw
    return Data(data={"text": result.text})  # loses metadata
```

---

## Testing Reference

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run integration tests (requires SurrealDB or mocks)
pytest tests/integration/ -v

# Run a specific test file
pytest tests/unit/test_chunker.py -v

# Check linting
ruff check components/ tests/

# Type check
mypy components/kreuzberg/ --strict
```

---

## Common Mistakes to Avoid

1. **Iterating a `dict` and expecting stable order** — use `list` for ordered collections
2. **Using `data.data.get("text")` without `ensure_metadata_dict`** — metadata may be None
3. **Forgetting to register the component** in `__init__.py` — it won't appear in Langflow
4. **Hardcoding model names or cache paths** — always expose as configurable inputs
5. **Putting heavy imports at module level** — use lazy imports inside `build()` for
   optional dependencies (OCR backends) so the component loads even when they're absent
6. **Not testing the empty list case** — `normalize_to_list([])` must return `[]` and
   components must handle it without error
7. **Logging credentials** — never log `SURREALDB_PASS`, auth tokens, or file contents
8. **Assuming `metadata` is a dict** — always call `ensure_metadata_dict(data)` first

---

## Milestone → Issue Dependency Order

Implement milestones in order. Do not start M2 until M1 is complete.

```
M1 Foundation      → 0.1, 0.2, 1.1, 2.1
M2 Core Pipeline   → 4.1, 4.2, 5.1
M3 SurrealDB       → 5.2, 6.1, 6.2
M4 Pipeline Flows  → 9.1, 9.2
M5 Batch+OCR       → 0.3, 2.2, 2.3
M6 Adv. Processing → 3.1, 3.2, 3.3, 3.4, 7.1, 7.2, 7.3
M7 Remote/MCP      → 1.2, 8.1, 8.2
M8 Hardening       → 10.1, 10.2
```

---

## Definition of Done (Per Issue)

An issue is **Done** — not "Done except tests" — only when all of the following are true:

- [ ] Component class implemented in `nodes/<name>.py`
- [ ] Registered in `components/kreuzberg/__init__.py`
- [ ] Unit tests pass: happy path, empty input, invalid type, ID determinism
- [ ] At least one integration test updated or added for the changed path
- [ ] `ruff check .` passes
- [ ] `mypy components/kreuzberg/ --strict` passes (or existing mypy baseline not worsened)
- [ ] Component docstring present and descriptive (shown in Langflow UI)
- [ ] `docs/metadata_schema.md` updated if any metadata keys were changed
- [ ] PR description includes the issue checklist from SKILLS.md
