import asyncio
import json
import os
import sys
import logging as log
from interactors.Kafka import Kafka, Consumer
from utils.Handlers import Handler
from models.Credits import Credits


DATA_DIR = 'data'
CREDITS_FILENAME = 'credentials.json'
NECESSARY_FILES = [CREDITS_FILENAME]


def main():
    base = os.path.dirname(os.path.abspath(__file__))

    if not all(os.path.exists(os.path.join(base, DATA_DIR, file)) for file in NECESSARY_FILES):
        log.critical(f'Please ensure that all required files are located in the "{DATA_DIR}" directory.')
        sys.exit(0)

    log.info('Loading credits')
    with open(os.path.join(base, DATA_DIR, CREDITS_FILENAME)) as credits_file:
        credits = Credits.model_validate(json.load(credits_file))
    del credits_file

    asyncio.run(_main(credits))


async def _main(credits: Credits):
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
    finally:
        await handler.stop()
        log.info('Handler stopped.')


async def worker(consumer: Consumer, number: int, handler: Handler) -> None:
    log.info(f'Starting consumer #{number}')
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
    log.basicConfig(level=log.INFO)
    main()


