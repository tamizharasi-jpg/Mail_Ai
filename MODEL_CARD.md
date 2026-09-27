# MailMind baseline model card

**Version:** `mailmind-classical-v1.0`  
**Feature version:** `features-v1.0`  
**Intended use:** decision support for a user reviewing pasted or uploaded emails.  
**Not intended for:** automatic deletion, automatic link opening, attachment execution, or declaring a sender malicious.

The baseline was trained from a small transparent seed corpus to keep the demo reproducible. It is subject to domain shift, class imbalance, ambiguous short messages, and dataset bias. Probabilities are model estimates. The app explicitly separates spam from phishing-support risk and labels uncertain messages for review.

## Safety

Email content is treated as untrusted input. File extraction does not execute attachments. The LLM receives structured evidence and a delimited email excerpt, cannot override the core labels, and is prevented from drafting replies for Spam, Suspicious, or Phishing Risk classifications.

## Monitoring plan

The API stores model version, feature version, timestamp, low-confidence outcomes, class distribution, and user corrections. Future iterations should monitor drift, calibration, false positives, and correction rates before retraining.