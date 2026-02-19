# SKILLS — Kreuzberg Langflow Component Bundle

> Required skill areas and working standards for implementing the Kreuzberg Langflow Component Bundle with SurrealDB integration.

---

## Skill 1 — Langflow Component Development

**Component anatomy** — every component inherits from `Component` and defines:
- Class attributes: `display_name`, `description`, `icon` (Lucide name), `name`
- `inputs: list[...]` using typed input classes (`StrInput`, `BoolInput`, `DropdownInput`, `FileInput`, `MultilineInput`)
- `outputs: list[Output]` — each `Output` specifies `name`, `display_name`, and `method`
- One or more methods named in `Output.method` that implement and return output values

**Return types** — annotate consistently; prefer structured types over primitives:
- `Data` for single documents, `list[Data]` for collections/chunks
- `Message` for chat-oriented outputs, `Embeddings` for vector outputs
- Wrap primitives in `Data` or `Message` for visual editor consistency

**Dynamic fields** — use `dynamic=True` + `real_time_refresh=True` on inputs to trigger `update_build_config()`, which can toggle `show`, `required`, `advanced`, and `options` based on user selections.

**Advanced UX** — keep ≤5 inputs visible by default; group power-user settings under `advanced=True`. Use `self.log()` for debug output and `self.status` to surface execution feedback in the UI.

**Error handling** — three patterns:
1. Raise `ValueError` / `ToolException` to halt with an error message
2. Return `Data(data={"error": str(e)})` to continue flow execution
3. `self.stop("output_name")` to halt a specific output path only

**Tool mode** — set `tool_mode=True` on inputs to enable agent-integrated usage.

**File layout:**
```
components/kreuzberg/
├── __init__.py      # must import and expose all components
└── my_component.py
```

**Competency indicators:**
- Can replicate structural conventions from an existing component
- Avoids: type mismatches, list-vs-single normalization bugs, hidden state between runs

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
| **Schema Stability** | Never silently rename/remove metadata keys; add new key alongside old, document in `docs/metadata_schema.md` |
| **Determinism** | Chunk IDs and ordering must be identical for identical input + settings; embeddings align 1:1 with chunks |
| **Defensive Normalization** | Components accepting `Data or list[Data]` must call `normalize_to_list()` internally; empty input → structured result with warning, never unhandled exception |
| **User-Friendly Errors** | Zero raw tracebacks in Langflow UI; every error states **what** failed, **why**, and **what to do** |
| **Component UX** | ≤5 basic inputs visible; advanced inputs in collapsible group; port names/types consistent across all bundle nodes |

---

## PR Review Checklist

**Component correctness**
- [ ] Inputs/outputs match the contracts documented in the issue
- [ ] Handles both single `Data` and `list[Data]` where specified; uses `normalize_to_list()`
- [ ] Preserves original metadata; sets deterministic IDs on output
- [ ] `len(embeddings) == len(chunks)` enforced and tested (embedding components)
- [ ] All errors are readable with actionable hints

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
2. Find the closest existing component; copy its structural pattern (class attributes, inputs/outputs, advanced field grouping)
3. Implement adapter/utility logic in shared modules (`kreuzberg_utils.py`, `kreuzberg_errors.py`) — not inside component classes
4. Write tests for shape/order/ID stability **before** implementing functionality
5. Update: `components/kreuzberg/__init__.py`, `docs/metadata_schema.md` (if keys changed), sample flow JSON (if wiring changed)

**Done** = discoverable in Langflow UI with correct display name and docstring, composable with adjacent nodes, tested with committed fixtures (unit + integration), and all PR checklist items checked.
