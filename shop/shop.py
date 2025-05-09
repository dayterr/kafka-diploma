import argparse
import json
import logging
import sys

import os
print(os.getcwd())

from confluent_kafka import Producer

from extra.callbalcks import delivery_report
from extra.constants import GOODS_TOPIC

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
    prog='ShopAPIParser',
    description='Reads the file',
    epilog='See you again')

parser.add_argument('filename')
args = parser.parse_args()

conf = {
    "bootstrap.servers": "127.0.0.1:9093,127.0.0.1:9094,127.0.0.1:9095",
    "acks": "1",
    "retries": 5,

    'security.protocol': 'SASL_SSL',
    'ssl.ca.location': 'ca.crt',  # Сертификат центра сертификации
    'ssl.certificate.location': 'kafka.crt',  # Сертификат клиента Kafka
    'ssl.key.location': 'kafka.key',  # Приватный ключ для клиента Kafka

    'sasl.mechanism': 'PLAIN',  # Используемый механизм SASL (PLAIN)
    'sasl.username': 'admin',  # Имя пользователя для аутентификации
    'sasl.password': 'admin-secret',  # Пароль пользователя для аутентификации
}
producer = Producer(conf)

if not args.filename:
    logger.error('no file')
    sys.exit(1)

if not args.filename.endswith('.json'):
    logger.error('incorrect file format')
    sys.exit(1)

with open(args.filename, 'r') as f:
    accept = json.load(f)

producer.produce(topic=GOODS_TOPIC, value=json.dumps(accept).encode('utf-8'), callback=delivery_report)
producer.flush()
logger.info(f'item sent to {GOODS_TOPIC}')
