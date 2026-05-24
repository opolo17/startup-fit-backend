import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.diagnosis import DiagnosisRequest, Narratives, QuantitativeMetrics, TeamRoles
from app.services.diagnosis_pipeline import DiagnosisPipelineService
from app.services.quantitative_scoring import RUNWAY_INFINITE, calculate_runway_months, score_stability

client = TestClient(app)


def base_metrics(**overrides: object) -> QuantitativeMetrics:
    payload = {
        'current_assets': 600,
        'monthly_overhead': 50,
        'interview_scale': '10회 이상',
        'monetization_stage': '실제 유료 고객 있음',
        'team_roles': {
            'pm_planning': True,
            'design': False,
            'developer': True,
            'marketing_sales': False,
        },
        'has_mvp_url': True,
    }
    payload.update(overrides)
    return QuantitativeMetrics(**payload)


def test_runway_zero_uses_infinite_runway():
    runway = calculate_runway_months(100, 0)
    assert runway == RUNWAY_INFINITE
    assert score_stability(runway) == 100


def test_execution_capacity_type_when_no_dev_no_mvp():
    request = DiagnosisRequest(
        narratives=Narratives(problem_definition='문제'),
        quantitative_metrics=base_metrics(
            team_roles=TeamRoles(developer=False),
            has_mvp_url=False,
        ),
    )
    result = DiagnosisPipelineService().run(request)
    assert result.type == '실행역량 강화형'


def test_low_runway_high_growth_challenge_type():
    request = DiagnosisRequest(
        narratives=Narratives(),
        quantitative_metrics=base_metrics(
            current_assets=100,
            monthly_overhead=50,
            team_roles=TeamRoles(developer=True),
            has_mvp_url=True,
        ),
    )
    result = DiagnosisPipelineService().run(request)
    assert result.type == '고성장 도전형'


def test_market_validation_type():
    request = DiagnosisRequest(
        narratives=Narratives(),
        quantitative_metrics=base_metrics(
            current_assets=1200,
            monthly_overhead=50,
            interview_scale='5회 미만',
            team_roles=TeamRoles(developer=True),
            has_mvp_url=True,
        ),
    )
    result = DiagnosisPipelineService().run(request)
    assert result.type == '시장검증 보완형'


def test_api_run_endpoint():
    response = client.post(
        '/api/v1/diagnosis/run',
        json={
            'narratives': {
                'problem_definition': '지원사업 탐색이 어렵다',
                'solution_description': 'AI 맞춤 진단',
                'differentiation_strategy': '진단+추천 통합',
                'value_proposition': '원스톱 진단',
                'revenue_model': '구독+기관 제휴',
                'expansion_strategy': '전국 확장',
            },
            'quantitative_metrics': {
                'current_assets': 500,
                'monthly_overhead': 50,
                'interview_scale': '5회 이상~10회 미만',
                'monetization_stage': '구매 의향을 말한 고객 있음',
                'team_roles': {
                    'pm_planning': True,
                    'design': True,
                    'developer': True,
                    'marketing_sales': False,
                },
                'has_mvp_url': True,
                'mvp_url': 'https://example.com',
            },
            'startup_status': '예비창업자',
            'item_name': 'Startup Fit AI',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert 'type' in body
    assert body['scores']['stability'] == 80
    assert body['scores']['market_validation'] == 35
    assert body['scores']['execution_readiness'] == 100
