# MailMind Model Card

**Version:** `mailmind-classical-v2.0`  
**Feature version:** `features-v1.0`  
**Intended use:** Decision support for a user reviewing pasted or uploaded emails.  
**Not intended for:** Automatic deletion, automatic link opening, attachment execution, or declaring a sender malicious.

## Training Data

| Property | Value |
|----------|-------|
| Dataset | UCI SMS Spam Collection v1 |
| License | CC BY 4.0 |
| Total messages (post-cleaning) | 5,158 |
| Training split | 3,610 (70%) |
| Validation split | 774 (15%) |
| Test split | 774 (15%) |
| Stratification | Yes (preserves ~12.4% spam ratio in all splits) |

## Model Performance (Held-Out Test Set)

| Metric | Multinomial NB | Logistic Regression | Random Forest | Linear SVM |
|--------|:-:|:-:|:-:|:-:|
| Accuracy | 0.9832 | 0.9832 | 0.9845 | **0.9871** |
| Precision | **0.9882** | 0.9192 | **1.0000** | 0.9300 |
| Recall | 0.8750 | 0.9479 | 0.8750 | **0.9688** |
| F1 | 0.9282 | 0.9333 | 0.9333 | **0.9490** |
| ROC-AUC | 0.9917 | **0.9978** | 0.9976 | 0.9878 |
| PR-AUC | 0.9761 | **0.9868** | 0.9849 | 0.9781 |

### Confusion Matrix (Best Test F1: Linear SVM)

|  | Predicted Ham | Predicted Spam |
|--|:-:|:-:|
| **Actual Ham** | 671 (TN) | 7 (FP) |
| **Actual Spam** | 3 (FN) | 93 (TP) |

False positive rate: 1.03% · False negative rate: 3.13%

## Limitations and Risks

- **Domain shift**: Trained on SMS messages; may not perfectly generalize to formal email content.
- **Class imbalance**: ~87:13 ham:spam ratio. Handled via `class_weight='balanced'` but rare spam types may be missed.
- **Ambiguous messages**: Short, context-dependent messages may receive uncertain classifications.
- **No ground-truth for priority**: Priority scoring uses transparent rules, not a trained classifier.
- **Phishing is a supporting signal**: The phishing risk score combines multiple heuristics; it cannot prove malicious intent.

## Safety Design

- Email content is treated as **untrusted input** — never executed.
- File extraction does not run embedded scripts or macros.
- The LLM receives structured evidence and a delimited email excerpt; it **cannot override** core ML labels.
- **Spam/Suspicious/Phishing Risk** classifications prevent auto-generated response drafts.
- Probabilities and risk labels include explicit uncertainty language.

## Monitoring

The API persists for every analysis:
- Model version and feature version
- Prediction timestamp
- Classification probabilities and confidence scores
- Low-confidence outcomes flagged for review
- User correction feedback (spam/category/priority/intent)

Future iterations should monitor calibration drift, false positive/negative trends, and correction rates before retraining.

## Reproducibility

```bash
python scripts/prepare_dataset.py   # Download, clean, split
python scripts/train_models.py      # Train 4 models, evaluate, save best
python scripts/evaluate_models.py   # Re-evaluate on test set
```

All scripts use `random_state=42`.
