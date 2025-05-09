import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def delivery_report(err, msg):
    if err is not None:
        logging.error(f'error when sending: {err}')
    else:
        logging.info('message sent')
