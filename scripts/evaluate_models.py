"""
MailMind Model Evaluation (Standalone)
======================================
Loads the saved best model and evaluates on the held-out test set.
Useful for re-running evaluation without retraining.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = ROOT / "data" / "test" / "test.csv"
MODEL_PATH = ROOT / "models" / "best_spam_model.joblib"
METRICS_PATH = ROOT / "models" / "training_metrics.json"


def main() -> None:
    print("=" * 60)
    print("MailMind Model Evaluation")
    print("=" * 60)

    # Load test data
    df = pd.read_csv(TEST_PATH)
    X_test = df["text"].tolist()
    y_test = df["label"].tolist()
    print(f"Test set: {len(X_test):,} messages")

    # Load model
    bundle = joblib.load(MODEL_PATH)
    vectorizer = bundle["vectorizer"]
    model = bundle["model"]
    model_name = bundle["model_name"]
    print(f"Model: {model_name}")

    # Transform and predict
    X_tfidf = vectorizer.transform(X_test)
    y_pred = model.predict(X_tfidf)

    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_tfidf)[:, list(model.classes_).index("spam")]
    else:
        y_prob = None

    # Metrics
    cm = confusion_matrix(y_test, y_pred, labels=["ham", "spam"])
    print(f"\nAccuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred, pos_label='spam'):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred, pos_label='spam'):.4f}")
    print(f"F1:        {f1_score(y_test, y_pred, pos_label='spam'):.4f}")
    if y_prob is not None:
        binary = [1 if y == "spam" else 0 for y in y_test]
        print(f"ROC-AUC:   {roc_auc_score(binary, y_prob):.4f}")
        print(f"PR-AUC:    {average_precision_score(binary, y_prob):.4f}")

    print(f"\nConfusion Matrix:")
    print(f"  TN={cm[0][0]}  FP={cm[0][1]}")
    print(f"  FN={cm[1][0]}  TP={cm[1][1]}")

    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["ham", "spam"]))

    # Load and display full saved metrics
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text())
        print("Full metrics report available at:", METRICS_PATH)
        print(f"Best model: {metrics.get('best_model', 'unknown')}")
        print(f"Dataset: {metrics.get('dataset', {}).get('source', 'unknown')}")


if __name__ == "__main__":
    main()
