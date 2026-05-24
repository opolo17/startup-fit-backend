# Startup Fit AI — Backend

FastAPI 진단 API: 정량 스코어링 + OpenAI 리포트 + 5대 유형 분류.

## 요구 사항

- Python 3.11+ (3.14 테스트됨)
- OpenAI API 키

## 환경 변수

이 폴더(`startup-fit-backend`)에 `.env`:

```env
OPENAI_API_KEY=sk-...
```

```powershell
Copy-Item .env.example .env
notepad .env
```

## 최초 설치 (PowerShell)

OneDrive 안에서는 `python -m venv .venv`가 실패할 수 있습니다. 스크립트가 `%LOCALAPPDATA%\StartupFitAI-venv`를 사용합니다.

```powershell
cd C:\Users\gnhan\OneDrive\Desktop\startup-fit\startup-fit-backend
.\setup-venv.ps1
```

## 서버 실행

```powershell
.\run-server.ps1
```

- Health: http://127.0.0.1:8000/health
- Docs: http://127.0.0.1:8000/docs
- 진단: `POST /api/v1/diagnosis/run`

포트 충돌 시: `.\stop-server.ps1` 후 재실행

## 테스트

```powershell
.\run-tests.ps1
```

## 프론트 연동

[startup-fit-frontend](../startup-fit-frontend)에서 `npm run dev` 후 진단 API 호출.
