import json
from aiokafka import AIOKafkaConsumer
from models.Creds import Creds
from models.GELFMessage import GELFMessage


class Consumer:
    def __init__(self, topic, bootstrap_servers, group_id):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id

        self.consumer = AIOKafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    enable_auto_commit=True
            )

    async def start(self) -> None:
        """Set up consumer"""
        await self.consumer.start()

    async def stop(self) -> None:
        """Dispose consumer and delete all connections"""
        await self.consumer.stop()

    async def get_message(self) -> GELFMessage:
        """Get another GELF message"""
        msg = await self.consumer.getone()
        value = msg.value.decode('utf-8')
        json_value = json.loads(value)
        message = GELFMessage.model_validate(json_value)
        return message

    def get_partitions_count(self) -> int:
        partitions = self.consumer.partitions_for_topic(self.topic)
        return len(partitions)


class Kafka:
    def __init__(self, credits: Creds):
        self.topic = credits.kafka.topic
        self.bootstrap_servers = credits.kafka.bootstrap_servers
        self.group_id = credits.kafka.group_id

        self.consumer = self._init_consumer()

    def _init_consumer(self):
        return Consumer(self.topic, self.bootstrap_servers, self.group_id)
