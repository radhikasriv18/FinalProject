from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType

# 1. Create Spark Session
spark = SparkSession.builder \
    .appName("KafkaSparkStructuredStreaming") \
    .master("spark://spark-master:7077") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Define the schema of the incoming data
schema = StructType() \
    .add("patient_id", StringType()) \
    .add("heart_rate", DoubleType()) \
    .add("temperature", DoubleType()) \
    .add("timestamp", StringType())  # We'll parse timestamp if needed

# 3. Read from Kafka
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092") \
    .option("subscribe", "iot_patient_data") \
    .option("startingOffsets", "latest") \
    .load()

# 4. Parse JSON payload
parsed_df = raw_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# 5. Optional: Basic data cleaning
clean_df = parsed_df.filter(
    (col("heart_rate").isNotNull()) &
    (col("temperature").isNotNull()) &
    (col("patient_id").isNotNull())
)

# 6. Write output into HDFS
query = clean_df.writeStream \
    .format("parquet") \
    .option("checkpointLocation", "hdfs://172.19.0.4:9000/tmp/spark_checkpoint/") \
    .option("path", "hdfs://172.19.0.4:9000/data/iot_patient_data/") \
    .outputMode("append") \
    .start()

query.awaitTermination()
