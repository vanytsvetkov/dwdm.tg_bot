from pydantic import BaseModel


class DisplayData(BaseModel):
    operationState: str = str()
    adminState: str = str()
    displayTopologySource: str = str()
    displayDeploymentState: str = str()
    displayName: str = str()


class AdditionalAttributes(BaseModel):
    isActual: str = str()
    FULLY_STITCHED: str = str()
    portCapacityInMbps: str = str()

    
class Attributes(BaseModel):
    operationState: str = str()
    deploymentState: str = str()
    displayData: DisplayData = DisplayData()
    resourceState: str = str()
    customerName: str = str()
    serviceClass: str = str()
    lastUpdatedAdminStateTimeStamp: str = str()
    lastUpdatedOperationalStateTimeStamp: str = str()
    userLabel: str = str()
    mgmtName: str = str()
    nativeName: str = str()
    awarenessTime: str = str()
    layerRate: str = str()
    layerRateQualifier: str = str()
    networkRole: str = str()
    directionality: str = str()
    topologySources: list[str] = list()
    adminState: str = str()
    active: bool = bool()
    additionalAttributes: AdditionalAttributes = AdditionalAttributes()
    reliability: str = str()
    resilienceLevel: str = str()
