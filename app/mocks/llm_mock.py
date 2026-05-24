"""
테스트·오프라인용 LLM Mock.
프로덕션 경로: app.services.llm_service (OpenAI gpt-4o-mini + Structured Outputs)
"""

import hashlib

from app.schemas.diagnosis import Narratives

def _seeded_score(seed: str, minimum: int = 45, span: int = 46) -> int:
    """동일 입력에 대해 테스트 가능한 결정적 0~100 점수."""
    digest = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    value = int(digest[:8], 16)
    return min(100, minimum + (value % span))


def evaluate_with_llm_mock(narratives: Narratives) -> dict[str, int]:
    """
    LLM 정성 평가 Mock.
    실제 OpenAI 등 API로 교체 시 이 함수 시그니처를 유지하고 내부만 교체하면 됩니다.
    """
    blob = '|'.join(
        [
            narratives.problem_definition,
            narratives.solution_description,
            narratives.differentiation_strategy,
            narratives.value_proposition,
            narratives.revenue_model,
            narratives.expansion_strategy,
        ],
    )

    return {
        'policy_finance': _seeded_score(f'policy:{blob}', minimum=40, span=55),
        'growth': _seeded_score(f'growth:{blob}', minimum=35, span=60),
    }


def generate_final_report_mock(
    scores: dict[str, int],
    final_type: str,
    narratives: Narratives,
) -> dict[str, object]:
    """
    최종 리포트 생성 Mock.
    실제 LLM 리포트 생성기로 교체 시 반환 JSON 스키마를 동일하게 유지합니다.
    """
    problem_hint = narratives.problem_definition[:40] or '핵심 문제 정의'
    solution_hint = narratives.solution_description[:40] or '솔루션 접근'

    type_copy: dict[str, dict[str, list[str] | str]] = {
        '실행역량 강화형': {
            'strengths': [
                f'문제 인식({problem_hint}…)이 비교적 분명해 실행 방향을 잡기 쉽습니다.',
                '초기 범위를 좁히면 빠르게 프로토타입을 검증할 수 있는 구조입니다.',
            ],
            'risk_factors': [
                '개발·MVP 실행 역량이 부족해 검증 속도가 느려질 수 있습니다.',
                '시장 반응 데이터가 쌓이기 전에 자금 소진 위험이 있습니다.',
            ],
            'action_plans': [
                '핵심 기능 1개만 포함한 MVP를 4주 내 출시하세요.',
                '개발 파트너 또는 외주 범위를 명확히 정의해 실행 계획을 세우세요.',
            ],
            'recommended_support': '예비창업패키지(MVP 제작), 창업지원센터 기술 멘토링, K-Startup 액셀러레이팅',
        },
        '고성장 도전형': {
            'strengths': [
                '성장 잠재력 점수가 양호해 확장 시나리오를 그리기 좋습니다.',
                f'솔루션({solution_hint}…)이 시장 니즈와 연결될 여지가 있습니다.',
            ],
            'risk_factors': [
                '런웨이가 6개월 미만이면 성장 실험 전에 자금 압박이 큽니다.',
                '고정비 대비 매출 검증이 늦어지면 투자·지원 설득이 어렵습니다.',
            ],
            'action_plans': [
                '월 고정비를 재조정하고 6개월 이상 런웨이 확보 계획을 수립하세요.',
                '유료 전환 또는 LOI(구매 의향서) 확보를 8주 안에 목표로 설정하세요.',
            ],
            'recommended_support': '초기창업패키지, TIPS/R&D 연계, 지역 창업도약패키지',
        },
        '시장검증 보완형': {
            'strengths': [
                '가치 제안 서술이 있어 인터뷰 설계의 출발점이 마련되어 있습니다.',
                '정량 지표상 실행 준비도가 일부 확보되어 실험을 진행할 수 있습니다.',
            ],
            'risk_factors': [
                '고객 인터뷰가 5회 미만이면 문제·가설 검증 신뢰도가 낮습니다.',
                '지불 의사 데이터가 부족하면 BM 수정 근거가 약합니다.',
            ],
            'action_plans': [
                '핵심 고객 10명 이상 인터뷰를 3주 내 완료하세요.',
                '인터뷰 스크립트에 가격·대체재·구매 의향 질문을 반드시 포함하세요.',
            ],
            'recommended_support': '창업진흥원 창업교육, 예비창업자 시장검증 프로그램, 대학 창업센터 PoC 지원',
        },
        '정책금융 보완형': {
            'strengths': [
                '사업 구조 설명(수익·확장)이 있어 지원사업 서류화에 활용 가능합니다.',
                '안정성·시장검증 중 일부 영역은 보완 가능한 수준입니다.',
            ],
            'risk_factors': [
                '정책금융·지원사업 대출 심사에 필요한 재무·실적 근거가 부족합니다.',
                'BM·재무 계획 서술이 심사 기준에 미달할 수 있습니다.',
            ],
            'action_plans': [
                '3개년 재무계획 초안과 자금 조달 계획을 작성하세요.',
                '지원사업·대출용 1페이지 IR 요약본을 별도로 준비하세요.',
            ],
            'recommended_support': '신용보증재단 보증, 기술보증기금, 소상공인 정책자금, 지역 혁신바우처',
        },
        '균형 성장형': {
            'strengths': [
                '안정성·시장검증·실행준비도가 고르게 나와 다음 단계 확장이 가능합니다.',
                f'차별화 전략({narratives.differentiation_strategy[:30] or "차별점"}…)을 지원사업 스토리에 연결하기 좋습니다.',
            ],
            'risk_factors': [
                '성장·정책금융 영역은 추가 개선 여지가 있어 우선순위 조정이 필요합니다.',
                '팀 역할 분담이 불명확하면 실행 속도가 떨어질 수 있습니다.',
            ],
            'action_plans': [
                '분기별 KPI(인터뷰 수, 전환율, 런웨이)를 정의하고 월간 점검하세요.',
                '지원사업·민간 투자용 자료를 버전별로 분리해 관리하세요.',
            ],
            'recommended_support': '예비창업패키지, 초기창업패키지, 창업도약패키지, 민간 액셀러레이터',
        },
    }

    copy = type_copy.get(final_type, type_copy['균형 성장형'])

    return {
        'type': final_type,
        'scores': scores,
        'strengths': copy['strengths'],
        'risk_factors': copy['risk_factors'],
        'action_plans': copy['action_plans'],
        'rationale': (
            f'[Mock] 최종 유형 "{final_type}"은 정량 런웨이·인터뷰·MVP·팀 역량과 '
            f'Mock LLM 점수(정책금융 {scores["policy_finance"]}, 성장 {scores["growth"]})를 '
            f'폭포수 규칙으로 종합한 결과입니다. 문제·솔루션 서술 길이를 반영한 더미 근거입니다.'
        ),
        'recommended_support': copy['recommended_support'],
    }
