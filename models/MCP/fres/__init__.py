from typing import Any
from pydantic import BaseModel

from models.MCP.common.Meta import Meta
from models.MCP.common.Links import Links
from models.MCP.fres.Data import Data


class fres(BaseModel):
    meta: Meta = Meta()
    links: Links = Links()
    data: list[Data] = list()
    included: list[dict[str, Any]] = list()
