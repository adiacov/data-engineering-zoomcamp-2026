from kafka import KafkaConsumer
from streaming.ride import Ride


def main():
    print("[INFO] Starting consumer APP")

    topic = "test-topic"

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=["localhost:19092"],
        client_id="consumer_test_1",
        group_id="consumer_test_group",
        auto_offset_reset="earliest",
        value_deserializer=Ride.value_deserializer,
    )

    try:
        for message in consumer:
            print(
                "%s:%d:%d: key=%s value=%s"
                % (
                    message.topic,
                    message.partition,
                    message.offset,
                    message.key,
                    message.value,
                )
            )
    except KeyboardInterrupt:
        print("\n[INFO] KeyboardInterrupt received, stopping consumer...")

    finally:
        consumer.close()  # ensure the consumer shuts down cleanly
        print("[INFO] Consumer APP stopped")


if __name__ == "__main__":
    main()
