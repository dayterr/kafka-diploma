import argparse
import json
import logging
import sys

from confluent_kafka import Producer

from ..extra.callbalcks import delivery_report
from ..extra.constants import GOODS_TOPIC

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
    prog='ShopAPIParser',
    description='Reads the file',
    epilog='See you again')

parser.add_argument('filename')
args = parser.parse_args()

conf = {
    "bootstrap.servers": "127.0.0.1:9094,127.0.0.1:9095,127.0.0.1:9096",
    "acks": "all",
    "retries": 5,
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

producer.produce(topic=GOODS_TOPIC, value=accept, callback=delivery_report)
producer.flush()
logger.info(f'item sent to {GOODS_TOPIC}')
