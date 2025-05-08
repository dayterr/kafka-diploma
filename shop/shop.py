import argparse
import json
import logging
import os
import sys

BDE_PATH = '../bde/bde.json'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
    prog='ShopAPIParser',
    description='Reads the file',
    epilog='See you again')

parser.add_argument('filename')
args = parser.parse_args()

if not args.filename:
    logger.error('no file')
    sys.exit(1)

if not args.filename.endswith('.json'):
    logger.error('incorrect file format')
    sys.exit(1)

with open(args.filename, 'r') as f:
    accept = json.load(f)

with open(BDE_PATH, 'r+', encoding='utf-8') as f:
    bde = {'items': []}
    try:
        bde = json.load(f)
    except json.decoder.JSONDecodeError as e:
        logger.error('failed reading json', e)
        sys.exit(1)
    bde['items'].append(accept)
    f.seek(0)
    json.dump(bde, f, indent=4, ensure_ascii=False)
    logger.info('wrote to bde')
