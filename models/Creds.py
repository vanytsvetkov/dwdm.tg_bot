from pydantic import BaseModel


class Bot(BaseModel):
    token: str
    users: dict[str, int]
    groups: dict[str, int]


class Cred(BaseModel):
    username: str | None = ''
    password: str | None = ''
    url: str | None = ''
    token: str | None = None


class Kafka(BaseModel):
    bootstrap_servers: str = 'localhost'
    topic: str
    handler: str

    @property
    def group_id(self) -> str:
        return f'{self.topic}:{self.handler}'


class Redis(BaseModel):
    host: str = 'localhost'
    port: int = 6379
    db: int = 0


class GTable(BaseModel):
    sheet_id: str


class Creds(BaseModel):
    tg: dict[str, Bot]
    d42: Cred
    mcp: Cred
    kafka: Kafka
    redis: Redis = Redis()
    gtable: GTable
