from fastapi import APIRouter, Depends, HTTPException

from app.exceptions import LLMServiceError
from app.schemas.diagnosis import DiagnosisRequest, DiagnosisResponse
from app.services.diagnosis_pipeline import DiagnosisPipelineService, get_pipeline_service

router = APIRouter(prefix='/diagnosis', tags=['diagnosis'])


@router.post('/run', response_model=DiagnosisResponse, summary='자가진단 파이프라인 실행')
def run_diagnosis(
    request: DiagnosisRequest,
    service: DiagnosisPipelineService = Depends(get_pipeline_service),
) -> DiagnosisResponse:
    try:
        return service.run(request)
    except LLMServiceError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail='진단 파이프라인 처리 중 오류가 발생했습니다.',
        ) from error
