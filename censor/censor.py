import json
import logging
import ssl

import faust

BDE_PATH = '../bde/bde.json'
BLOCKED_GOODS = ('Оружие', 'Алкоголь')
FILTERED_GOODS_TOPIC = 'filtered_goods'
GOODS_TOPIC = 'goods'

custom_sep = '\n'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ssl_context = ssl.create_default_context(
    purpose=ssl.Purpose.SERVER_AUTH, cafile='ca.pem')
ssl_context.load_cert_chain('kafka.crt', keyfile='kafka.key')

app = faust.App(
    'my-faust-app',
    broker="localhost:9092,localhost:9093,localhost:9094,localhost:9095,localhost:9097,localhost:9098",
    value_serializer='raw',
    broker_credentials=faust.auth.SASLCredentials(
        username='admin',
        password='admin-secret',
        ssl_context=ssl_context,
    )

)

goods = app.topic(GOODS_TOPIC)
filtered_goods = app.topic(FILTERED_GOODS_TOPIC)


@app.agent(goods)
async def censor_goods(stream):
    async for item in stream:
        if isinstance(item, bytes):
            item = item.decode('utf-8')
            logger.info('json decoded')
        try:
            item = json.loads(item)  
            logger.info('json loaded success')
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
        if item['category'] in BLOCKED_GOODS:
            logger.info('запрещённый к продаже товар')
        else:
            await filtered_goods.send(value=json.dumps(item, ensure_ascii=False).encode('utf-8'))
            logger.info(f'товар отправлен в топик {filtered_goods}')
