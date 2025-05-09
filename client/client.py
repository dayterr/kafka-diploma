import argparse
import json
import logging
from random import randint
import sys

BDE_PATH = '../bde/bde.json'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
    prog='ClientAPIParser',
    description='Reads the file',
    epilog='See you again')

parser.add_argument('-s', '--search')
parser.add_argument('-r', '--recommendation')
args = parser.parse_args()

if args.search is None and args.recommendation is None:
    logger.error('unknown argument')
    sys.exit(1)

with open(BDE_PATH, 'r+', encoding='utf-8') as f:
    bde = {'items': []}
    try:
        bde = json.load(f)
    except json.decoder.JSONDecodeError as e:
        logger.error('failed reading json', e)
        sys.exit(1)

if args.search:
    res = []
    for item in bde['items']:
        if args.search.lower() in item['name'].lower():
            res.append(item)
    if res:
        print(f'found:\n{res}')
    else:
        print('nothing found')

if args.recommendation:
    if not bde['items']:
        print('рекомендации отсутствуют')
    ind = randint(0, len(bde['items']))
