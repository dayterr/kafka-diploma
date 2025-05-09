## Конфигурация нужного коннектора
1. выведем основную информацию о кластере. команда:  
`curl -s localhost:8083`
ответ:
```
{
    "version": "7.7.1-ccs",
    "commit": "91d86f33092378c89731b4a9cf1ce5db831a2b07",
    "kafka_cluster_id": "Ad5KRh8MRlyNEX1jGK5www"
}
```

2. посмотрим на установленные плагины. команда:  
`curl localhost:8083/connector-plugins`
ответ:
```
[
    {
        "class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
        "type": "sink",
        "version": "7.7.1-ccs"
    },
    {
        "class": "org.apache.kafka.connect.file.FileStreamSourceConnector",
        "type": "source",
        "version": "7.7.1-ccs"
    },
    {
        "class": "org.apache.kafka.connect.mirror.MirrorCheckpointConnector",
        "type": "source",
        "version": "7.7.1-ccs"
    },
    {
        "class": "org.apache.kafka.connect.mirror.MirrorHeartbeatConnector",
        "type": "source",
        "version": "7.7.1-ccs"
    },
    {
        "class": "org.apache.kafka.connect.mirror.MirrorSourceConnector",
        "type": "source",
        "version": "7.7.1-ccs"
    }
]
```

3. сконфигурируем коннектор. команда:  
```
curl -X PUT \
-H "Content-Type: application/json" \
--data '{
"name": "file-stream-sink",
"connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
"tasks.max": "1",
"topics": "filtered_goods",
"file": "bde.json",
"value.converter": "org.apache.kafka.connect.storage.StringConverter"
}' \
http://localhost:8083/connectors/file-stream-sink/config
```
ответ:
```
{
    "name": "file-stream-sink",
    "config": {
        "name": "file-stream-sink",
        "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
        "tasks.max": "1",
        "topics": "filtered_goods",
        "file": "bde.json",
        "value.converter": "org.apache.kafka.connect.storage.StringConverter"
    },
    "tasks": [],
    "type": "sink"
}
```

4. проверим статус коннектора. команда:  
`curl http://localhost:8083/connectors/file-stream-sink/status`
ответ:
```
{
    "name": "file-stream-sink",
    "connector": {
        "state": "RUNNING",
        "worker_id": "localhost:8083"
    },
    "tasks": [
        {
            "id": 0,
            "state": "RUNNING",
            "worker_id": "localhost:8083"
        }
    ],
    "type": "sink"
}
```


## Возможные проблемы

1. выключается контейнер kafka-connect
решение:  
зайти в контейнер. команда:  
`docker exec -it kafka-0 bash`  

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

дать доступ к топикам. команда:
```
kafka-acls --bootstrap-server localhost:9092 \
--add \
--allow-principal User:alice \
--operation All \
--topic connect-offset-storage \
--topic connect-status-storage \
--topic connect-config-storage \
--group kafka-connect \
--command-config prop.cfg
```

перезапустить контейнер.