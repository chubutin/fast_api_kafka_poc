import datetime
import random
from random import randint
from typing import Set, Any
from fastapi import FastAPI
from kafka import TopicPartition

import uvicorn
import aiokafka
import asyncio
import json
import logging
import os
import time

app = FastAPI()

# global variables
consumer_task = None
consumer_1 = None
consumer_2 = None
_state = 0

# env variables
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_CONSUMER_GROUP_PREFIX = os.getenv('KAFKA_CONSUMER_GROUP_PREFIX', 'group')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    log.info('Initializing API ...')
    await initialize()
    await consume()


@app.on_event("startup")
async def logging_startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


@app.on_event("shutdown")
async def shutdown_event():
    log.info('Shutting down API')
    consumer_task.cancel()
    await consumer_1.stop()
    await consumer_2.stop()


async def initialize(init_topics_from_start=True):
    loop = asyncio.get_event_loop()
    # global producer
    global consumer_1
    global consumer_2

    group_id = f'{KAFKA_CONSUMER_GROUP_PREFIX}-{randint(0, 10000)}'
    log.info(f'Initializing KafkaConsumer for topic {KAFKA_TOPIC}, group_id {group_id}'
              f' and using bootstrap servers {KAFKA_BOOTSTRAP_SERVERS}')
    consumer_1 = aiokafka.AIOKafkaConsumer(KAFKA_TOPIC, loop=loop,
                                         bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                                         group_id=f'{KAFKA_CONSUMER_GROUP_PREFIX}-1')
    consumer_2 = aiokafka.AIOKafkaConsumer(KAFKA_TOPIC, loop=loop,
                                         bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                                         group_id=f'{KAFKA_CONSUMER_GROUP_PREFIX}-2')
    # get cluster layout and join group
    await consumer_1.start()
    await consumer_2.start()
    consumers = [consumer_1, consumer_2]

    for consumer in consumers:
        partitions: Set[TopicPartition] = consumer.assignment()

        nr_partitions = len(partitions)
        if nr_partitions != 1:
            log.warning(f'Found {nr_partitions} partitions for topic {KAFKA_TOPIC}. Expecting '
                        f'only one, remaining partitions will be ignored!')
        for tp in partitions:

            # get the log_end_offset
            end_offset_dict = await consumer.end_offsets([tp])
            end_offset = end_offset_dict[tp]

            if init_topics_from_start:

                if end_offset == 0:
                    log.warning(f'Topic ({KAFKA_TOPIC}) has no messages (log_end_offset: '
                                f'{end_offset}), skipping initialization ...')
                    return

                log.debug(f'Found log_end_offset: {end_offset} seeking to {end_offset-1}')
                consumer.seek(tp, end_offset-1)
                msg = await consumer.getone()
                log.info(f'Initializing API with data from msg: {msg}')

                # update the API state
                _update_state(msg.value)


async def consume():
    global consumer_task
    consumer_1_task = asyncio.create_task(read_consumer_message(consumer_1))
    consumer_2_task = asyncio.create_task(read_consumer_message(consumer_2))


async def read_consumer_message(consumer):
    try:
        # consume messages
        async for msg in consumer:
            # x = json.loads(msg.value)
            now = datetime.datetime.now()
            time_to_wait = random.randrange(1,3)
            time.sleep(time_to_wait)
            log.info(f"Consumed from consumer msg: {msg} content {msg.value} started at {now} waited {time_to_wait}")
            # update the API state
            _update_state(msg.value)
    except Exception as e:
        log.exception('Exception while consuming message')
        # will leave consumer group; perform autocommit if enabled
        log.warning('Stopping consumer')
        await consumer.stop()


def _update_state(message: Any) -> None:
    value = json.loads(message)
    global _state
    _state = value['message']
