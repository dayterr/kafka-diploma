import json
import logging
import ssl

import faust

BDE_PATH = '../bde/bde.json'
BLOCKED_GOODS = ('Оружие', 'Алкоголь')
FILTERED_GOODS_TOPIC = 'filtered_goods'
GOODS_TOPIC = 'goods'

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
        if item['category'] in BLOCKED_GOODS:
            logger.info('запрещённый к продаже товар')
        else:
            with open(BDE_PATH, 'r+', encoding='utf-8') as f:
                bde = {'items': []}
                try:
                    bde = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    logger.error('failed reading json', e)
                bde['items'].append(item)
                await filtered_goods.send(value=bde)
                logger.info(f'товар отправлен в топик {filtered_goods}')
