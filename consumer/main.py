import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

def main():
    #tích hợp thư viện để spark tương tác được với kafka
    spark = SparkSession.builder.appName("WeatherSreamingConsumer")\
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0").getOrCreate()
    #Lọc các thông báo rác
    spark.sparkContext.setLogLevel("WARN")

    # Bộ khung tĩnh để ép kiểu dữ liệu nhận về
    schema = StructType([
        StructField("temperature", DoubleType()),
        StructField("windspeed", DoubleType()),
        StructField("winddirection", DoubleType()),
        StructField("weathercode", DoubleType()),
        StructField("time", StringType()),
        StructField("timestamp", DoubleType())
    ])
    # Đọc dữ liều từ Kafka
    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    topic = os.getenv("WEATHER_TOPIC", "weather_data")

    # Nguồn cung cấp dữ liệu streaming là Kafka
    # Tắt tính năng tự động đánh dấu trang của Kafka
    df = spark.readStream.format("kafka")\
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", topic) \
        .option("group.id", "weather-consumer-group") \
        .option("startingOffsets", "earliest") \
        .load()
    #   .option("kafka.enable.auto.commit", "false") \
    #JSON - Giải mã dữ liệu
    # Chuyển đổi kiểu dữ sang chuỗi văn bản - truyền chuỗi văn bảng vào schema (data)
    weather_df = df.selectExpr("CAST(value as STRING)").select(from_json(col("value"), schema).alias("data"))\
                .select("data.*").withColumn("event_time", col("timestamp").cast(TimestampType()))
    #Chuyển các thuộc tính trong gói data thành các cột độc lập trong bảng - ép kiểu sang định dạng thời gian chuẩn

    #Transformation - Biến đổi và tính toán
    #Dữ liệu đến trễ vẫn được đối chiếu vào khung giờ để tính toán
    #Nhóm luồng dữ liệu thành các khối thời gian 9h10 - 9h15
    #Tính nhiệt độ trung bình cho toàn bộ các bản ghi được truyền vào khối thời gian 5phuts
    avg_tmp_df = weather_df.withWatermark("event_time", "10 minutes")\
                .groupBy(window(col("event_time"),"5 minutes")).agg(avg("temperature").alias("average_tmp"))

    #Xuất kết quả
    query = avg_tmp_df.writeStream.outputMode("complete").format("console")\
            .option("checkpointLocation", "/tmp/checkpoints/weather_stats")\
            .trigger(processingTime='10 seconds').start()

    # option("group.id", "weather-consumer-group")
            # Ghi lại tiến trình xuống ô cứng, sẽ đọc file này nếu máy ảo bị sập
    query.awaitTermination()

if __name__=="__main__":
    main()