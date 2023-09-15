from pydantic import BaseModel


class Relationships(BaseModel):
    networkConstructPlanned: dict = dict()
    networkConstructExpectations: dict = dict()
    networkConstructDiscovered: dict = dict()
    managementSession: dict = dict()
    utilization: dict = dict()
    networkConstructTiming: dict = dict()
    networkConstructPOs: dict = dict()
    exclusionProfiles: dict = dict()
    physicalLocation: dict = dict()
    parentNetworkConstruct: dict = dict()
    childrenNetworkConstruct: dict = dict()
    concrete: dict = dict()
    concreteAssociations: dict = dict()
    groups: dict = dict()
    srlg: dict = dict()
    shareSrlg: dict = dict()
    aggregatedMembers: dict = dict()
    displayAggregatedMembers: dict = dict()
    aggregatingParent: dict = dict()
