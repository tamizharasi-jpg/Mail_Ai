# MailMind AI architecture

The Expo mobile client sends pasted or safely extracted email text to the FastAPI API. The API normalizes the message, extracts security and metadata features, runs trained classical NLP models, adds transparent phishing-support signals, and persists a versioned analysis in MongoDB. The managed backend-only LLM is a final readability layer for summaries and drafts; it cannot overwrite the structured model output and is disabled for unsafe response drafting.

```text
Paste / .eml / .txt / PDF / DOCX
        ↓
Safe extraction + HTML cleaning
        ↓
TF-IDF word n-grams + metadata/security features
        ↓
Spam model | category model | intent model | priority score
        ↓
Phishing supporting checks + feature factors
        ↓
Backend-only LLM summary/recommendation
        ↓
MongoDB history + mobile detail view
```

The first release intentionally has no account wall. Each installation uses an anonymous client id so history remains isolated per device, while authentication can be added later without changing the analysis contract.