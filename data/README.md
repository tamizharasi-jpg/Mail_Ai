# MailMind AI Data Layout

## Dataset: UCI SMS Spam Collection v1

- **Source**: [archive.ics.uci.edu/dataset/228](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)
- **License**: CC BY 4.0
- **Citation**: Almeida, T.A., Gómez Hidalgo, J.M., Yamakami, A. (2011)

## Directory Structure

```
data/
├── raw/
│   ├── SMSSpamCollection       # Original TSV file (5,574 messages)
│   ├── seed_emails.csv         # Small seed corpus for fallback
│   └── readme                  # Dataset original readme
├── processed/
│   └── dataset.csv             # Cleaned, deduplicated (5,158 messages)
├── train/
│   └── train.csv               # 70% stratified split (3,610 messages)
├── validation/
│   └── validation.csv          # 15% stratified split (774 messages)
└── test/
    └── test.csv                # 15% stratified held-out split (774 messages)
```

## Reproducing the Splits

```bash
python scripts/prepare_dataset.py
```

Uses `random_state=42` for deterministic stratified splitting.

## Class Distribution (All Splits)

| Split | Ham | Spam | Spam % |
|-------|----:|-----:|-------:|
| Train | 3,161 | 449 | 12.4% |
| Validation | 677 | 97 | 12.5% |
| Test | 678 | 96 | 12.4% |
