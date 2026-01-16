from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

# 1. Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:29092'],  # Connect to Kafka externally
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Encode JSON
)

# 2. Function to generate random patient data
def generate_patient_data():
    return {
        "patient_id": f"P{random.randint(10000, 99999)}",
        "heart_rate": random.uniform(60, 120),  # bpm
        "temperature": random.uniform(36.5, 39.0),  # Celsius
        "timestamp": datetime.utcnow().isoformat()
    }

# 3. Send messages in a loop
while True:
    message = generate_patient_data()
    producer.send('iot_patient_data', value=message)
    print(f"Sent: {message}")
    time.sleep(1)  # Wait 1 second before sending next message
