from app.schemas.diagnosis import AreaScores, DiagnosisRequest, DiagnosisResponse
from app.services.llm_service import evaluate_qualitative_scores, generate_final_report
from app.services.quantitative_scoring import calculate_runway_months, compute_quantitative_scores
from app.services.type_classification import classify_diagnosis_type


class DiagnosisPipelineService:
    def run(self, request: DiagnosisRequest) -> DiagnosisResponse:
        metrics = request.quantitative_metrics
        quantitative = compute_quantitative_scores(metrics)
        runway = calculate_runway_months(metrics.current_assets, metrics.monthly_overhead)

        llm_scores = evaluate_qualitative_scores(request.narratives)

        final_type = classify_diagnosis_type(
            metrics=metrics,
            runway_months=runway,
            policy_finance_score=llm_scores['policy_finance'],
        )

        merged_scores = {
            'stability': quantitative.stability,
            'growth': llm_scores['growth'],
            'market_validation': quantitative.market_validation,
            'execution_readiness': quantitative.execution_readiness,
            'policy_finance': llm_scores['policy_finance'],
        }

        metadata = {
            'startup_status': request.startup_status,
            'item_name': request.item_name,
            'selected_sectors': request.selected_sectors,
            'location': request.location,
        }

        report = generate_final_report(
            narratives=request.narratives,
            final_type=final_type,
            merged_scores=merged_scores,
            quantitative_breakdown=quantitative,
            metrics=metrics,
            runway_months=runway,
            metadata=metadata,
        )

        return DiagnosisResponse(
            type=report.type,
            scores=report.scores,
            strengths=report.strengths,
            risk_factors=report.risk_factors,
            action_plans=report.action_plans,
            rationale=report.rationale,
            recommended_support=report.recommended_support,
            quantitative_breakdown=quantitative,
        )


def get_pipeline_service() -> DiagnosisPipelineService:
    return DiagnosisPipelineService()
