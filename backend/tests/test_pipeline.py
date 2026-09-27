import io

from file_parser import parse_upload
from ml_pipeline import MailMindPipeline, extract_features


def test_healthworthy_pipeline_has_versioned_models():
    pipeline = MailMindPipeline()
    assert pipeline.model_version.startswith("mailmind-classical-")
    metrics = pipeline.bundle.metrics
    # Accept both old flat format and new nested format
    assert "models" in metrics or "logisticRegression" in metrics


def test_legitimate_meeting_has_action_and_entities():
    result = MailMindPipeline().analyze("team@example.test", "Project review tomorrow", "Please confirm the meeting tomorrow at 10am.")
    assert result["category"]["label"] in {"Work", "Meetings"}
    assert result["intent"]["actionRequired"] is True
    assert "tomorrow" in result["entities"]["dates"]


def test_phishing_support_signal_blocks_safe_draft_at_api_boundary_contract():
    result = MailMindPipeline().analyze("notice@unknown.test", "Verify your password immediately", "Login at http://192.168.1.4/reset and enter your password.")
    assert result["phishing"]["probability"] >= 0.68
    assert result["spam"]["label"] in {"Phishing Risk", "Suspicious", "Spam"}


def test_feature_engineering_preserves_urls_and_security_counts():
    features = extract_features("sender@example.test", "Invoice", "Pay $20 at https://example.test now!")
    assert features["urlCount"] == 1
    assert features["currencyCount"] == 1
    assert features["exclamationCount"] == 1


def test_supported_file_parser_reads_text_and_rejects_unknown_extensions():
    parsed = parse_upload("note.txt", b"Subject: Hello\n\nA short message")
    assert len(parsed) == 1
    assert parsed[0]["subject"] == "Hello"
    assert "A short message" in parsed[0]["body"]
    try:
        parse_upload("run.exe", b"unsafe")
    except ValueError as exc:
        assert "Unsupported" in str(exc)
    else:
        raise AssertionError("unsupported extension should be rejected")


def test_text_file_with_multiple_emails_splits_into_separate_records():
    text = (
        "From: alice@example.com\nSubject: Standup update\n\nAll good on my end.\n"
        "\n---\n\n"
        "From: bob@example.com\nSubject: Invoice\n\nPlease pay by Friday."
    )
    parsed = parse_upload("bundle.txt", text.encode())
    assert len(parsed) == 2
    subjects = {p["subject"] for p in parsed}
    assert subjects == {"Standup update", "Invoice"}
    assert "pay" in parsed[1]["body"].lower()


def test_text_file_splits_on_repeated_from_headers_without_delimiter():
    text = (
        "From: a@x.com\nSubject: One\n\nBody one.\n"
        "From: b@x.com\nSubject: Two\n\nBody two."
    )
    parsed = parse_upload("stack.txt", text.encode())
    assert len(parsed) == 2
    assert parsed[0]["sender"].endswith("a@x.com")


def test_csv_file_produces_one_record_per_row():
    csv_bytes = b"sender,subject,body\nalice@example.com,Hi,Please review\nbob@example.com,Invoice,Pay by Friday $200\n"
    parsed = parse_upload("emails.csv", csv_bytes)
    assert len(parsed) == 2
    assert parsed[0]["sender"] == "alice@example.com"
    assert parsed[1]["subject"] == "Invoice"


def test_csv_file_missing_required_columns_is_rejected():
    try:
        parse_upload("emails.csv", b"foo,bar\n1,2\n")
    except ValueError as exc:
        assert "column" in str(exc).lower()
    else:
        raise AssertionError("CSV without subject/body columns must fail")