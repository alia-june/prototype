"""Stable CPU-domain errors; no transport or filesystem execution."""

class ModelError(ValueError):
    def __init__(self, code: str, message: str, operation_id: str | None = None):
        super().__init__(message)
        self.code = code
        self.operation_id = operation_id

    def to_dict(self) -> dict:
        return {"code": self.code, "message": str(self), "operation_id": self.operation_id}
