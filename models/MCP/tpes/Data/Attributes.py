from pydantic import BaseModel


class Identifier(BaseModel):
    circuitId: str = str()
    networkConstructId: str = str()
    nodalId: str = str()


class Location(BaseModel):
    managementType: str = str()
    shelf: str = str()
    slot: str = str()
    port: str = str()
    mgmtMcId: str = str()
    mgmtNmcId: str = str()
    neName: str = str()


class LayerTermination(BaseModel):
    layerRate: str = str()
    structureType: str = str()
    terminationState: str = str()
    active: bool = bool()
    signalIndex: dict = dict()
    additionalAttributes: dict = dict()


class AdditionalAttributes(BaseModel):
    alarmResourceId: str = str()
    tpeLifeCycleOwnerType: str = str()
    shelves: str = str()
    reconcileRule: str = str()


class Attributes(BaseModel):
    state: str = str()
    identifiers: list[Identifier] = list()
    resourceState: str = str()
    structureType: str = str()
    nativeName: str = str()
    locations: list[Location] = list()
    layerTerminations: list[LayerTermination] = list()
    stackDirection: str = str()
    displayAlias: str = str()
    cardType: str = str()
    active: bool = bool()
    additionalAttributes: AdditionalAttributes = AdditionalAttributes()
