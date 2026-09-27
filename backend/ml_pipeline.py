"""MailMind's reproducible classical ML + feature engineering pipeline.

The spam classifier uses the pre-trained model from ``models/best_spam_model.joblib``
(trained on the UCI SMS Spam Collection via ``scripts/train_models.py``).  If the
serialized model is unavailable, the pipeline falls back to a small seed corpus so
the API can always start.
"""
from __future__ import annotations

import html
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB

logger = logging.getLogger("mailmind.pipeline")

_MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
_SPAM_MODEL_PATH = _MODEL_DIR / "best_spam_model.joblib"
_METRICS_PATH = _MODEL_DIR / "training_metrics.json"


SPAM_TRAINING = [
    ("Congratulations you have won a cash prize claim your reward now", "spam"),
    ("You have been selected for a free gift click to claim", "spam"),
    ("Limited offer buy now and save money today", "spam"),
    ("Your account qualifies for an exclusive bonus act immediately", "spam"),
    ("Earn money from home with this amazing opportunity", "spam"),
    ("Winner notification urgent claim your lottery payment", "spam"),
    ("Get cheap loans no credit check apply online", "spam"),
    ("Final notice your reward expires today", "spam"),
    ("Team standup is moved to tomorrow at ten", "ham"),
    ("Please review the attached project plan before our meeting", "ham"),
    ("Your interview is scheduled for next Tuesday", "ham"),
    ("Thanks for sending the quarterly report", "ham"),
    ("The invoice for this month is ready in the finance portal", "ham"),
    ("Can we catch up for coffee this weekend", "ham"),
    ("Your travel booking confirmation is attached", "ham"),
    ("Please confirm your availability for the client call", "ham"),
    ("The course enrollment deadline is Friday", "ham"),
    ("Your support case has been updated by our service team", "ham"),
    ("Here are the notes from today's planning session", "ham"),
]

CATEGORY_TRAINING = [
    ("project roadmap sprint planning team deliverables", "Work"),
    ("client review business meeting agenda colleagues", "Work"),
    ("happy birthday family dinner this weekend", "Personal"),
    ("checking in hope you are doing well", "Personal"),
    ("bank account statement transfer payment", "Banking"),
    ("credit card payment due account security", "Banking"),
    ("invoice receipt tax balance due", "Finance"),
    ("budget forecast quarterly expenses", "Finance"),
    ("course assignment lecture exam university", "Education"),
    ("class registration scholarship campus", "Education"),
    ("job interview resume recruiter application", "Career"),
    ("career opportunity hiring position application", "Job"),
    ("calendar invite meeting appointment schedule", "Meetings"),
    ("doctor appointment consultation tomorrow", "Appointments"),
    ("order shipped delivery tracking package", "Shopping"),
    ("cart sale product discount store", "Shopping"),
    ("flight hotel booking itinerary travel", "Travel"),
    ("customer support ticket resolution help", "Customer Support"),
    ("newsletter promotion special offer campaign", "Marketing"),
    ("monthly bill payment due statement", "Bills"),
]

INTENT_TRAINING = [
    ("please confirm your attendance", "Confirm"),
    ("let me know if you can join", "Attend"),
    ("please review and approve the document", "Approve"),
    ("send the completed form before Friday", "Submit"),
    ("please pay the outstanding invoice", "Pay"),
    ("can you reply with your availability", "Reply"),
    ("schedule a call next week", "Schedule"),
    ("please provide the requested information", "Provide information"),
    ("follow up on the open request", "Follow up"),
    ("here is an update for your records", "No action"),
]


def clean_nlp_text(text: str) -> str:
    """Clean prose while preserving security indicators in separate features."""
    soup = BeautifulSoup(text or "", "html.parser")
    without_html = soup.get_text(" ")
    without_html = html.unescape(without_html)
    return re.sub(r"\s+", " ", without_html).strip().lower()


def extract_features(sender: str, subject: str, body: str) -> dict[str, Any]:
    raw = f"{subject}\n{body}"
    urls = re.findall(r"https?://[^\s<>\]\)]+|www\.[^\s<>\]\)]+", raw, re.I)
    domains = re.findall(r"(?:https?://|www\.)?([a-z0-9.-]+\.[a-z]{2,})", " ".join(urls), re.I)
    email_addresses = re.findall(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", raw, re.I)
    suspicious_terms = re.findall(
        r"\b(password|credential|verify|login|reset|account suspended|wire transfer|urgent|immediately|gift card)\b",
        raw,
        re.I,
    )
    shortened = [u for u in urls if re.search(r"bit\.ly|tinyurl|t\.co|goo\.gl|is\.gd", u, re.I)]
    ip_urls = [u for u in urls if re.search(r"https?://(?:\d{1,3}\.){3}\d{1,3}", u, re.I)]
    sender_domain = sender.lower().split("@")[-1].strip(" >") if "@" in sender else ""
    body_words = re.findall(r"\b\w+\b", body)
    upper = sum(char.isupper() for char in raw)
    special = sum(not char.isalnum() and not char.isspace() for char in raw)
    return {
        "emailLength": len(body),
        "subjectLength": len(subject),
        "wordCount": len(body_words),
        "urlCount": len(urls),
        "externalDomainCount": len(set(domains)),
        "emailAddressCount": len(email_addresses),
        "uppercaseRatio": round(upper / max(len(raw), 1), 3),
        "specialCharacterCount": special,
        "exclamationCount": raw.count("!"),
        "questionCount": raw.count("?"),
        "currencyCount": len(re.findall(r"[$€£]|\b(?:usd|eur|gbp)\b", raw, re.I)),
        "htmlElementCount": len(BeautifulSoup(body or "", "html.parser").find_all()),
        "suspiciousTermCount": len(suspicious_terms),
        "shortenedUrlCount": len(shortened),
        "ipUrlCount": len(ip_urls),
        "urls": urls,
        "senderDomain": sender_domain,
        "securityTerms": sorted(set(t.lower() for t in suspicious_terms)),
    }


@dataclass
class ModelBundle:
    spam_vectorizer: TfidfVectorizer
    spam_model: Any  # Pre-trained model (NB, LR, SVM, RF, etc.)
    category_vectorizer: TfidfVectorizer
    category_model: LogisticRegression
    intent_vectorizer: TfidfVectorizer
    intent_model: LogisticRegression
    metrics: dict[str, Any]


class MailMindPipeline:
    model_version = "mailmind-classical-v2.0"
    feature_version = "features-v1.0"

    def __init__(self) -> None:
        self.bundle = self._train()

    def _load_pretrained_spam(self) -> tuple[TfidfVectorizer, Any, dict[str, Any]] | None:
        """Try to load the serialized model trained on the full dataset."""
        if not _SPAM_MODEL_PATH.exists():
            return None
        try:
            bundle = joblib.load(_SPAM_MODEL_PATH)
            vectorizer = bundle["vectorizer"]
            model = bundle["model"]
            model_name = bundle.get("model_name", "unknown")
            metrics: dict[str, Any] = {}
            if _METRICS_PATH.exists():
                metrics = json.loads(_METRICS_PATH.read_text(encoding="utf-8"))
            logger.info("Loaded pre-trained spam model: %s", model_name)
            return vectorizer, model, metrics
        except Exception as exc:
            logger.warning("Could not load pre-trained model (%s), falling back to seed corpus.", exc)
            return None

    def _train(self) -> ModelBundle:
        # --- Spam model: prefer pre-trained, fallback to seed ---
        pretrained = self._load_pretrained_spam()
        if pretrained:
            spam_vectorizer, spam_model, comparison = pretrained
        else:
            spam_text, spam_labels = zip(*SPAM_TRAINING)
            spam_vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
            X = spam_vectorizer.fit_transform(spam_text)
            spam_model = LogisticRegression(max_iter=500, class_weight="balanced", random_state=7)
            spam_model.fit(X, spam_labels)
            baseline = MultinomialNB().fit(X, spam_labels)
            y_true = list(spam_labels)
            y_pred = spam_model.predict(X)
            comparison = {
                "logisticRegression": self._metrics(y_true, y_pred),
                "naiveBayes": self._metrics(y_true, baseline.predict(X)),
                "evaluationNote": "Seed-corpus diagnostic metrics. Run scripts/train_models.py for held-out evaluation.",
            }

        # --- Category and intent: lightweight seed classifiers ---
        cat_text, cat_labels = zip(*CATEGORY_TRAINING)
        cat_vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        cat_model = LogisticRegression(max_iter=600, random_state=7).fit(cat_vectorizer.fit_transform(cat_text), cat_labels)
        intent_text, intent_labels = zip(*INTENT_TRAINING)
        intent_vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        intent_model = LogisticRegression(max_iter=600, random_state=7).fit(intent_vectorizer.fit_transform(intent_text), intent_labels)
        return ModelBundle(spam_vectorizer, spam_model, cat_vectorizer, cat_model, intent_vectorizer, intent_model, comparison)

    @staticmethod
    def _metrics(y_true: list[str], y_pred: list[str]) -> dict[str, float]:
        return {"accuracy": round(accuracy_score(y_true, y_pred), 3), "precision": round(precision_score(y_true, y_pred, pos_label="spam", zero_division=0), 3), "recall": round(recall_score(y_true, y_pred, pos_label="spam", zero_division=0), 3), "f1": round(f1_score(y_true, y_pred, pos_label="spam", zero_division=0), 3)}

    def analyze(self, sender: str, subject: str, body: str) -> dict[str, Any]:
        combined = clean_nlp_text(f"{subject} {body}")
        features = extract_features(sender, subject, body)
        vector = self.bundle.spam_vectorizer.transform([combined])
        spam_probability = float(self.bundle.spam_model.predict_proba(vector)[0][list(self.bundle.spam_model.classes_).index("spam")])
        phishing_probability = self._phishing_probability(features, sender, body)
        category_vector = self.bundle.category_vectorizer.transform([combined])
        category_probability = float(max(self.bundle.category_model.predict_proba(category_vector)[0]))
        category = str(self.bundle.category_model.predict(category_vector)[0])
        intent_vector = self.bundle.intent_vectorizer.transform([combined])
        intent_probability = float(max(self.bundle.intent_model.predict_proba(intent_vector)[0]))
        intent = str(self.bundle.intent_model.predict(intent_vector)[0])
        priority, priority_probability, priority_reasons = self._priority(features, combined, intent)
        if phishing_probability >= 0.68:
            label, risk = "Phishing Risk", "high"
        elif spam_probability >= 0.70:
            label, risk = "Spam", "high"
        elif phishing_probability >= 0.42 or 0.55 <= spam_probability <= 0.70:
            label, risk = "Suspicious", "medium"
        elif spam_probability <= 0.45:
            label, risk = "Legitimate", "low"
        else:
            label, risk = "Needs Review", "medium"
        entities = self._entities(sender, subject, body, features)
        explanation = self._explanation(features, spam_probability, phishing_probability, label)
        action_required = intent != "No action" and label not in {"Spam", "Phishing Risk"}
        return {
            "spam": {"label": label, "probability": round(spam_probability, 3), "riskLevel": risk},
            "phishing": {"risk": "high" if phishing_probability >= 0.68 else "medium" if phishing_probability >= 0.42 else "low", "probability": round(phishing_probability, 3)},
            "category": {"label": category if label not in {"Spam", "Phishing Risk"} else "Security", "probability": round(category_probability, 3)},
            "priority": {"label": priority, "probability": round(priority_probability, 3), "reasons": priority_reasons},
            "intent": {"label": intent, "actionRequired": action_required, "confidence": round(intent_probability, 3)},
            "entities": entities,
            "features": {k: v for k, v in features.items() if k not in {"urls"}},
            "explanation": explanation,
            "modelVersion": self.model_version,
            "featureVersion": self.feature_version,
            "metrics": self.bundle.metrics,
            "nlp": {"cleanTextPreview": combined[:240], "tokens": len(combined.split())},
        }

    @staticmethod
    def _phishing_probability(features: dict[str, Any], sender: str, body: str) -> float:
        score = 0.04 + min(features["urlCount"] * 0.08, 0.24) + min(features["suspiciousTermCount"] * 0.10, 0.35)
        score += min(features["shortenedUrlCount"] * 0.16, 0.24) + min(features["ipUrlCount"] * 0.22, 0.34)
        if "@" in sender and features["urls"]:
            sender_domain = sender.lower().split("@")[-1].strip(" >")
            if not any(sender_domain in url.lower() for url in features["urls"]):
                score += 0.12
        if re.search(r"\b(password|credential|login|verify identity)\b", body, re.I):
            score += 0.14
        return min(round(score, 3), 0.99)

    @staticmethod
    def _priority(features: dict[str, Any], text: str, intent: str) -> tuple[str, float, list[str]]:
        score = 0.20
        reasons: list[str] = []
        if intent in {"Pay", "Approve", "Submit"}:
            score += 0.20; reasons.append("A concrete decision or transaction is requested")
        if intent in {"Attend", "Schedule", "Confirm"}:
            score += 0.14; reasons.append("A time-bound coordination action is requested")
        if re.search(r"\b(deadline|due|expires|interview|today|tomorrow|this week)\b", text):
            score += 0.18; reasons.append("Time context suggests the message may need attention soon")
        if features["currencyCount"] or re.search(r"\binvoice|payment|bank\b", text):
            score += 0.15; reasons.append("Financial context increases consequence of delay")
        if not reasons:
            reasons.append("No strong time-bound or consequential action signal detected")
        score = min(score, 0.96)
        label = "Critical" if score >= 0.82 else "High" if score >= 0.62 else "Medium" if score >= 0.40 else "Low" if score >= 0.25 else "Informational"
        return label, score, reasons

    @staticmethod
    def _entities(sender: str, subject: str, body: str, features: dict[str, Any]) -> dict[str, list[str]]:
        amounts = re.findall(r"(?:[$€£]\s?\d[\d,.]*|\b\d[\d,.]*\s?(?:USD|EUR|GBP)\b)", body, re.I)
        dates = re.findall(r"\b(?:today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b", body, re.I)
        phones = re.findall(r"\+?\d[\d\s().-]{7,}\d", body)
        return {"people": [sender] if sender else [], "organizations": [features["senderDomain"]] if features["senderDomain"] else [], "dates": sorted(set(dates)), "amounts": sorted(set(amounts)), "phoneNumbers": sorted(set(phones)), "urls": features["urls"]}

    @staticmethod
    def _explanation(features: dict[str, Any], spam: float, phishing: float, label: str) -> list[dict[str, str]]:
        factors: list[dict[str, str]] = []
        if features["urlCount"]: factors.append({"type": "security", "direction": "risk", "text": f"{features['urlCount']} link(s) were detected in the message"})
        if features["suspiciousTermCount"]: factors.append({"type": "security", "direction": "risk", "text": "Credential, urgency, or payment language influenced the risk assessment"})
        if features["shortenedUrlCount"] or features["ipUrlCount"]: factors.append({"type": "security", "direction": "risk", "text": "A shortened or IP-based link pattern needs careful review"})
        if features["htmlElementCount"] > 3: factors.append({"type": "structure", "direction": "risk", "text": "Rich HTML structure contributed a small security signal"})
        if not factors: factors.append({"type": "model", "direction": "support", "text": "No prominent link, credential, or unusual structure signal was detected"})
        factors.append({"type": "model", "direction": "support", "text": f"The trained TF-IDF classifier estimated {round(spam * 100)}% spam probability"})
        if label == "Phishing Risk": factors.append({"type": "safety", "direction": "risk", "text": f"Supporting phishing checks estimated {round(phishing * 100)}% risk; this is not proof of malicious intent"})
        return factors