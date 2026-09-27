# API documentation

Base URL: `/api`

## `POST /email/analyze`

Accepts `{ "sender": "", "subject": "", "body": "", "client_id": "device-id" }`. Returns the saved record with spam, phishing, category, priority, intent, entities, explanations, feature metadata, model versions, summary, recommendation, and optional suggested response.

## `POST /email/analyze-file`

Multipart form field `file`; query `client_id`. Supported file extensions: `.eml`, `.txt`, `.pdf`, `.docx`; maximum size is 8 MB. Attachments are metadata only and are never executed.

## `POST /email/analyze-batch`

Multipart `files` (up to 50) and query `client_id`. Returns completed items, per-file errors, and counts for spam, high priority, and action-required messages.

## `GET /email/history`

Query `client_id`, optional `search`. Returns the most recent saved records with MongoDB `_id` excluded from the response.

## `POST /email/{id}/feedback`

Accepts `{ "client_id": "device-id", "field": "spam|category|priority|intent", "corrected_value": "..." }` and stores a human-in-the-loop correction.

## `GET /health`

Reports API, pipeline, model version, and whether the backend LLM key is configured.