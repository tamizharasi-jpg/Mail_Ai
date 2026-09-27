# MailMind AI data layout

`raw/`, `processed/`, `train/`, `validation/`, and `test/` are reserved for licensed dataset exports.

The runtime baseline is deliberately small and reproducible: the training examples in `raw/seed_emails.csv` are used by `backend/ml_pipeline.py` to fit a TF-IDF + Logistic Regression spam classifier and compare it with Multinomial Naive Bayes. They are not a substitute for a held-out public corpus. For a capstone evaluation, add a licensed SpamAssassin, Enron, or SMS Spam Collection export and run the documented training/evaluation commands without committing private email content.