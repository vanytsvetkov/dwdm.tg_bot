import asyncio
import logging as log

import vars
from interactors.Kafka import Consumer, Kafka
from models.Creds import Creds
from utils.Handlers import Handler
from utils.utils import load_creds


def main():
    credits = load_creds()
    asyncio.run(_main(credits))


async def _main(credits: Creds):
    log.info('Initialize Handler')
    handler = Handler(credits)

    log.info('Initialize Kafka')
    kafka = Kafka(credits)

    log.info('Initialize Consumer')
    await kafka.consumer.start()

    log.info('Get counts')
    count = kafka.consumer.get_partitions_count()
    workers = []
    for partition_id in range(count):
        worker_task = asyncio.create_task(worker(kafka.consumer, partition_id, handler))
        workers.append(worker_task)

    try:
        await handler.start()
        await asyncio.gather(*workers)
    except asyncio.CancelledError:
        log.info('Handler cancelled, stop.')
        await handler.stop()
    finally:
        log.info('Handler stopped.')


async def worker(consumer: Consumer, number: int, handler: Handler) -> None:
    log.info(f'Starting consumer #{number}')
    match number:
        case 0:
            consumer = consumer
        case _:
            consumer = await consumer.fork()
    while True:
        try:
            msg = await consumer.get_message()
            log.info(f'Consumer #{number} get a new message.')
            await handler.process(msg)
        except asyncio.CancelledError:
            log.info(f'Stopping consumer #{number}')
            await consumer.stop()
            log.info(f'Consumer #{number} stooped')
            break
        except Exception as e:
            error_text = e.__class__.__name__ + ': ' + str(e)
            log.critical(error_text)


if __name__ == "__main__":
    log.basicConfig(level=vars.LOG_LEVEL)
    main()
