from google.adk.models import Gemini

from helpdesk import config


def test_model_uses_configured_id_and_retry():
    m = config.model()
    assert isinstance(m, Gemini)
    assert m.model == config.MODEL_ID
    assert m.retry_options.attempts == 5
    assert 429 in m.retry_options.http_status_codes


def test_model_id_is_pinned_not_alias():
    assert "latest" not in config.MODEL_ID
