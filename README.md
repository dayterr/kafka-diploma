# kafka-diploma

## Запуск кластера 

команда:  
`docker compose up -d`

## Возможные проблемы с Kafka Connect

Описаны [здесь](https://github.com/dayterr/kafka-diploma/blob/main/kafka-connect/README.md)

## Добавление хостов

Нужно добавить в `/etc/hosts` следующие хосты:

```
172.23.0.21      kafka-1
172.23.0.20      kafka-0
172.23.0.23      kafka-2
```

## Создание топиков

зайти в контейнер брокера. команда:  
`docker exec -it kafka-1 bash`

создать конфиг следующего вида:
```
echo 'security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="admin" password="admin-secret";
# Path to the keystore (if client authentication is required)
ssl.keystore.location=/etc/kafka/secrets/kafka.kafka.keystore.pkcs12
ssl.keystore.password=your-password
ssl.key.password=your-password
# Path to the truststore
ssl.truststore.location=/etc/kafka/secrets/kafka.kafka.truststore.jks
ssl.truststore.password=your-password
ssl.endpoint.identification.algorithm=' >> prop.cfg
```

создать топики. команда:  
```
kafka-topics --bootstrap-server localhost:9092 --topic goods --create --partitions 1 --replication-factor 1
```

```
kafka-topics --bootstrap-server localhost:9092 --topic filtered-goods --create --partitions 1 --replication-factor 1
```

```
kafka-topics --bootstrap-server localhost:9092 --topic queries --create --partitions 1 --replication-factor 1
```

```
kafka-topics --bootstrap-server localhost:9092 --topic recommendations --create --partitions 1 --replication-factor 1
```

дать права. команда:  

```
kafka-acls --bootstrap-server localhost:9092 \
--add \
--allow-principal User:alice \
--operation write \
--operation create \
--topic goods \
--topic filtered_goods \
--topic queries \
--topic recommendations
```

## Запуск SHOP API

Описано [здесь](https://github.com/dayterr/kafka-diploma/blob/main/shop/README.md)

## Запуск censor

Описано [здесь](https://github.com/dayterr/kafka-diploma/blob/main/censor/README.md)

## Запуск bde

Описано [здесь](https://github.com/dayterr/kafka-diploma/blob/main/bde/README.md)