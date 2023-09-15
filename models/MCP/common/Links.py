from pydantic import BaseModel


class Links(BaseModel):
    self: str = str()
    first: str = str()
    last: str = str()
    prev: str = str()
    next: str = str()
    current: str = str()
