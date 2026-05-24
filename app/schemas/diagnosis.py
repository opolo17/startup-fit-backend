from typing import Literal

from pydantic import BaseModel, Field

InterviewScale = Literal['5회 미만', '5회 이상~10회 미만', '10회 이상']

MonetizationStage = Literal[
    '아직 없음',
    '구매 의향을 말한 고객이 있음',
    '구매 의향을 말한 고객 있음',
    '사전예약/대기자 있음',
    '파일럿 또는 계약 논의 중',
    '실제 유료 고객 있음',
    '반복 구매 또는 재계약 있음',
]

DiagnosisType = Literal[
    '실행역량 강화형',
    '고성장 도전형',
    '시장검증 보완형',
    '정책금융 보완형',
    '균형 성장형',
]


class Narratives(BaseModel):
    problem_definition: str = ''
    solution_description: str = ''
    differentiation_strategy: str = ''
    value_proposition: str = ''
    revenue_model: str = ''
    expansion_strategy: str = ''


class TeamRoles(BaseModel):
    pm_planning: bool = False
    design: bool = False
    developer: bool = False
    marketing_sales: bool = False


class QuantitativeMetrics(BaseModel):
    current_assets: float = Field(ge=0, description='현재 보유 창업 자금 (만원)')
    monthly_overhead: float = Field(ge=0, description='예상 월 고정비 (만원)')
    interview_scale: InterviewScale
    monetization_stage: MonetizationStage
    team_roles: TeamRoles
    has_mvp_url: bool = False
    mvp_url: str = ''
    has_3month_goal: bool = False


class DiagnosisRequest(BaseModel):
    """프론트엔드 자가진단 제출 페이로드 (핵심 필드 + 선택 메타데이터)."""

    narratives: Narratives
    quantitative_metrics: QuantitativeMetrics
    startup_status: str | None = None
    item_name: str | None = None
    selected_sectors: list[str] | None = None
    location: str | None = None


class AreaScores(BaseModel):
    stability: int
    growth: int
    market_validation: int
    execution_readiness: int
    policy_finance: int


class QuantitativeBreakdown(BaseModel):
    runway_months: float
    stability: int
    market_validation: int
    execution_readiness: int


class DiagnosisResponse(BaseModel):
    type: DiagnosisType
    scores: AreaScores
    strengths: list[str]
    risk_factors: list[str]
    action_plans: list[str]
    rationale: str
    recommended_support: str
    quantitative_breakdown: QuantitativeBreakdown
