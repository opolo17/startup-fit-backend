from pydantic import BaseModel, Field

from app.schemas.diagnosis import AreaScores, DiagnosisType


class QualitativeEvaluationOutput(BaseModel):
    """Step 2: 정성 서사 기반 LLM 점수 (정책금융·성장성)."""

    policy_finance: int = Field(ge=0, le=100, description='정책금융 준비도 0~100')
    growth: int = Field(ge=0, le=100, description='성장성 0~100')


class DiagnosisReportStructuredOutput(BaseModel):
    """Step 4: 최종 리포트 Strict JSON (OpenAI Structured Outputs)."""

    type: DiagnosisType
    scores: AreaScores
    strengths: list[str] = Field(
        min_length=2,
        max_length=2,
        description='강점 TOP 2',
    )
    risk_factors: list[str] = Field(
        min_length=2,
        max_length=2,
        description='위험 요인 TOP 2',
    )
    action_plans: list[str] = Field(
        min_length=2,
        max_length=2,
        description='다음 액션 플랜 TOP 2',
    )
    rationale: str = Field(description='상세 판단 근거 줄글')
    recommended_support: str = Field(description='추천 지원사업 및 전략 줄글')
