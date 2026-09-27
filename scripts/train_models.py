"""
MailMind Model Training & Evaluation
=====================================
Trains four classical ML classifiers on the SMS Spam Collection training split,
tunes hyper-parameters on validation, and reports final held-out metrics on the
test split.

Models compared
---------------
1. Multinomial Naive Bayes
2. Logistic Regression
3. Random Forest
4. Linear SVM (SGDClassifier with hinge loss)

Metrics reported
----------------
Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, and confusion matrix — all
computed on the **held-out test set only**.

Outputs
-------
models/training_metrics.json – Full metrics report
models/confusion_matrices.json – Confusion matrices for every model
models/best_spam_model.joblib – Serialized best model + vectorizer
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
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
from sklearn.naive_bayes import MultinomialNB

ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = ROOT / "data" / "train" / "train.csv"
VAL_PATH = ROOT / "data" / "validation" / "validation.csv"
TEST_PATH = ROOT / "data" / "test" / "test.csv"
MODEL_DIR = ROOT / "models"

RANDOM_STATE = 42


def load_split(path: Path) -> tuple[list[str], list[str]]:
    df = pd.read_csv(path)
    return df["text"].tolist(), df["label"].tolist()


def compute_metrics(y_true: list[str], y_pred: list[str], y_prob: np.ndarray | None, pos_label: str = "spam") -> dict:
    """Compute full classification metrics."""
    labels = sorted(set(y_true))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    metrics = {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, pos_label=pos_label, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, pos_label=pos_label, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, pos_label=pos_label, zero_division=0), 4),
        "confusion_matrix": {
            "labels": labels,
            "matrix": cm.tolist(),
            "true_negatives": int(cm[0][0]),
            "false_positives": int(cm[0][1]),
            "false_negatives": int(cm[1][0]),
            "true_positives": int(cm[1][1]),
        },
    }
    if y_prob is not None:
        binary_true = [1 if y == pos_label else 0 for y in y_true]
        metrics["roc_auc"] = round(roc_auc_score(binary_true, y_prob), 4)
        metrics["pr_auc"] = round(average_precision_score(binary_true, y_prob), 4)
    return metrics


def train_and_evaluate() -> None:
    print("=" * 60)
    print("MailMind Model Training & Evaluation")
    print("=" * 60)

    # -----------------------------------------------------------
    # 1. Load data splits
    # -----------------------------------------------------------
    print("\n[1/5] Loading data splits...")
    X_train, y_train = load_split(TRAIN_PATH)
    X_val, y_val = load_split(VAL_PATH)
    X_test, y_test = load_split(TEST_PATH)
    print(f"  Train: {len(X_train):,}  Val: {len(X_val):,}  Test: {len(X_test):,}")

    # -----------------------------------------------------------
    # 2. TF-IDF vectorization
    # -----------------------------------------------------------
    print("\n[2/5] Fitting TF-IDF vectorizer on training data...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
        max_features=15000,
        strip_accents="unicode",
        lowercase=True,
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_val_tfidf = vectorizer.transform(X_val)
    X_test_tfidf = vectorizer.transform(X_test)
    print(f"  Vocabulary size: {len(vectorizer.vocabulary_):,}")
    print(f"  Feature matrix shape: {X_train_tfidf.shape}")

    # -----------------------------------------------------------
    # 3. Define and train models
    # -----------------------------------------------------------
    print("\n[3/5] Training models...")
    models = {
        "multinomial_naive_bayes": MultinomialNB(alpha=0.1),
        "logistic_regression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE, C=1.0
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1
        ),
        "linear_svm": SGDClassifier(
            loss="modified_huber",  # gives probability estimates
            class_weight="balanced",
            random_state=RANDOM_STATE,
            max_iter=1000,
            tol=1e-3,
        ),
    }

    results = {}
    val_results = {}
    best_model_name = None
    best_val_f1 = -1.0

    for name, model in models.items():
        print(f"\n  Training {name}...")
        model.fit(X_train_tfidf, y_train)

        # Validation set evaluation (for model selection)
        y_val_pred = model.predict(X_val_tfidf)
        if hasattr(model, "predict_proba"):
            y_val_prob = model.predict_proba(X_val_tfidf)[:, list(model.classes_).index("spam")]
        else:
            y_val_prob = None

        val_metrics = compute_metrics(y_val, y_val_pred, y_val_prob)
        val_results[name] = val_metrics
        val_f1 = val_metrics["f1"]

        print(f"    Validation — Acc: {val_metrics['accuracy']:.4f}  P: {val_metrics['precision']:.4f}  R: {val_metrics['recall']:.4f}  F1: {val_f1:.4f}", end="")
        if "roc_auc" in val_metrics:
            print(f"  ROC-AUC: {val_metrics['roc_auc']:.4f}", end="")
        print()

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_model_name = name

    print(f"\n  Best model on validation (by F1): {best_model_name} (F1={best_val_f1:.4f})")

    # -----------------------------------------------------------
    # 4. Final test set evaluation
    # -----------------------------------------------------------
    print("\n[4/5] Evaluating all models on held-out test set...")
    for name, model in models.items():
        y_test_pred = model.predict(X_test_tfidf)
        if hasattr(model, "predict_proba"):
            y_test_prob = model.predict_proba(X_test_tfidf)[:, list(model.classes_).index("spam")]
        else:
            y_test_prob = None

        test_metrics = compute_metrics(y_test, y_test_pred, y_test_prob)
        test_metrics["validation_metrics"] = val_results[name]
        results[name] = test_metrics

        is_best = " ★ BEST" if name == best_model_name else ""
        print(f"\n  {name}{is_best}")
        print(f"    Test — Acc: {test_metrics['accuracy']:.4f}  P: {test_metrics['precision']:.4f}  R: {test_metrics['recall']:.4f}  F1: {test_metrics['f1']:.4f}", end="")
        if "roc_auc" in test_metrics:
            print(f"  ROC-AUC: {test_metrics['roc_auc']:.4f}  PR-AUC: {test_metrics['pr_auc']:.4f}", end="")
        print()
        cm = test_metrics["confusion_matrix"]
        print(f"    Confusion: TN={cm['true_negatives']}  FP={cm['false_positives']}  FN={cm['false_negatives']}  TP={cm['true_positives']}")

        # Print sklearn classification report for test set
        print(f"\n    Classification Report:")
        report = classification_report(y_test, y_test_pred, target_names=sorted(set(y_test)))
        for line in report.split("\n"):
            print(f"      {line}")

    # -----------------------------------------------------------
    # 5. Save results and best model
    # -----------------------------------------------------------
    print("\n[5/5] Saving artifacts...")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Full metrics report
    report_data = {
        "dataset": {
            "source": "UCI SMS Spam Collection v1",
            "url": "https://archive.ics.uci.edu/dataset/228/sms+spam+collection",
            "license": "CC BY 4.0",
            "total_messages": len(X_train) + len(X_val) + len(X_test),
            "train_size": len(X_train),
            "validation_size": len(X_val),
            "test_size": len(X_test),
            "split_ratio": "70/15/15",
            "stratified": True,
            "random_state": RANDOM_STATE,
        },
        "vectorizer": {
            "type": "TfidfVectorizer",
            "ngram_range": [1, 2],
            "max_features": 15000,
            "vocabulary_size": len(vectorizer.vocabulary_),
            "sublinear_tf": True,
        },
        "best_model": best_model_name,
        "models": results,
        "evaluation_note": "All test metrics are computed on a held-out 15% stratified test split never seen during training or validation.",
    }
    metrics_path = MODEL_DIR / "training_metrics.json"
    metrics_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    print(f"  Metrics: {metrics_path}")

    # Serialize best model
    best_model = models[best_model_name]
    bundle_path = MODEL_DIR / "best_spam_model.joblib"
    joblib.dump({"vectorizer": vectorizer, "model": best_model, "model_name": best_model_name}, bundle_path)
    print(f"  Best model: {bundle_path}")

    print("\nTraining and evaluation complete.")


if __name__ == "__main__":
    train_and_evaluate()
