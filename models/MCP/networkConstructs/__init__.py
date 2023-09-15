from typing import Any
from pydantic import BaseModel

from models.MCP.networkConstructs.Meta import Meta
from models.MCP.common.Links import Links
from models.MCP.networkConstructs.Data import Data


class networkConstructs(BaseModel):
    meta: Meta = Meta()
    links: Links = Links()
    data: list[Data] = list()
    included: list[dict[str, Any]] = list()
