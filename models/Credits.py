from pydantic import BaseModel


class Bot(BaseModel):
    token: str
    users: dict[str, int]
    groups: dict[str, int]


class Credit(BaseModel):
    username: str | None = ''
    password: str | None = ''
    url: str | None = ''
    token: str | None = None


class Kafka(BaseModel):
    bootstrap_servers: str
    topic: str
    handler: str

    @property
    def group_id(self) -> str:
        return f'{self.topic}:{self.handler}'


class Credits(BaseModel):
    tg: dict[str, Bot]
    d42: Credit
    mcp: Credit
    kafka: Kafka
