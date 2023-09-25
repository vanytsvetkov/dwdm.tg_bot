from typing import Any
from pydantic import BaseModel


class Bucket(BaseModel):
    bucketKey: str = str()
    bucketValue: str = str()
    absoluteTotal: str = str()


class Aggregation(BaseModel):
    name: str = str()
    bucket: list[Bucket] = list()


class MissingReferenceIdAttributes(BaseModel):
    additionalAttributes: dict[str, Any] = dict()


class MissingReferenceId(BaseModel):
    type: str = str()
    id: str = str()
    attributes: MissingReferenceIdAttributes = MissingReferenceIdAttributes()


class Meta(BaseModel):
    total: int = int()
    absoluteTotal: int = int()
    aggregations: list[Aggregation] = []
    missingReferences: bool = bool()
    missingReferenceIds: list[MissingReferenceId] = []
    filtered: bool = bool()
    totalHierarchicalCount: int = int()
