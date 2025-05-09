import json
import logging

import faust

from .extra.constants import (BDE_PATH, BLOCKED_GOODS,
                              FILTERED_GOODS_TOPIC,
                              GOODS_TOPIC)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = faust.App(
    'my-faust-app',
    broker="127.0.0.1:9093,127.0.0.1:9094,127.0.0.1:9095",
    value_serializer='raw'
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
