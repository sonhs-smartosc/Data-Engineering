import json
import time
from datetime import datetime, timedelta
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable, KafkaError

# --- Cấu hình Kafka và Windowing ---
KAFKA_BROKER = 'localhost:9092' # Địa chỉ Kafka broker
TOPIC_NAME = 'random_events'   # Tên topic
CONSUMER_GROUP_ID = 'manual_aggregator_group' # ID của nhóm consumer
WINDOW_SIZE_SECONDS = 60 # Kích thước cửa sổ: 1 phút
WINDOW_SIZE_MS = WINDOW_SIZE_SECONDS * 1000

# --- Hàm hỗ trợ Deserialize ---
def deserialize_data(data):
    """Deserialize JSON bytes to a dictionary."""
    if data is None: # Handle potential None data
        # print("Received None data")
        return None
    try:
        return json.loads(data.decode('utf-8'))
    except json.JSONDecodeError:
        # print("Error decoding JSON from message") # Avoid excessive logging for bad messages
        return None
    except Exception as e:
        print(f"Unexpected error during deserialization: {e}")
        return None

# --- Logic Consumer với Manual Aggregation ---
def run_consumer():
    """Runs the Kafka consumer logic and performs manual aggregation."""
    print(f"Connecting consumer to Kafka broker at {KAFKA_BROKER}")
    consumer = None
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset='earliest', # Bắt đầu đọc từ đầu nếu chưa có offset
            enable_auto_commit=True,     # Tự động commit offset
            group_id=CONSUMER_GROUP_ID,  # ID nhóm consumer
            value_deserializer=deserialize_data,
            # Configure the consumer to use the message timestamp (producer or broker time)
            # If message timestamps are not available, Kafka uses append time by default.
            # For event-time windowing, producer timestamps are best.
            # Kafka client uses message.timestamp by default if available.

            # Set consumer timeout to allow checking for new messages periodically if needed
            # consumer_timeout_ms=1000 # Example timeout: exit loop if no messages in 1s
        )
        print(f"Consumer connected successfully to topic '{TOPIC_NAME}' in group '{CONSUMER_GROUP_ID}'.")
        print(f"Starting aggregation: Count events per {WINDOW_SIZE_SECONDS} seconds.")
        print("Listening for messages...")

        # --- State for Aggregation ---
        current_window_start_ms = None # Timestamp (ms) of the start of the current window
        current_window_count = 0     # Count of events in the current current_window_start_ms
        last_processed_timestamp_ms = 0 # Keep track of the timestamp of the last processed message

        # Optional: Wait for the topic to be created if the consumer starts first
        # Give Kafka some time to register the topic after producer sends first message
        # Or if the consumer is started before the producer
        time.sleep(5)
        try:
             # Check if partitions exist for the topic
             partitions = consumer.partitions_for_topic(TOPIC_NAME)
             if not partitions:
                 print(f"Topic '{TOPIC_NAME}' has no partitions yet or no brokers available. Waiting...")
                 # Wait longer if topic is not found initially
                 # We'll rely on the consumer loop to block until messages arrive and topic is ready
             else:
                  print(f"Confirmed connection to topic '{TOPIC_NAME}' with partitions: {partitions}.")
        except NoBrokersAvailable as e:
             print(f"No Kafka brokers available at startup: {e}. Ensure Kafka is running.")
             return # Exit if brokers not found
        except Exception as e:
             print(f"Could not get initial partitions for topic '{TOPIC_NAME}': {e}. Proceeding, hope topic appears.")


        # --- Message Consumption Loop ---
        # The loop blocks until a message is available or timeout occurs (if set)
        for message in consumer:
            try:
                # message.timestamp is the event timestamp (producer time if configured)
                # message.value is the deserialized Python object (dict in this case)

                event_timestamp_ms = message.timestamp # Get Kafka's message timestamp (ms)
                event_data = message.value             # Get the deserialized event data

                # We only process messages with valid timestamps and data
                if event_timestamp_ms is None or event_data is None:
                    if event_timestamp_ms is None:
                        print(f"Skipping message without timestamp: Partition {message.partition}, Offset {message.offset}")
                    if event_data is None:
                         print(f"Skipping message with None value (deserialization failed?): Partition {message.partition}, Offset {message.offset}")
                    continue # Skip to the next message

                # Basic check to handle potential out-of-order messages if not strictly sequential
                # This is a simplification; proper out-of-order handling in streams is complex (requires buffering)
                # For this simple counter, we'll assume messages are mostly in order or close
                if event_timestamp_ms < last_processed_timestamp_ms:
                     print(f"Received potentially out-of-order message (current ts: {event_timestamp_ms}, last processed: {last_processed_timestamp_ms}). Processing anyway...")
                last_processed_timestamp_ms = max(last_processed_timestamp_ms, event_timestamp_ms)


                # Calculate the start time of the window this event belongs to
                # We use integer division to round down to the nearest window interval
                # Example: timestamp 65s (65000ms) with 60s window (60000ms) -> 65000 // 60000 * 60000 = 1 * 60000 = 60000ms (start of the minute)
                event_window_start_ms = (event_timestamp_ms // WINDOW_SIZE_MS) * WINDOW_SIZE_MS


                # Initialize the first window when the very first relevant message arrives
                if current_window_start_ms is None:
                    current_window_start_ms = event_window_start_ms
                    print(f"\nInitialized first window starting at: {datetime.fromtimestamp(current_window_start_ms / 1000)}")
                    current_window_count = 0 # Start count for the very first window


                # Check if this message belongs to a new window based on its timestamp
                if event_window_start_ms > current_window_start_ms:
                    # --- A new window has started, report the count for the previous window ---
                    # Calculate the end time of the previous window for printing
                    previous_window_end_ms = current_window_start_ms + WINDOW_SIZE_MS - 1 # End timestamp (inclusive)

                    print(f'\n--- Window Closed ({datetime.fromtimestamp(current_window_start_ms / 1000)} to {datetime.fromtimestamp(previous_window_end_ms / 1000)}) ---')
                    print(f"Total events in window: {current_window_count}")
                    print('----------------------------------------------\n')

                    # --- Reset for the new window this message belongs to ---
                    current_window_start_ms = event_window_start_ms
                    current_window_count = 1 # Start count for the new window with the current message
                    print(f"New window started at: {datetime.fromtimestamp(current_window_start_ms / 1000)}")

                else:
                    # --- The message belongs to the current window ---
                    current_window_count += 1
                    # Optional: Print every message received (can be chatty)
                    # print(f"Received event: {event_data} (TS: {event_timestamp_ms}, Partition: {message.partition}, Offset: {message.offset}) - Count in current window: {current_window_count}")

            except KafkaError as e:
                 print(f"Kafka error while consuming message: {e}")
                 # Decide how to handle: continue, retry, exit?
                 # For basic script, often just log and continue
            except Exception as e:
                print(f"An unexpected error occurred while processing message: {e}")
                # Log the error and continue processing other messages

    except KeyboardInterrupt:
        print("\nStopping consumer.")
    except NoBrokersAvailable as e:
         print(f"Could not connect to Kafka brokers: {e}. Ensure Kafka is running and accessible.")
    except Exception as e:
        print(f"An error occurred in the consumer loop: {e}")
    finally:
        # Report the count for the last potentially incomplete window before closing
        if current_window_start_ms is not None:
             current_time_ms = int(time.time() * 1000)
             print(f'\n--- Final (potentially incomplete) Window ({datetime.fromtimestamp(current_window_start_ms / 1000)} to {datetime.fromtimestamp(current_time_ms / 1000)}) ---')
             print(f"Total events counted so far: {current_window_count}")
             print('----------------------------------------------\n')

        # Ensure consumer is closed
        if consumer:
            consumer.close()
            print("Consumer connection closed.")

# --- Điểm thực thi chính ---
if __name__ == "__main__":
    run_consumer()
