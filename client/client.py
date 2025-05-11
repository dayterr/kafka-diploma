import json
import logging

from confluent_kafka import Consumer, KafkaException, Producer
from flask import Flask

BDE_PATH = '../bde/bde.json'
RECOMMENDATIONS_TOPIC = 'recommendations'
QUERIES_TOPIC = 'queries'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

custom_sep = '\n'

def delivery_report(err, msg):
    if err is not None:
        logging.error(f'error when sending: {err}')
    else:
        logging.info('message sent')


conf = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094,localhost:9095,localhost:9097,localhost:9098',
    'acks': '1',
    'retries': 5,

    'security.protocol': 'SASL_SSL',
    'ssl.ca.location': 'ca.crt',  # Сертификат центра сертификации
    'ssl.certificate.location': 'kafka.crt',  # Сертификат клиента Kafka
    'ssl.key.location': 'kafka.key',  # Приватный ключ для клиента Kafka

    'sasl.mechanism': 'PLAIN',  # Используемый механизм SASL (PLAIN)
    'sasl.username': 'alice',  # Имя пользователя для аутентификации
    'sasl.password': 'alice-secret',  # Пароль пользователя для аутентификации
}

cons_conf = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094,localhost:9095,localhost:9097,localhost:9098',
    'group.id': 'kafka',
    'auto.offset.reset': 'earliest',

    'security.protocol': 'SASL_SSL',
    'ssl.ca.location': 'ca.crt',  # Сертификат центра сертификации
    'ssl.certificate.location': 'kafka.crt',  # Сертификат клиента Kafka
    'ssl.key.location': 'kafka.key',  # Приватный ключ для клиента Kafka

    'sasl.mechanism': 'PLAIN',  # Используемый механизм SASL (PLAIN)
    'sasl.username': 'alice',  # Имя пользователя для аутентификации
    'sasl.password': 'alice-secret',  # Пароль пользователя для аутентификации
}

producer = Producer(conf)
consumer = Consumer(cons_conf)
consumer.subscribe([RECOMMENDATIONS_TOPIC])

app = Flask(__name__)

@app.route('/search/<itemname>', methods=['GET'])
def search_itemname(itemname):
    with open(BDE_PATH, 'r+', encoding='utf-8') as f:
        file_content = f.read()
        objects = file_content.split(custom_sep)
        try:
            objects = [json.loads(obj) for obj in objects if obj]
        except json.decoder.JSONDecodeError as e:
            logger.error('failed reading json', e)
            return json.loads('{}'), 503
        res = []
        for obj in objects:
            if itemname.lower() in obj['name'].lower():
                res.append(obj)
        producer.produce(topic=QUERIES_TOPIC, value=json.dumps({'message': itemname}).encode('utf-8'), callback=delivery_report)
        producer.flush()
        logger.info(f'item sent to {QUERIES_TOPIC}')
        return res, 200

@app.route('/recommendations', methods=['GET'])
def recommend():
    rec = ''
    try:
        while True:
            message = consumer.poll(timeout=2.0)
            if message is None:
                continue
            if message.error():
                logger.error(f'Ошибка: {message.error()}')
                continue
            value = message.value().decode('utf-8')
            logger.info(f'Получено сообщение: {value}')
            rec = value
    except KafkaException as e:
        logger.error(f'Failed to {e}')
    return rec, 200
