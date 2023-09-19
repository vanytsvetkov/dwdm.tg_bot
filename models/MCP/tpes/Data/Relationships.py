from pydantic import BaseModel


class Relationships(BaseModel):
    tpeDiscovered: dict = dict()
    networkConstruct: dict = dict()
    equipment: dict = dict()
    owningServerTpe: dict = dict()
