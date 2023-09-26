from datetime import datetime
import ipaddress
import uuid

from pydantic import BaseModel, Field


class GELFMessage(BaseModel):
    version: str = str()
    timestamp: datetime = datetime.now()
    host: str = str()
    short_message: str = str()
    level: int = int()
    full_message: str = str()
    level_: int = Field(int(), alias='_level')
    gl2_remote_ip_: ipaddress.IPv4Address = Field(ipaddress.IPv4Address('0.0.0.0'), alias='_gl2_remote_ip')
    gl2_remote_port_: int = Field(int(), alias='_gl2_remote_port')
    gl2_message_id_: str = Field(str(), alias='_gl2_message_id')
    kafka_topic_: str = Field(str(), alias='_kafka_topic')
    source_: str = Field(str(), alias='_source')
    message_: str = Field(str(), alias='_message')
    gl2_source_input_: str = Field(str(), alias='_gl2_source_input')
    full_message_: str = Field(str(), alias='_full_message')
    facility_num_: int = Field(int(), alias='_facility_num')
    forwarder_: str = Field(str(), alias='_forwarder')
    gl2_source_node_: uuid.UUID = Field(uuid.UUID, alias='_gl2_source_node')
    id_: uuid.UUID = Field(uuid.UUID, alias='_id')
    facility_: str = Field(str(), alias='_facility')
    timestamp_: datetime = Field(datetime.now(), alias='_timestamp')

    def __str__(self) -> str:
        return self.full_message
