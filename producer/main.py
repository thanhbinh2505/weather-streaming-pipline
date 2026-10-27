import os
import time
import json

import requests
from kafka import KafkaProducer

from dotenv import load_dotenv
from loguru import logger

# 1. Nạp cấu hình hệ thống
load_dotenv()
KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("WEATHER_TOPIC", "weather_data")
LAT = os.getenv("LAT", "10.7626") #Vĩ độ
LON = os.getenv("LON", "106.6601")#Kinh độ
INTERVAL = int(os.getenv("FETCH_INTERVAL_SECONDS", 60))

# 2. Thiết lập Kafka Producer
# Lưu ý: value_serializer tự động chuyển thành chuỗi byte JSON
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def fetch_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        weather = data.get("current_weather", {})
        weather["timestamp"] = time.time()
        weather["location"] = {"lat": LAT, "lon": LON}
        
        return weather
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None

def main():
    logger.info("Starting Weather Producer...")
    while True:
        data = fetch_weather()
        if data:
            producer.send(TOPIC, value=data)
            logger.info(f"Sent to Kafka: {data['temperature']}°C at {data['time']}")
        
        # tạm nhưng hệ thống để chở tới đợt lấy dữ liệu khác
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()