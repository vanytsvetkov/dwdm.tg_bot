from typing import Any
from pydantic import BaseModel


class Bucket(BaseModel):
    bucketKey: str
    bucketValue: str
    absoluteTotal: str


class Aggregation(BaseModel):
    name: str
    bucket: list[Bucket]


class MissingReferenceIdAttributes(BaseModel):
    additionalAttributes: dict[str, Any]


class MissingReferenceId(BaseModel):
    type: str
    id: str
    attributes: MissingReferenceIdAttributes


class Meta(BaseModel):
    total: int = int()
    absoluteTotal: int = int()
    aggregations: list[Aggregation] = []
    missingReferences: bool = bool()
    missingReferenceIds: list[MissingReferenceId] = []
    filtered: bool = bool()
    totalHierarchicalCount: int = int()
