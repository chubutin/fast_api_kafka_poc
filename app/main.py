from random import randint
import json
import logging
import os
from random import randint
from typing import Any

import aiokafka
from fastapi import FastAPI

app = FastAPI()

# global variables
producer = None
_state = 0

# env variables
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_CONSUMER_GROUP_PREFIX = os.getenv('KAFKA_CONSUMER_GROUP_PREFIX', 'group')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.on_event("startup")
async def startup_event():
    log.info('Initializing API ...')
    await initialize()


@app.on_event("startup")
async def logging_startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


@app.on_event("shutdown")
async def shutdown_event():
    log.info('Shutting down API')
    await producer.stop()


@app.get("/send_message")
async def send_message():
    try:
        for i in range(0,50):
            await producer.send(KAFKA_TOPIC, bytes(json.dumps({"message": "Super message %s" % i}), encoding='utf8'))
    except Exception as e:
        log.exception('Exception while sending message')


@app.get("/state")
async def state():
    return {"state": _state}


async def initialize():
    global producer

    producer = aiokafka.AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()

    group_id = f'{KAFKA_CONSUMER_GROUP_PREFIX}-{randint(0, 10000)}'
    log.info(f'Initializing KafkaConsumer for topic {KAFKA_TOPIC}, group_id {group_id}'
              f' and using bootstrap servers {KAFKA_BOOTSTRAP_SERVERS}')



def _update_state(message: Any) -> None:
    value = json.loads(message)
    global _state
    _state = value['message']
