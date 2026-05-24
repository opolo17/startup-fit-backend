class LLMServiceError(Exception):
    """OpenAI 호출 실패 시 라우터에서 HTTPException으로 변환합니다."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)
