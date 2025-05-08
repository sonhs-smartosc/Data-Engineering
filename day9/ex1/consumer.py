import time
import json
from kafka import KafkaConsumer


KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'random_events'
CONSUMER_GROUP_ID = 'my_consumer_group'


def deserialize_data(data):
    """Deserialize JSON bytes to a dictionary."""
    try:
        return json.loads(data.decode('utf-8'))
    except json.JSONDecodeError:
        print("Error decoding JSON from message")
        return None

def run_consumer():
    """Runs the Kafka consumer logic."""
    print(f"Connecting consumer to Kafka broker at {KAFKA_BROKER}")
    consumer = None
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=CONSUMER_GROUP_ID,
            value_deserializer=deserialize_data
        )
        print(f"Consumer connected successfully to topic '{TOPIC_NAME}' in group '{CONSUMER_GROUP_ID}'.")
        print("Listening for messages...")

        time.sleep(5)
        try:
             consumer.partitions_for_topic(TOPIC_NAME)
             print(f"Confirmed connection to topic '{TOPIC_NAME}'.")
        except Exception as e:
             print(f"Could not get initial partitions for topic '{TOPIC_NAME}': {e}. Proceeding, hope topic appears.")


        for message in consumer:
            event = message.value

            if event:
                print(f"Received event: {event} (Partition: {message.partition}, Offset: {message.offset})")

    except KeyboardInterrupt:
        print("\nStopping consumer.")
    except Exception as e:
        print(f"An error occurred in the consumer: {e}")
    finally:
        if consumer:
            consumer.close()
            print("Consumer connection closed.")

if __name__ == "__main__":
    run_consumer()