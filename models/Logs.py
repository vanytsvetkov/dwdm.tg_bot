from pydantic import BaseModel, Field
import html


class Log(BaseModel):
    PRIVAL: str = str()
    VERSION: str = str()
    TIMESTAMP: str = str()
    SOURCE: str = str()

    processed: bool = False
    regexp_pattern: str = str()

    def __init__(self, **data):
        for key, value in data.items():
            if isinstance(value, str) and key != 'regexp_pattern':
                data[key] = html.escape(value)
        super().__init__(**data)


class LogCiena6500(Log):
    LEVEL: str = str()
    SITE: str = str()
    SHELF: str = str()
    PIM: str = str()
    RESOURCE: str = str()
    DATE: str = str()
    TIME: str = str()
    YEAR: str = str()
    LOGNAME: str = str()
    LOGEVENT: str = str()
    UID: str = str()
    UPC: str = str()
    PORTTYPE: str = str()
    PORTADDR: str = str()
    STATUS: str = str()
    EVTDESCR: str = str()
    CONDITION_TYPE: str = str()
    SEVERITY: str = str()
    LOCATION: str = str()
    DIRECTION: str = str()
    DESCRIPTION: str = str()
    PORT_MODE: str = str()
    NE_ALARM_ID: str = str()
    MODE: str = str()
    ADDITIONALINFO: str = str()
    WAVELENGTH: str = str()
    SERVICE_AFFECTED: str = 'NSA'
    DBCHGSEQ: str = str()
    USERID: str = str()
    PRIORITY: str = str()
    ED_TELEMETRY: str = str()
    LOSTHRES: str = str()
    TELEPWR: str = str()
    TELEMODE: str = str()
    SIGNALPWR: str = str()
    RXPWR: str = str()
    SPANLOSS: str = str()
    MSG: str = str()


class LogCienaWaveserver(Log):
    INTRO: str = str()
    MAC: str = str()
    WS: str = str()
    PIM: str = str()
    EVENT_TYPE: str = str()
    WOS: str = str()
    TIME_FORMAT: str = str()
    EVENT_ID: str = str()
    EVENT_NAME: str = str()
    EVENT_ORIGIN: str = str()
    TAG: str = str()
    MSG_ID: str = str()
    MSG_: str = Field(str(), alias='MSG')

    RESOURCE_: str = Field(str(), alias='RESOURCE')
    RESO: str = str()
    URCE: str = str()

    SEVERITY: str = str()

    MONTH: str = str()
    DAY: str = str()
    TIME: str = str()

    @property
    def MSG(self):
        return self.MSG_.strip()

    @property
    def RESOURCE(self) -> str:
        resource = str()
        if self.RESOURCE_:
            if self.RESOURCE_.isdigit():
                resource = f'{self.EVENT_ORIGIN} {self.RESOURCE_}'
            else:
                resource = self.RESOURCE_
        elif self.RESO and self.URCE:
            resource = f'{self.RESO}-{self.URCE}'

        return (
            resource
            .replace("/", "-")
            .replace(' ', '-')
            .lower()
        )
