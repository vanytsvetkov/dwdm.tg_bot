from pydantic import BaseModel

from models.MCP.fres.Data.Attributes import Attributes
from models.MCP.fres.Data.Relationships import Relationships


class Data(BaseModel):
    id: str = str()
    type: str = str()
    attributes: Attributes = Attributes()
    relationships: Relationships = Relationships()
