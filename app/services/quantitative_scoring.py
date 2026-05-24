from app.schemas.diagnosis import QuantitativeBreakdown, QuantitativeMetrics

RUNWAY_INFINITE = 999.0

INTERVIEW_SCORES: dict[str, int] = {
    '5회 미만': 0,
    '5회 이상~10회 미만': 15,
    '10회 이상': 30,
}

MONETIZATION_SCORES: dict[str, int] = {
    '아직 없음': 0,
    '구매 의향을 말한 고객이 있음': 20,
    '구매 의향을 말한 고객 있음': 20,
    '사전예약/대기자 있음': 40,
    '파일럿 또는 계약 논의 중': 50,
    '실제 유료 고객 있음': 60,
    '반복 구매 또는 재계약 있음': 70,
}


def calculate_runway_months(current_assets: float, monthly_overhead: float) -> float:
    if monthly_overhead <= 0:
        return RUNWAY_INFINITE
    return current_assets / monthly_overhead


def score_stability(runway: float) -> int:
    if runway >= 12:
        return 100
    if runway >= 6:
        return 80
    if runway >= 3:
        return 60
    if runway >= 1:
        return 30
    return 10


def score_market_validation(metrics: QuantitativeMetrics) -> int:
    interview_score = INTERVIEW_SCORES.get(metrics.interview_scale, 0)
    payment_score = MONETIZATION_SCORES.get(metrics.monetization_stage, 0)
    return min(100, interview_score + payment_score)


def score_execution_readiness(metrics: QuantitativeMetrics) -> int:
    total = 20
    if metrics.team_roles.developer:
        total += 40
    if metrics.has_mvp_url:
        total += 40
    return min(100, total)


def compute_quantitative_scores(metrics: QuantitativeMetrics) -> QuantitativeBreakdown:
    runway = calculate_runway_months(metrics.current_assets, metrics.monthly_overhead)

    return QuantitativeBreakdown(
        runway_months=round(runway, 2) if runway != RUNWAY_INFINITE else RUNWAY_INFINITE,
        stability=score_stability(runway),
        market_validation=score_market_validation(metrics),
        execution_readiness=score_execution_readiness(metrics),
    )
