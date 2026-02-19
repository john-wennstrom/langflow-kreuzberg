# Kreuzberg Metadata Schema

This document is the canonical reference for Langflow `Data.data` payload keys used
across the Kreuzberg component bundle.

## DocumentSource

Produced by loader components.

| Key | Type | Required | Description |
|---|---|---|---|
| `bytes` | `bytes` | yes (or `path`/`url`) | Raw file bytes for local extraction |
| `path` | `str` | no | Source file path when loaded from disk |
| `url` | `str` | no | Source URL when loaded remotely |
| `filename` | `str` | yes | Display/source filename |
| `mime` | `str` | yes | MIME type, inferred or overridden |
| `source_id` | `str` | yes | Deterministic id (`hash_id(filename, content_hash)`) |
| `source_uri` | `str \| None` | no | Original URI/path if available |

## ExtractedDocument

Produced by extraction components.

| Key | Type | Required | Description |
|---|---|---|---|
| `text` | `str` | yes | Extracted text content |
| `metadata` | `dict` | yes | Metadata dictionary preserving source keys |
| `tables` | `list[dict] \| None` | no | Structured table extraction output |
| `images` | `list[dict] \| None` | no | Image extraction output |
| `pages` | `list[Data] \| None` | no | Per-page extracted content when enabled |

## Chunk

Produced by chunking components.

| Key | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | yes | Deterministic chunk id |
| `text` | `str` | yes | Chunk text |
| `metadata` | `dict` | yes | Inherited and chunk-specific metadata |
| `page` | `int \| None` | no | Page number for page-aligned chunking |
| `offset_start` | `int \| None` | no | Start character offset |
| `offset_end` | `int \| None` | no | End character offset |


### ExtractedDocument metadata keys

| Key | Type | Description |
|---|---|---|
| `source_id` | `str` | Deterministic source identifier from loader stage |
| `filename` | `str` | Original source filename |
| `mime` | `str` | Source MIME type |
| `page_count` | `int` | Number of pages emitted by extractor |
| `ocr_used` | `bool` | Whether OCR path was used |
| `ocr_backend` | `str \| None` | OCR backend name when OCR is used |
| `format` | `str` | Output format requested (`text`, `markdown`, `structured`) |
| `page_number` | `int` | Present in per-page metadata when page tracking is enabled |

## Shared helper semantics

- `normalize_to_list(data_or_list)` returns `[]` for `None`, otherwise a list.
- `ensure_metadata_dict(data)` always returns a dictionary, default `{}`.
- `hash_id(*parts)` uses SHA256 and returns first 32 hex characters.
- `merge_metadata(base, extra, policy)` supports `overwrite`, `keep`, `raise`.
