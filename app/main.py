from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import env_file_hint, get_settings

app = FastAPI(
    title='Startup Fit AI Diagnosis API',
    description='예비창업자 자가진단 하이브리드(정량+정성) 파이프라인',
    version='0.1.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix='/api/v1')


@app.get('/health')
def health_check() -> dict[str, str | bool]:
    settings = get_settings()
    return {
        'status': 'ok',
        'openai_configured': bool(settings.openai_api_key),
        'env_hint': env_file_hint(),
    }
