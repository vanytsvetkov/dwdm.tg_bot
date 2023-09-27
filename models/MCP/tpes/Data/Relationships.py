from pydantic import BaseModel


class Data(BaseModel):
    type: str = str()
    id: str = str()


class ClientTpes(BaseModel):
    data: list[Data] = list()


class Relationships(BaseModel):
    tpeDiscovered: dict = dict()
    networkConstruct: dict = dict()
    equipment: dict = dict()
    owningServerTpe: dict = dict()
    clientTpes: ClientTpes = ClientTpes()
