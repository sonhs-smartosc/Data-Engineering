import time
import json
import random
from kafka import KafkaProducer

KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'random_events'

def serialize_data(data):
    """Serialize data (dictionary) to JSON bytes."""
    try:
        return json.dumps(data).encode('utf-8')
    except TypeError as e:
        print(f"Error serializing data: {e}")
        return None

def generate_random_event():
    """Generate a random event dictionary."""
    event_id = random.randint(1000, 9999)
    value = round(random.uniform(0, 100), 2)
    timestamp = int(time.time() * 1000) # Milliseconds
    return {
        'event_id': event_id,
        'value': value,
        'timestamp': timestamp,
        'message': f"Random event {event_id}"
    }

def run_producer():
    """Runs the Kafka producer logic."""
    print(f"Connecting producer to Kafka broker at {KAFKA_BROKER}")
    producer = None
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=serialize_data
        )
        print("Producer connected successfully.")
        print(f"Sending random events to topic '{TOPIC_NAME}'...")

        while True:
            event = generate_random_event()
            serialized_event = serialize_data(event)
            if serialized_event is not None:
                print(f"Sending event: {event}")
                producer.send(TOPIC_NAME, value=event)

            time.sleep(1)

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