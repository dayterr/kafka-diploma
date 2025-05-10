import json
import logging

from confluent_kafka import Producer
from flask import Flask, request

GOODS_TOPIC = 'goods'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def delivery_report(err, msg):
    if err is not None:
        logging.error(f'error when sending: {err}')
    else:
        logging.info('message sent')


conf = {
    "bootstrap.servers": "kafka-0:9092,kafka-1:9092,kafka-2:9092",
    "acks": "1",
    "retries": 5,

    'security.protocol': 'SASL_SSL',
    'ssl.ca.location': 'ca.crt',  # Сертификат центра сертификации
    'ssl.certificate.location': 'kafka.crt',  # Сертификат клиента Kafka
    'ssl.key.location': 'kafka.key',  # Приватный ключ для клиента Kafka

    'sasl.mechanism': 'PLAIN',  # Используемый механизм SASL (PLAIN)
    'sasl.username': 'alice',  # Имя пользователя для аутентификации
    'sasl.password': 'alice-secret',  # Пароль пользователя для аутентификации
}
producer = Producer(conf)

app = Flask(__name__)


@app.route('/add/<filename>', methods=['GET'])
def hello_world(filename):
    filename = 'data/' + filename

    with open(filename, 'r') as f:
        accept = json.load(f)

    logger.info(f'file opened')
    producer.produce(topic=GOODS_TOPIC, value=json.dumps(accept).encode('utf-8'), callback=delivery_report)
    producer.flush()
    logger.info(f'item sent to {GOODS_TOPIC}')
    return json.loads('{}'), 200
