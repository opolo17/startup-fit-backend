import json
from typing import Any, NoReturn

from pydantic import BaseModel
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from app.config import get_settings
from app.exceptions import LLMServiceError
from app.schemas.diagnosis import DiagnosisType, Narratives, QuantitativeBreakdown, QuantitativeMetrics
from app.schemas.llm_outputs import DiagnosisReportStructuredOutput, QualitativeEvaluationOutput

QUALITATIVE_SYSTEM_PROMPT = """\
너는 10년 차 정부지원사업 및 기술창업 전문 심사역이다.
예비창업자가 제출한 정성 서사(narratives)를 비판적으로 검증하고, 아래 루브릭에 따라 0~100 정수로 엄격하게 채점하라.

## 채점 루브릭
### policy_finance (정책금융·지원사업 준비도)
- 문제·솔루션·수익모델·확장 전략이 지원사업 IR/사업계획서에 바로 쓰일 수 있는가?
- 재무·실적·시장검증 근거가 서술에 드러나는가? (없으면 40점 이하)
- 정책자금·보증·R&D 연계 스토리가 논리적인가?

### growth (성장성)
- 시장 규모·확장 시나리오·차별화가 구체적인가?
- 수익모델이 단기 검증 가능한 구조인가?
- 모호·과장·근거 없는 주장은 감점하라.

## 규칙
- 각 점수는 반드시 0 이상 100 이하 정수.
- 서사가 빈약하거나 모순이 있으면 50점 미만을 부여할 수 있다.
- 응답은 지정된 JSON 스키마만 따른다.
"""

REPORT_SYSTEM_PROMPT = """\
너는 10년 차 정부지원사업 및 기술창업 전문 심사역이다.
백엔드 Rule-based 엔진이 산출한 **확정 유형(type)** 과 **확정 점수(scores)** 는 절대 변경하지 마라.
너의 역할은 해당 유형·점수와 논리적으로 100% 일치하는 진단 리포트 문장을 작성하는 것이다.

## 작성 규칙
1. `type`, `scores` 필드는 사용자 메시지에 주어진 값을 **그대로** 복사한다.
2. `strengths`, `risk_factors`, `action_plans`는 각각 정확히 2개의 한국어 문장(배열 길이 2).
3. `rationale`: 확정 유형·5개 영역 점수·정량 지표(런웨이, 인터뷰, 지불의사 등)를 인용하며 3~6문장으로 판단 근거를 서술.
4. `action_plans`: 확정 유형에 맞는 실행 가능한 다음 단계 2가지(기한·수치 포함 권장).
5. `recommended_support`: 한국 정부·공공 지원사업·정책금융·액셀러레이터를 1~2문장으로 구체 추천.
6. 정성 서사(narratives)의 핵심 키워드를 1회 이상 반영하되, 허구 데이터를 만들지 마라.
7. 응답은 지정된 JSON 스키마만 따른다.
"""


def _get_client() -> OpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise LLMServiceError(
            status_code=503,
            detail='OPENAI_API_KEY가 설정되지 않았습니다. 프로젝트 루트 .env 파일을 확인하세요.',
        )
    return OpenAI(api_key=settings.openai_api_key)


def _handle_openai_error(error: Exception) -> NoReturn:
    if isinstance(error, AuthenticationError):
        raise LLMServiceError(
            status_code=401,
            detail='OpenAI API 인증에 실패했습니다. OPENAI_API_KEY를 확인하세요.',
        ) from error
    if isinstance(error, RateLimitError):
        raise LLMServiceError(
            status_code=429,
            detail='OpenAI API 요청 한도를 초과했습니다. 잠시 후 다시 시도하세요.',
        ) from error
    if isinstance(error, APITimeoutError):
        raise LLMServiceError(
            status_code=504,
            detail='OpenAI API 응답 시간이 초과되었습니다.',
        ) from error
    if isinstance(error, APIConnectionError):
        raise LLMServiceError(
            status_code=503,
            detail='OpenAI API에 연결할 수 없습니다. 네트워크 상태를 확인하세요.',
        ) from error
    if isinstance(error, APIStatusError):
        if error.status_code == 400 and 'token' in str(error).lower():
            raise LLMServiceError(
                status_code=413,
                detail='입력 내용이 너무 깁니다. 서사를 줄인 뒤 다시 시도하세요.',
            ) from error
        raise LLMServiceError(
            status_code=502,
            detail=f'OpenAI API 오류가 발생했습니다. (HTTP {error.status_code})',
        ) from error
    raise LLMServiceError(
        status_code=502,
        detail='OpenAI API 호출 중 알 수 없는 오류가 발생했습니다.',
    ) from error


def _parse_completion(completion: Any, model_type: type[BaseModel]) -> BaseModel:
    message = completion.choices[0].message
    if getattr(message, 'refusal', None):
        raise LLMServiceError(status_code=422, detail=f'LLM이 응답을 거부했습니다: {message.refusal}')

    parsed = message.parsed
    if parsed is None:
        raise LLMServiceError(status_code=502, detail='LLM 구조화 응답 파싱에 실패했습니다.')
    return parsed


def evaluate_qualitative_scores(narratives: Narratives) -> dict[str, int]:
    """
    정성 서사 기반 policy_finance·growth 점수 산출 (OpenAI Structured Outputs).
    테스트·폴백: app.mocks.llm_mock.evaluate_with_llm_mock
    """
    settings = get_settings()
    client = _get_client()

    user_payload = {
        'narratives': narratives.model_dump(),
        'instruction': '위 서사만을 근거로 policy_finance, growth를 채점하세요.',
    }

    try:
        completion = client.beta.chat.completions.parse(
            model=settings.openai_model,
            messages=[
                {'role': 'system', 'content': QUALITATIVE_SYSTEM_PROMPT},
                {'role': 'user', 'content': json.dumps(user_payload, ensure_ascii=False)},
            ],
            response_format=QualitativeEvaluationOutput,
            temperature=0.2,
        )
        result = _parse_completion(completion, QualitativeEvaluationOutput)
        return {
            'policy_finance': result.policy_finance,
            'growth': result.growth,
        }
    except LLMServiceError:
        raise
    except Exception as error:
        _handle_openai_error(error)


def generate_final_report(
    narratives: Narratives,
    final_type: DiagnosisType,
    merged_scores: dict[str, int],
    quantitative_breakdown: QuantitativeBreakdown,
    metrics: QuantitativeMetrics,
    runway_months: float,
    metadata: dict[str, Any] | None = None,
) -> DiagnosisReportStructuredOutput:
    """
    확정 유형·점수를 반영한 최종 리포트 생성 (OpenAI Structured Outputs).
    Mock 대체: app.mocks.llm_mock.generate_final_report_mock
    """
    settings = get_settings()
    client = _get_client()

    locked_scores = {
        'stability': merged_scores['stability'],
        'growth': merged_scores['growth'],
        'market_validation': merged_scores['market_validation'],
        'execution_readiness': merged_scores['execution_readiness'],
        'policy_finance': merged_scores['policy_finance'],
    }

    user_payload = {
        'locked_type': final_type,
        'locked_scores': locked_scores,
        'quantitative_context': {
            'runway_months': quantitative_breakdown.runway_months,
            'rule_stability': quantitative_breakdown.stability,
            'rule_market_validation': quantitative_breakdown.market_validation,
            'rule_execution_readiness': quantitative_breakdown.execution_readiness,
            'interview_scale': metrics.interview_scale,
            'monetization_stage': metrics.monetization_stage,
            'team_roles': metrics.team_roles.model_dump(),
            'has_mvp_url': metrics.has_mvp_url,
            'current_assets_manwon': metrics.current_assets,
            'monthly_overhead_manwon': metrics.monthly_overhead,
            'runway_months_computed': runway_months,
        },
        'narratives': narratives.model_dump(),
        'metadata': metadata or {},
        'instruction': (
            'locked_type과 locked_scores를 JSON의 type, scores에 그대로 넣고, '
            '나머지 텍스트 필드만 작성하세요.'
        ),
    }

    try:
        completion = client.beta.chat.completions.parse(
            model=settings.openai_model,
            messages=[
                {'role': 'system', 'content': REPORT_SYSTEM_PROMPT},
                {'role': 'user', 'content': json.dumps(user_payload, ensure_ascii=False)},
            ],
            response_format=DiagnosisReportStructuredOutput,
            temperature=0.4,
        )
        report = _parse_completion(completion, DiagnosisReportStructuredOutput)
    except LLMServiceError:
        raise
    except Exception as error:
        _handle_openai_error(error)

    # 프론트 파싱 안정성: 백엔드 확정값으로 강제 정합
    from app.schemas.diagnosis import AreaScores

    return DiagnosisReportStructuredOutput(
        type=final_type,
        scores=AreaScores(**locked_scores),
        strengths=report.strengths,
        risk_factors=report.risk_factors,
        action_plans=report.action_plans,
        rationale=report.rationale,
        recommended_support=report.recommended_support,
    )
