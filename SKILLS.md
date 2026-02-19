# SKILLS — Kreuzberg Langflow Component Bundle

> This document defines the required skill areas, competency indicators, and
> working standards for agents (human or AI) implementing the Kreuzberg
> Langflow Component Bundle with SurrealDB integration.

---

## Core Skill Areas (Must Have)

### Skill 1 — Langflow Component Development

**You must be able to:**
- Implement custom components using Langflow's standard component base class,
  `inputs`, `outputs`, and `build()` patterns
- Use Langflow data types correctly:
  - `Data` for single documents
  - `list[Data]` for collections (chunks, batch results)
  - `Embeddings` for vector outputs
- Design ports for composability: every component works standalone **and**
  as a pipeline node
- Implement "Advanced settings" UX: keep basic inputs visible, expose power-user
  settings in collapsed/advanced groups
- Export and verify sample Langflow flow JSON files (flows must import and run)

**Competency Indicators:**
- Can read an existing Langflow component and replicate its structural conventions
- Knows how to avoid: type mismatches, list-vs-single normalization bugs,
  hidden state, and side effects between runs

---

### Skill 2 — Kreuzberg Feature Mapping + Adapters

**You must be able to:**
- Translate Kreuzberg capabilities into modular, testable adapter classes:
  extraction, OCR selection, quality processing, chunking, embeddings,
  keyword extraction, token reduction, batch processing, plugins
- Wrap all Kreuzberg calls behind a stable adapter boundary so upstream
  library changes do not break component contracts
- Convert Kreuzberg outputs into canonical Langflow `Data` schemas
- Implement robust error handling: catch all library exceptions and re-raise
  as user-friendly `KreuzbergComponentError` subtypes with actionable hints

**Competency Indicators:**
- Can implement an adapter layer with clear boundaries, no leaking internals
- Can enforce schema stability and add backward-compatible fields

---

### Skill 3 — Embeddings + Vector Store Plumbing

**You must be able to:**
- Generate embeddings for `list[Data]` chunks and output Langflow `Embeddings`
- Guarantee stable ordering: `embeddings[i]` always corresponds to `chunks[i]`
- Implement deterministic ID mapping and full metadata preservation
- Understand vector-store contracts:
  - upsert with deterministic or content-hash IDs
  - similarity search by query embedding returning scored `list[Data]`
  - optional metadata filtering
- Handle batching, caching (with cache-key strategy), and optional L2 normalization

**Competency Indicators:**
- Can write tests that verify vector alignment and ID stability across runs
- Can design SurrealDB table schema and SurrealQL queries for vector search

---

### Skill 4 — SurrealDB Integration (Vector + Metadata)

**You must be able to:**
- Insert and upsert embedding records alongside chunk metadata into SurrealDB
- Implement similarity search with scored results and optional metadata filters
- Handle connection config via environment variables (never hardcoded credentials)
- Write parameterized SurrealQL queries with proper error handling and retries
- Design an index/table strategy for vector + metadata co-location

**Competency Indicators:**
- Can write SurrealDB query code with clear parameterization
- Can design a namespace/table/index layout for vectors + metadata at scale

---

### Skill 5 — Testing + Quality Engineering

**You must be able to:**
- Write `pytest` unit tests for each component covering:
  - happy path
  - empty input (no crash, structured warning)
  - invalid types / bad inputs
  - missing optional dependencies (OCR backend absent)
  - deterministic output checks (IDs, ordering, token counts)
- Write at minimum one integration test per epic:
  - Extract → Chunk → Embed
  - Embed → SurrealDB Upsert
  - Query Embed → Similarity Search → Ranked Results
- Use committed fixtures: small PDF, DOCX, PNG, HTML (< 100 KB total)
- Verify `RunReport` fields for caching and concurrency features

**Competency Indicators:**
- Uses `pytest` fixtures and `monkeypatch` / `unittest.mock` effectively
- Avoids flaky tests: controls randomness, uses deterministic fixtures
- Can write concurrency tests that verify ordering without timing dependencies

---

## Secondary Skill Areas (Nice to Have)

### Skill A — OCR & Document Pipelines
- Familiarity with Tesseract, PaddleOCR, EasyOCR and their language packs
- Understanding of scanned PDF preprocessing and OCR quality tradeoffs
- Gracefully managing optional dependencies (importable guard pattern)

### Skill B — Performance Engineering
- Batch processing concurrency patterns (thread pool vs. process pool)
- Cache key strategies, invalidation policies, and memory pressure management
- Token estimation without loading full models (whitespace approximation)

### Skill C — Security + Deployment Awareness
- Never dynamic code execution (`eval`, `exec`) in hosted environments
- Safe file upload handling: size limits, MIME validation, path traversal prevention
- SSRF considerations for remote fetch components
- Secrets in environment variables, never in logs or error messages

---

## Working Standards (Non-Negotiable)

### Standard 1 — Schema Stability
- Never silently rename or remove metadata keys
- If a key must change:
  1. Add the new key alongside the old key (both present)
  2. Document the change in `docs/metadata_schema.md`
  3. Add a deprecation note and migration path

### Standard 2 — Determinism
- Chunk IDs and their ordering must be identical for identical input + settings
- Embeddings must align 1:1 with input chunks on every run
- Tests must verify both ID stability and ordering explicitly

### Standard 3 — Defensive Normalization
- Every component that says it accepts `Data or list[Data]` must normalize internally
  using `normalize_to_list()` — never assume the caller does it
- Empty text or empty lists must never raise an unhandled exception; return a
  structured result with a warning in metadata

### Standard 4 — User-Friendly Errors
- Zero raw tracebacks in the Langflow UI
- Every error must include:
  - **What** failed (component name, input identifier)
  - **Why** it likely failed (format unsupported, backend missing, network timeout)
  - **What to do** (install hint, config change, file to check)

### Standard 5 — Component UX
- Basic inputs visible by default (no more than 5 in basic mode)
- Advanced inputs grouped under a collapsible "Advanced" section
- Port names and types are consistent with the conventions in this document
  across **all** nodes in the bundle

---

## Review Checklist (Use on Every PR)

### Component Correctness
- [ ] Inputs/outputs match the contracts documented in the issue
- [ ] Handles both single `Data` and `list[Data]` inputs where specified
- [ ] Preserves original metadata and sets deterministic IDs on output
- [ ] `len(embeddings) == len(chunks)` enforced and tested (embedding components)
- [ ] All errors are readable and include actionable hints

### Tests
- [ ] Unit tests cover: happy path, empty input, invalid type, common failure
- [ ] Fixtures are small (< 100 KB each), committed to `tests/fixtures/`
- [ ] At least one integration test added or updated for the changed path
- [ ] No `time.sleep()` or random delays in tests

### Docs
- [ ] Component class has a docstring (shown in Langflow UI tooltip)
- [ ] `docs/metadata_schema.md` updated if any metadata keys were added/changed
- [ ] Sample flow JSON updated if wiring or port names changed

---

## Agent Profiles

| Profile | Focus Areas |
|---------|-------------|
| **Profile 1 — Langflow Component Engineer** | Component UI/ports/types, schema normalization, sample flows, docs |
| **Profile 2 — Kreuzberg Adapter Engineer** | Extraction/OCR/processing adapters, error taxonomy, caching hooks |
| **Profile 3 — Embeddings + Vector Store Engineer** | Embeddings generation, ordering guarantees, batching, SurrealDB upsert/search |
| **Profile 4 — QA / Reliability Engineer** | Tests, fixtures, determinism checks, integration tests, performance smoke |

Issues are labeled `agent:langflow-engineer`, `agent:kreuzberg-adapter`,
`agent:vector-store`, or `agent:qa` to indicate the most relevant profile.

---

## Quickstart for New Agents

1. Read `AGENT.md` for project conventions and overall architecture
2. Locate the closest existing Langflow component with similar behavior and
   copy its structural pattern (inputs/outputs, advanced fields grouping)
3. Implement adapter/utility logic in shared modules (`kreuzberg_utils.py`,
   `kreuzberg_errors.py`), **not** inside component classes
4. Write tests for shape/order/ID stability **before** implementing functionality
5. Finish by updating:
   - `components/kreuzberg/__init__.py` exports
   - `docs/metadata_schema.md` if any keys changed
   - Sample flow JSON if wiring changed
   - Issue checklist in the PR description

---

## Deliverable Quality Bar

A component is considered **Done** only when:
- [ ] Discoverable in the Langflow UI with correct display name and docstring
- [ ] Composable with adjacent nodes using the correct Langflow types
- [ ] Tested with committed fixtures (unit + at least one integration path)
- [ ] Documented well enough that a new user can wire it to SurrealDB without
      reading source code
- [ ] All items in the PR Review Checklist above are checked
