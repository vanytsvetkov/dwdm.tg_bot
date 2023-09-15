from pydantic import BaseModel
import models.MCP


def ProcessResponse(response: dict, model: str):
    model_cls = getattr(models.MCP, model, dict)

    class Response(BaseModel):
        response: model_cls = {}
        success: bool
        status_code: int
        message: str = ''
        errors: list = []

    return Response.model_validate(response)
