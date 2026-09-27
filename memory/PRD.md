# MailMind AI — Product Requirements

## What it does
MailMind AI is an Expo mobile app + FastAPI backend that runs an actual NLP + classical ML pipeline over uploaded or pasted emails and returns spam/phishing risk, category, priority, intent, entities, explainability factors, and (for legitimate mail only) a response recommendation and draft.

## Current capabilities
- Animated cursor-grid launch screen with a Start button (no auth).
- Adaptive light/dark theme sourced from `src/theme.ts`.
- Analyze email by:
  - Pasting sender/subject/body, OR
  - Uploading files. Supported: `.eml`, `.txt`, `.pdf`, `.docx`, `.csv`.
- **Multi-email files**: a single `.txt` can contain multiple emails separated by `From:` headers, mbox `From ` lines, or `---` / `===` / `***` separators — each block is analyzed as its own record. A `.csv` becomes one analysis per row.
- Batch upload up to 50 files with live progress showing file count and total emails processed.
- ML pipeline (`backend/ml_pipeline.py`): TF-IDF + Logistic Regression for spam & category, a compared MultinomialNB baseline, TF-IDF + LR intent classifier, plus feature-engineered phishing scoring and a transparent priority scoring function.
- Explainability: model factor list per prediction plus a diagnostic metrics block on the record.
- Suspicious/Spam/Phishing Risk records never produce a suggested response; instead they surface a safety recommendation.
- Backend-only Emergent LLM (`gpt-5.4`) is used purely as a readability layer on top of structured ML evidence; falls back to deterministic assistance when the key is unavailable.
- History, natural-language search over subject/sender, filters (all / priority / phishing / action), analytics summary endpoint, human-in-the-loop feedback persistence.

## Endpoints
- `GET /api/health`
- `POST /api/email/analyze` — paste analysis
- `POST /api/email/analyze-file` — single file (returns `{items, errors, completed, total, summary}`; a multi-email file produces multiple `items`)
- `POST /api/email/analyze-batch` — multi-file upload
- `GET /api/email/history` — search + status filter
- `GET /api/email/{id}` — detail
- `POST /api/email/{id}/feedback` — human corrections (validated, 404 on missing id)
- `GET /api/analytics/summary`

## Tests
`cd /app/backend && python -m pytest tests/test_pipeline.py` — 9 passing tests covering pipeline versioning, legitimate/phishing behavior, feature engineering, and file-parser support for text, multi-email text, CSV rows, and unsupported extensions.

## Known limitations
- ML models train on a small bundled corpus; training metrics in the response are diagnostic, not held-out benchmarks. A licensed public dataset is still required for reportable ROC-AUC / PR-AUC numbers.
- No authentication (per user direction). Records are scoped by a generated `client_id` stored on device.
