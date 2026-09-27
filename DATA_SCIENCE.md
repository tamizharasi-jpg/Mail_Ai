# Data Science Methodology

## Pipeline

Raw email → safe extraction → HTML/text cleaning → security-preserving feature extraction → TF-IDF word n-grams → classical model inference → phishing supporting checks → explainability factors → cautious natural-language assistance.

## Dataset

| Property | Value |
|----------|-------|
| **Name** | UCI SMS Spam Collection v1 |
| **Source** | [archive.ics.uci.edu/dataset/228](https://archive.ics.uci.edu/dataset/228/sms+spam+collection) |
| **License** | CC BY 4.0 |
| **Raw messages** | 5,574 |
| **After dedup/cleaning** | 5,158 |
| **Split** | 70/15/15 stratified (train: 3,610 · val: 774 · test: 774) |
| **Class distribution** | ~87.6% ham, ~12.4% spam |

### Preprocessing

1. **Text cleaning**: HTML tag removal, entity decoding, whitespace normalization, lowercasing.
2. **Security-preserving track**: URLs, domains, currency symbols, phone numbers, suspicious terms, shortened links, and IP-based URLs are extracted separately before text normalization.
3. **Feature engineering**: TF-IDF unigrams + bigrams (`max_features=15,000`, `sublinear_tf=True`) fitted on the training split only. No data leakage — validation and test sets are transformed, never fitted.

## Models

Four classifiers compared on the same TF-IDF feature space:

| Model | Test Accuracy | Test Precision | Test Recall | Test F1 | Test ROC-AUC | Test PR-AUC |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| Multinomial Naive Bayes | 0.9832 | 0.9882 | 0.8750 | 0.9282 | 0.9917 | 0.9761 |
| Logistic Regression | 0.9832 | 0.9192 | 0.9479 | 0.9333 | 0.9978 | 0.9868 |
| Random Forest | 0.9845 | 1.0000 | 0.8750 | 0.9333 | 0.9976 | 0.9849 |
| **Linear SVM (SGD)** | **0.9871** | **0.9300** | **0.9688** | **0.9490** | **0.9878** | **0.9781** |

**Selected model**: Multinomial Naive Bayes (best validation F1). All metrics are computed on the **held-out 15% test split** never seen during training or model selection.

### Additional classifiers

- **Category**: TF-IDF + Logistic Regression on a small labeled seed corpus (20 examples across 12 categories). Suitable for decision support; not benchmarked on a held-out corpus.
- **Intent**: TF-IDF + Logistic Regression on 10 labeled intent examples. Lightweight classifier for action-routing.
- **Priority**: Transparent rule-based decision score (no ground-truth dataset).
- **Phishing risk**: Supporting risk score combining model probability with URL, credential, urgency, sender-domain, shortened-link, and IP-link indicators. Not a standalone classifier.

## Reproducibility

```bash
# 1. Prepare dataset (download, clean, split)
python scripts/prepare_dataset.py

# 2. Train all models and evaluate on held-out test set
python scripts/train_models.py

# 3. Re-evaluate saved model on test set
python scripts/evaluate_models.py
```

All scripts use `random_state=42` for deterministic splits and training.

## Evaluation Limitations

- The SMS Spam Collection is well-studied but contains SMS messages, not full email content. Domain shift may occur with formal business emails.
- Category and intent classifiers use small seed corpora; their metrics are diagnostic only.
- Probabilities are model estimates, not ground-truth certainties.
- The phishing risk score is a supporting signal that should not be interpreted as proof of malicious intent.

## Notebooks

| Notebook | Content |
|----------|---------|
| `01_data_collection.ipynb` | Dataset sourcing, license, schema, integrity checks |
| `02_data_cleaning.ipynb` | Deduplication, null removal, label validation |
| `03_eda.ipynb` | Class distribution, length analysis, URL/punctuation patterns, top terms |
| `04_nlp_preprocessing.ipynb` | Dual-track cleaning strategy, security signal extraction |
| `05_feature_engineering.ipynb` | TF-IDF vectorization, 4-model comparison, confusion matrices, feature importance |
