from app.schemas.diagnosis import DiagnosisType, QuantitativeMetrics


def classify_diagnosis_type(
    metrics: QuantitativeMetrics,
    runway_months: float,
    policy_finance_score: int,
) -> DiagnosisType:
    """
    폭포수(우선순위) 규칙 — 먼저 일치하는 유형을 반환.
    """
    if not metrics.team_roles.developer and not metrics.has_mvp_url:
        return '실행역량 강화형'

    if runway_months < 6:
        return '고성장 도전형'

    if metrics.interview_scale == '5회 미만':
        return '시장검증 보완형'

    if policy_finance_score <= 60:
        return '정책금융 보완형'

    return '균형 성장형'
