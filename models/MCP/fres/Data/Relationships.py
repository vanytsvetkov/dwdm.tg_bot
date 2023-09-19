from pydantic import BaseModel


class Data(BaseModel):
    type: str = str()
    id: str = str()


class FreDiscovered(BaseModel):
    data: Data = Data()


class Relationship(BaseModel):
    data: list[Data] = list()


class Relationships(BaseModel):
    freDiscovered: FreDiscovered = FreDiscovered()
    supportedByServices: Relationship = Relationship()
    endPoints: Relationship = Relationship()
    partitionFres: Relationship = Relationship()
    utilization: Relationship = Relationship()
