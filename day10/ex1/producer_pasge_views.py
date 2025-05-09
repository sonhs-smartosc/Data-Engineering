import time
import json
import random
from kafka import KafkaProducer

KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'page_views'

def serialize_data(data):
    """Serialize data (dictionary) to JSON bytes."""
    try:
        return json.dumps(data).encode('utf-8')
    except TypeError as e:
        print(f"Error serializing data: {e}")
        return None

def generate_page_view_event():
    """Generate a random page view event dictionary."""
    users = ["user_A", "user_B", "user_C", "user_D", "user_E"]
    pages = ["/", "/products", "/about", "/contact", "/blog/post-1"]

    user_id = random.choice(users)
    page_url = random.choice(pages)
    # Timestamp in milliseconds since epoch - important for Spark event-time processing
    timestamp_ms = int(time.time() * 1000)

    return {
        'user_id': user_id,
        'page_url': page_url,
        'timestamp': timestamp_ms
    }

def run_producer():
    """Runs the Kafka producer logic."""
    print(f"Connecting producer to Kafka broker at {KAFKA_BROKER}")
    producer = None
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=serialize_data,
        )
        print("Producer connected successfully.")
        print(f"Sending page view events to topic '{TOPIC_NAME}'...")

        while True:
            event = generate_page_view_event()
            print(f"Sending event: {event}")
            future = producer.send(TOPIC_NAME, value=event, timestamp_ms=event['timestamp'])

            time.sleep(0.1) #

    except KeyboardInterrupt:
        print("\nStopping producer.")
    except Exception as e:
        print(f"An error occurred in the producer: {e}")
    finally:
        if producer:
            producer.flush()
            producer.close()
            print("Producer connection closed.")

if __name__ == "__main__":
    run_producer()