# Data Science methodology

## Pipeline

Raw email → safe extraction → HTML/text cleaning → security-preserving feature extraction → TF-IDF word n-grams → classical model inference → phishing supporting checks → explainability factors → cautious natural-language assistance.

## Data and preprocessing

The runtime baseline uses `data/raw/seed_emails.csv` plus labeled examples in `backend/ml_pipeline.py`. It preserves raw URLs, domains, sender information, currency, dates, uppercase ratio, HTML element count, and suspicious-link patterns while making a separate normalized NLP representation. A future licensed SpamAssassin, Enron, or phishing corpus should be copied into `data/raw/`, deduplicated, stratified into `train/validation/test`, and documented with its license.

## Models

Spam uses TF-IDF word unigrams/bigrams and Logistic Regression with class balancing. Multinomial Naive Bayes is trained as the baseline comparison. Category and intent use replaceable TF-IDF + Logistic Regression classifiers. Priority is a transparent decision-support score because no ground-truth priority dataset is bundled. Phishing is a supporting risk score that combines model output with URL, credential, urgency, sender-domain, shortened-link, and IP-link indicators; it does not claim that any single signal proves maliciousness.

## Evaluation and limitations

`python scripts/evaluate_models.py` prints diagnostic metrics produced by the current training data. Those metrics must not be presented as generalization performance because the seed corpus is small and not a held-out benchmark. Production research work should report accuracy, precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix, false positives, false negatives, calibration, and per-category performance on an unseen, license-compliant test set.

Explainability currently surfaces security/metadata factors and the model probability. SHAP/LIME can be added to the persisted vectorizer/model bundle when a larger benchmark and model monitoring process are available.