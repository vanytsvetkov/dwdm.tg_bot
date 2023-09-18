from typing import Union

from pydantic import BaseModel
import models.MCP


class ResponseType(BaseModel):
    response: Union[*models.MCP.__all__, dict]
    success: bool
    status_code: int
    message: str = ''
    errors: list = []


def ProcessResponse(response: dict, model: str) -> ResponseType:
    model_cls = getattr(models.MCP, model, dict)

    class Response(ResponseType):
        response: model_cls = dict()

    return Response.model_validate(response)
