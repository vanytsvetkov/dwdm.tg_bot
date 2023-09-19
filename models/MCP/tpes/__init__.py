from pydantic import BaseModel, field_validator

from models.MCP.common.Meta import Meta
from models.MCP.common.Links import Links
from models.MCP.tpes.Data import Data


class tpes(BaseModel):
    meta: Meta = Meta()
    links: Links = Links()
    data: Data = Data()
