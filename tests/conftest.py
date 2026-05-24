import pytest

from app.mocks import llm_mock
from app.schemas.diagnosis import AreaScores
from app.schemas.llm_outputs import DiagnosisReportStructuredOutput


@pytest.fixture(autouse=True)
def use_llm_mocks_in_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """CI·로컬 테스트 시 OpenAI 호출 없이 결정적 Mock 사용."""

    monkeypatch.setattr(
        'app.services.llm_service.evaluate_qualitative_scores',
        llm_mock.evaluate_with_llm_mock,
    )
    monkeypatch.setattr(
        'app.services.diagnosis_pipeline.evaluate_qualitative_scores',
        llm_mock.evaluate_with_llm_mock,
    )

    def _mock_generate_final_report(
        narratives,
        final_type,
        merged_scores,
        **_: object,
    ) -> DiagnosisReportStructuredOutput:
        raw = llm_mock.generate_final_report_mock(merged_scores, final_type, narratives)
        return DiagnosisReportStructuredOutput(
            type=final_type,
            scores=AreaScores(**merged_scores),
            strengths=list(raw['strengths']),
            risk_factors=list(raw['risk_factors']),
            action_plans=list(raw['action_plans']),
            rationale=str(raw['rationale']),
            recommended_support=str(raw['recommended_support']),
        )

    monkeypatch.setattr(
        'app.services.llm_service.generate_final_report',
        _mock_generate_final_report,
    )
    monkeypatch.setattr(
        'app.services.diagnosis_pipeline.generate_final_report',
        _mock_generate_final_report,
    )
