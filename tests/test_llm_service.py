import pytest

from app.exceptions import LLMServiceError
from app.services import llm_service


def test_get_client_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        'app.services.llm_service.get_settings',
        lambda: type('S', (), {'openai_api_key': None, 'openai_model': 'gpt-4o-mini'})(),
    )

    with pytest.raises(LLMServiceError) as exc_info:
        llm_service._get_client()

    assert exc_info.value.status_code == 503
    assert 'OPENAI_API_KEY' in exc_info.value.detail
