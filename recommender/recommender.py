import logging

from confluent_kafka import Producer
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
   col,
   count,
   from_json,
)
from pyspark.sql.types import (
   StringType,
   StructField,
   StructType,
)

QUERIES_TOPIC = 'queries'
RECOMMENDATIONS_TOPIC = 'recommendations'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

conf = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094,localhost:9095,localhost:9097,localhost:9098',
    'acks': '1',
    'retries': 5,

    'security.protocol': 'SASL_SSL',
    'ssl.ca.location': 'ca.crt',
    'ssl.certificate.location': 'kafka.crt',
    'ssl.key.location': 'kafka.key',

    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'alice',
    'sasl.password': 'alice-secret',
}
producer = Producer(conf)


def send_to_kafka(batch_df, batch_id):
    if not batch_df.isEmpty():
        message = batch_df.collect()[0]['message']
        logger.info(f'Самое популярное сообщение: {message}')
        producer.send(RECOMMENDATIONS_TOPIC, value=message)
        logger.info(f'message sent to {RECOMMENDATIONS_TOPIC}')


schema = StructType([
   StructField('message', StringType(), True),
])


if __name__ == '__main__':
    spark = SparkSession.builder.appName(
        'StreamingAggregator[PySpark]'
        ).master('local[*]').getOrCreate()

    kafka_df = spark.readStream.format('kafka').option(
        'kafka.bootstrap.servers',
        'localhost:9092,localhost:9093,localhost:9094,localhost:9095,localhost:9097,localhost:9098',
        ).option(
            'subscribe',
            QUERIES_TOPIC,
        ).option(
            'startingOffsets',
            'earliest',
        ).load()

    json_df = kafka_df.select(
        from_json(
            col('value').cast('string'),
            schema,
            ).alias('data')).filter(col('data').isNotNull())

    parsed_df = json_df.select(
        col('data.message').alias('message'),
        )

    message_count_df = parsed_df.groupBy(
        'message'
        ).agg(
            count('message').alias('counter')
        )

    popular_message_df = message_count_df.orderBy(
        col('counter').desc()
    ).limit(1)

    query = popular_message_df.writeStream.foreachBatch(send_to_kafka).start()
    logger.info('Запуск обработки данных из Kafka...')
    query.awaitTermination()
