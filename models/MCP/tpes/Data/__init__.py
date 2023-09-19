from pydantic import BaseModel

from models.MCP.tpes.Data.Attributes import Attributes
from models.MCP.tpes.Data.Relationships import Relationships


class Data(BaseModel):
    id: str = str()
    type: str = str()
    attributes: Attributes = Attributes()
    relationships: Relationships = Relationships()
