from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Создание Spark сессии
spark = SparkSession.builder 
    .appName("Data Processing") 
    .getOrCreate()

# Чтение данных из HDFS
df = spark.read.json("hdfs:///data/local_data.json")

# Пример обработки: подсчет количества элементов
count_items = df.selectExpr("size(items) as item_count").collect()[0]['item_count']

# Вывод результата
print(f"Количество элементов: {count_items}")

# Пример аналитики: если у вас есть данные о пользователях и их оценках
# df.createOrReplaceTempView("items_view")
# recommendations = spark.sql("SELECT user_id, avg(rating) as avg_rating FROM items_view GROUP BY user_id")

# Запись рекомендаций в Kafka
# recommendations.write 
#     .format("kafka") 
#     .option("kafka.bootstrap.servers", "localhost:9092") 
#     .option("topic", "recommendations") 
#     .save()

# Завершение работы Spark
spark.stop()