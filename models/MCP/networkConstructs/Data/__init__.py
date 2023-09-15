from pydantic import BaseModel

from models.MCP.networkConstructs.Data.Attributes import Attributes
from models.MCP.networkConstructs.Data.Relationships import Relationships


class Meta(BaseModel):
    partiallyPopulated: bool = bool()


class Data(BaseModel):
    meta: Meta = Meta()
    id: str = str()
    type: str = str()
    attributes: Attributes = Attributes()
    relationships: Relationships = Relationships()
