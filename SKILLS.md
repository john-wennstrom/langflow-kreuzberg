# SKILLS — Kreuzberg Langflow Component Bundle

> Required skill areas and working standards for implementing the Kreuzberg Langflow Component Bundle with SurrealDB integration.

---

## Skill 1 — Langflow Component Development

> **Non-negotiable rule: NEVER stub Langflow imports or types. Every component must use real Langflow library classes. No placeholder types, no `Any`-typed workarounds, no `# TODO: replace with real type` comments. If a class exists in `lfx.io` or `lfx.schema`, use it.**

### Real imports — always use these exact paths

```python
# Base class (Langflow 1.7+)
from lfx.custom.custom_component.component import Component
# Backwards-compatible alias still works:
# from langflow.custom import Component

# All input types live here — import only what you use
from lfx.io import (
    StrInput,
    MultilineInput,
    BoolInput,
    IntInput,
    FloatInput,
    DropdownInput,
    FileInput,
    CodeInput,
    DataInput,
    MessageInput,
    MessageTextInput,
    HandleInput,
    ModelInput,
    Output,
)

# Return/schema types
from lfx.schema import Data, DataFrame, Message
from lfx.schema.message import Message          # chat-compatible output
from langflow.field_typing import Embeddings    # for embedding outputs
```

> If you are not sure which package exposes a type, check the installed langflow package directly — **do not stub it**. Run `python -c "from lfx.io import StrInput; print('ok')"` to verify.

---

### Complete component anatomy

Every component is a Python class that:
1. Inherits from `Component`
2. Declares class-level metadata attributes
3. Declares `inputs: list[...]` using real input classes from `lfx.io`
4. Declares `outputs: list[Output]` where each `Output.method` names a real method on the class
5. Implements those methods with correct return-type annotations

```python
from typing import Optional
from lfx.custom.custom_component.component import Component
from lfx.io import StrInput, BoolInput, DropdownInput, Output
from lfx.schema import Data, Message


class KreuzbergExampleComponent(Component):
    """One-line description shown as tooltip in the Langflow UI."""

    # --- Metadata (all required) ---
    display_name: str = "Kreuzberg Example"
    description: str = "Extracts text from a document using Kreuzberg."
    documentation: str = "https://github.com/your-org/kreuzberg-langflow"
    icon: str = "file-text"          # Any Lucide icon name: https://lucide.dev/icons
    name: str = "KreuzbergExample"   # Unique internal identifier; defaults to class name

    # --- Inputs ---
    inputs = [
        StrInput(
            name="file_path",
            display_name="File Path",
            info="Absolute path to the document to process.",
            required=True,
        ),
        DropdownInput(
            name="ocr_backend",
            display_name="OCR Backend",
            options=["tesseract", "paddle", "easyocr"],
            value="tesseract",
            info="OCR engine to use when the document has no embedded text.",
            advanced=True,
        ),
        BoolInput(
            name="include_metadata",
            display_name="Include Metadata",
            value=True,
            advanced=True,
        ),
    ]

    # --- Outputs ---
    outputs = [
        Output(
            name="document_data",
            display_name="Document Data",
            method="extract_document",   # must match the method name below
        ),
    ]

    # --- Output method (name MUST match Output.method above) ---
    def extract_document(self) -> Data:
        """Runs Kreuzberg extraction and returns a Data object."""
        # Access inputs as self.<input_name>
        path: str = self.file_path
        backend: str = self.ocr_backend
        include_meta: bool = self.include_metadata

        try:
            # Real logic — no stubs
            from kreuzberg import extract_file   # actual kreuzberg call
            result = extract_file(path, ocr_backend=backend)
            payload = {"text": result.text, "page_count": result.page_count}
            if include_meta:
                payload["metadata"] = result.metadata
            self.status = f"Extracted {result.page_count} pages from {path}"
            return Data(data=payload)
        except Exception as exc:
            raise ValueError(f"Extraction failed for '{path}': {exc}") from exc
```

---

### Input types reference

Use **exactly** these classes — never roll your own or replace with `str`/`Any`:

| Class | Use case | Key params |
|---|---|---|
| `StrInput` | Single-line text | `name`, `display_name`, `required`, `info`, `value` |
| `MultilineInput` | Multi-line / prompt text | same as StrInput |
| `BoolInput` | True/false toggle | `value=True/False` |
| `IntInput` | Integer number | `value`, `min`, `max` |
| `FloatInput` | Float number | `value`, `min`, `max` |
| `DropdownInput` | Fixed-option select | `options: list[str]`, `value` |
| `FileInput` | File upload | `file_types: list[str]` e.g. `[".pdf"]` |
| `DataInput` | Receives a `Data` object from another node | — |
| `MessageInput` | Receives a full `Message` object | — |
| `MessageTextInput` | Receives just the text of a message | `tool_mode=True` to support agent use |
| `HandleInput` | Typed handle for specific LangChain types | `input_types=["BaseRetriever"]` |

**Common shared parameters** (available on all input classes):
- `required: bool` — whether the field must be filled
- `advanced: bool` — hides field under the "Advanced" section; keep ≤5 inputs visible by default
- `info: str` — tooltip shown in the UI
- `value` — default value
- `dynamic: bool` — marks the field as controlled by `update_build_config`
- `real_time_refresh: bool` — triggers `update_build_config` immediately on change
- `show: bool` — initial visibility (use with `dynamic=True`)

---

### Output types reference

Annotate every output method's return type — Langflow uses annotations for port color-coding and connection validation:

```python
# Chat-compatible message
def build_message(self) -> Message:
    return Message(text="Hello from component", sender="System", sender_name=self.display_name)

# Flexible structured data (dict-like)
def build_data(self) -> Data:
    return Data(data={"key": "value", "score": 0.95})

# List of Data objects (e.g. chunks)
def build_chunks(self) -> list[Data]:
    return [Data(data={"text": chunk}) for chunk in chunks]

# Tabular data
def build_df(self) -> DataFrame:
    import pandas as pd
    return DataFrame(pd.DataFrame({"col": [1, 2, 3]}))

# Embedding vectors
def build_embeddings(self) -> Embeddings:
    return embeddings_list   # list[list[float]]
```

> **Never return plain `dict`, `list`, or `str` from output methods** — always wrap in `Data`, `Message`, or `DataFrame`. This ensures ports connect correctly in the visual editor.

---

### Multiple outputs

```python
outputs = [
    Output(name="chunks",     display_name="Chunks",     method="build_chunks"),
    Output(name="embeddings", display_name="Embeddings", method="build_embeddings"),
]
```

By default Langflow groups multiple outputs into one selectable port. To expose all outputs as **separate simultaneous ports** (parallel paths), set `group_outputs=True` on each:

```python
outputs = [
    Output(name="passed", display_name="Passed", method="route_pass", group_outputs=True),
    Output(name="failed", display_name="Failed", method="route_fail", group_outputs=True),
]
```

---

### Dynamic fields

Use `dynamic=True` + `real_time_refresh=True` to conditionally show/hide fields based on user selections. Implement `update_build_config` to control which fields are visible:

```python
inputs = [
    DropdownInput(
        name="mode",
        display_name="Mode",
        options=["fast", "accurate", "ocr"],
        value="fast",
        real_time_refresh=True,
    ),
    StrInput(
        name="ocr_language",
        display_name="OCR Language",
        value="eng",
        dynamic=True,
        show=False,          # hidden until mode == "ocr"
        advanced=True,
    ),
]

def update_build_config(self, build_config: dict, field_value: str, field_name: str | None = None) -> dict:
    if field_name == "mode":
        build_config["ocr_language"]["show"] = (field_value == "ocr")
        build_config["ocr_language"]["required"] = (field_value == "ocr")
    return build_config
```

---

### Execution hooks and shared state

```python
def _pre_run_setup(self) -> None:
    """Called once before output methods run. Use for one-time init."""
    self._client = build_my_client()

# Share data between multiple output methods in the same run:
def first_output(self) -> Data:
    self.ctx["intermediate"] = compute_something()
    return Data(data=self.ctx["intermediate"])

def second_output(self) -> Data:
    val = self.ctx.get("intermediate", {})
    return Data(data={"summary": summarize(val)})
```

---

### Error handling — three patterns

```python
# 1. Raise to halt with a user-visible error (preferred for bad inputs)
def process(self) -> Data:
    if not self.file_path:
        raise ValueError("File Path is required. Please provide a path to your document.")

# 2. Return error in Data to let the flow continue (preferred for recoverable errors)
def process(self) -> Data:
    try:
        result = risky_operation()
        return Data(data={"result": result})
    except Exception as exc:
        return Data(data={"error": str(exc), "file": self.file_path})

# 3. Stop a specific output path only (other outputs still run)
def process(self) -> Data:
    if not self.user_input.strip():
        self.stop("process")
        return Data(data={"error": "Empty input"})
```

**Status and logging:**
```python
self.status = "Processed 42 chunks"     # shows in component badge in UI
self.log(f"Processing file: {path}")    # appears in component Logs panel
```

---

### Tool mode (agent integration)

Set `tool_mode=True` on inputs to allow the component to be used as a tool by Agent nodes:

```python
inputs = [
    MessageTextInput(
        name="query",
        display_name="Query",
        info="The search query to process.",
        tool_mode=True,
    ),
]
```

---

### File layout and discovery

```
components/kreuzberg/
├── __init__.py                  # REQUIRED — must export all components
├── extractor.py
├── chunker.py
├── embedder.py
└── surreal_upsert.py
```

**`__init__.py` must explicitly export every component:**

```python
# components/kreuzberg/__init__.py
from .extractor import KreuzbergExtractor
from .chunker import KreuzbergChunker
from .embedder import KreuzbergEmbedder
from .surreal_upsert import SurrealDBUpsert

__all__ = [
    "KreuzbergExtractor",
    "KreuzbergChunker",
    "KreuzbergEmbedder",
    "SurrealDBUpsert",
]
```

To load components from a custom path, set the environment variable:
```
LANGFLOW_COMPONENTS_PATH=/path/to/components
```

Or pass `--components-path` to the CLI:
```bash
langflow run --components-path ./components
```

---

### Competency checklist — a correct component MUST

- [ ] Import from `lfx.io` and `lfx.schema` (not stubs, not `Any`)
- [ ] Inherit from `Component` (not a mock or base class stub)
- [ ] Have `display_name`, `description`, `icon`, `name` class attributes
- [ ] Access all input values via `self.<input_name>` in output methods
- [ ] Return typed objects (`Data`, `Message`, `DataFrame`, `Embeddings`) — never raw dicts
- [ ] Have `Output.method` match an actual method on the class
- [ ] Use `self.status` and `self.log()` for UI feedback
- [ ] Keep ≤5 inputs visible by default; rest under `advanced=True`
- [ ] Never contain `# stub`, `pass`, `...`, or `raise NotImplementedError` in output methods
- [ ] Be exported from `__init__.py`

---

## Skill 2 — Kreuzberg Adapters

**You must be able to:**
- Translate Kreuzberg capabilities into modular adapter classes (extraction, OCR, chunking, embeddings, keyword extraction, batching, plugins)
- Wrap all Kreuzberg calls behind a stable adapter boundary — no leaking internals
- Convert Kreuzberg outputs to canonical Langflow `Data` schemas
- Catch all library exceptions and re-raise as `KreuzbergComponentError` subtypes with actionable hints

**Competency indicator:** Can enforce schema stability and add backward-compatible fields without breaking existing flows.

---

## Skill 3 — Embeddings + Vector Store Plumbing

**You must be able to:**
- Generate embeddings for `list[Data]` chunks and output `Embeddings`
- Guarantee `embeddings[i]` always corresponds to `chunks[i]`
- Implement deterministic ID mapping and full metadata preservation
- Implement vector-store contracts: upsert with deterministic/content-hash IDs, similarity search returning scored `list[Data]`, optional metadata filtering
- Handle batching, caching (with cache-key strategy), and optional L2 normalization

**Competency indicator:** Can write tests verifying vector alignment and ID stability across runs.

---

## Skill 4 — SurrealDB Integration

**You must be able to:**
- Insert and upsert embedding records alongside chunk metadata into SurrealDB
- Implement similarity search with scored results and optional metadata filters
- Handle connection config via environment variables (never hardcoded credentials)
- Write parameterized SurrealQL queries with proper error handling and retries

**Competency indicator:** Can design a namespace/table/index layout for vectors + metadata at scale.

---

## Skill 5 — Testing + Quality Engineering

**You must be able to:**
- Write `pytest` unit tests covering: happy path, empty input, invalid types, missing optional dependencies, deterministic output (IDs, ordering, token counts)
- Write integration tests for: Extract→Chunk→Embed, Embed→SurrealDB Upsert, Query→Similarity Search→Ranked Results
- Use committed fixtures (small PDF, DOCX, PNG, HTML — < 100 KB total)

**Competency indicator:** Uses fixtures and `monkeypatch`/`unittest.mock` effectively; avoids flaky tests.

---

## Secondary Skills (Nice to Have)

| Area | Key Points |
|------|-----------|
| **OCR & Doc Pipelines** | Tesseract/PaddleOCR/EasyOCR tradeoffs; importable guard pattern for optional deps |
| **Performance** | Thread vs. process pool; cache key strategies; token estimation without full models |
| **Security** | No `eval`/`exec`; safe file upload (size limits, MIME validation); SSRF awareness; secrets in env vars only |

---

## Working Standards (Non-Negotiable)

| Standard | Rule |
|----------|------|
| **No Stubs** | Output methods must contain real logic. `pass`, `...`, and `raise NotImplementedError` are forbidden in production components |
| **Real Imports** | Always use `lfx.io`, `lfx.schema`, and `lfx.custom` — never create fake base classes or type aliases to work around missing imports |
| **Schema Stability** | Never silently rename/remove metadata keys; add new key alongside old, document in `docs/metadata_schema.md` |
| **Determinism** | Chunk IDs and ordering must be identical for identical input + settings; embeddings align 1:1 with chunks |
| **Defensive Normalization** | Components accepting `Data or list[Data]` must call `normalize_to_list()` internally; empty input → structured result with warning, never unhandled exception |
| **User-Friendly Errors** | Zero raw tracebacks in Langflow UI; every error states **what** failed, **why**, and **what to do** |
| **Component UX** | ≤5 basic inputs visible; advanced inputs in collapsible group; port names/types consistent across all bundle nodes |

---

## PR Review Checklist

**Component correctness**
- [ ] Imports are from `lfx.io`, `lfx.schema`, `lfx.custom` — no stubs or mocks
- [ ] Inputs/outputs match the contracts documented in the issue
- [ ] Handles both single `Data` and `list[Data]` where specified; uses `normalize_to_list()`
- [ ] Preserves original metadata; sets deterministic IDs on output
- [ ] `len(embeddings) == len(chunks)` enforced and tested (embedding components)
- [ ] All errors are readable with actionable hints
- [ ] `self.status` set after successful execution
- [ ] Component is exported from `__init__.py`

**Tests**
- [ ] Unit tests: happy path, empty input, invalid type, common failure
- [ ] Fixtures small (< 100 KB), committed to `tests/fixtures/`
- [ ] At least one integration test added/updated for the changed path
- [ ] No `time.sleep()` or random delays

**Docs**
- [ ] Component class has a docstring (shown in Langflow UI tooltip)
- [ ] `docs/metadata_schema.md` updated if metadata keys added/changed
- [ ] Sample flow JSON updated if wiring or port names changed

---

## Agent Profiles

| Profile | Focus |
|---------|-------|
| **Langflow Component Engineer** | Component UI/ports/types, `display_name`/`icon`/`inputs`/`outputs`, dynamic fields, schema normalization, sample flows |
| **Kreuzberg Adapter Engineer** | Extraction/OCR/processing adapters, error taxonomy, caching hooks |
| **Embeddings + Vector Store Engineer** | Embeddings generation, ordering guarantees, batching, SurrealDB upsert/search |
| **QA / Reliability Engineer** | Tests, fixtures, determinism checks, integration tests, performance smoke |

Issues labeled `agent:langflow-engineer`, `agent:kreuzberg-adapter`, `agent:vector-store`, or `agent:qa`.

---

## Quickstart for New Agents

1. Read `AGENT.md` for project conventions and overall architecture
2. Run `python -c "from lfx.io import StrInput, Output; from lfx.schema import Data, Message; print('imports ok')"` to confirm your environment is set up correctly before writing any code
3. Find the closest existing component; copy its structural pattern (class attributes, inputs/outputs, advanced field grouping)
4. Implement adapter/utility logic in shared modules (`kreuzberg_utils.py`, `kreuzberg_errors.py`) — not inside component classes
5. Write tests for shape/order/ID stability **before** implementing functionality
6. Update: `components/kreuzberg/__init__.py`, `docs/metadata_schema.md` (if keys changed), sample flow JSON (if wiring changed)

**Done** = discoverable in Langflow UI with correct display name and docstring, composable with adjacent nodes, tested with committed fixtures (unit + integration), and all PR checklist items checked.
