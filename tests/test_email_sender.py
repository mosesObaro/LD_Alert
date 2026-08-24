from src.email.sender import EmailSender


def test_email_sender_dry_run():
    sender = EmailSender(provider="console")
    success, msg = sender.send(
        subject="Test Subject",
        html_content="<p>Test</p>",
        text_content="Test",
        to_email="test@example.com",
        dry_run=True
    )
    assert success
    assert "Dry-run" in msg or "completed" in msg


def test_email_sender_missing_key(monkeypatch):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    sender = EmailSender(provider="resend")
    success, msg = sender.send(
        subject="Test",
        html_content="<p>Test</p>",
        text_content="Test",
        to_email="test@example.com",
        dry_run=False
    )
    assert not success
    assert "RESEND_API_KEY" in msg
