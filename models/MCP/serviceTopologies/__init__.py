from pydantic import BaseModel, field_validator

from models.MCP.common.Meta import Meta
from models.MCP.common.Links import Links
from models.MCP.fres.Data import Data
from models.MCP.tpes.Data import Data as tpeData


class serviceTopologies(BaseModel):
    meta: Meta = Meta()
    links: Links = Links()
    data: Data = Data()
    included: list[tpeData] = list()

    @field_validator('included')
    def filter_included_by_type(cls, value: list[tpeData]) -> list[tpeData]:
        return [item for item in value if item.type == 'tpes']
