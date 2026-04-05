from libs.kafka.base_consumer import BaseConsumer
from libs.kafka_config import KafkaConfig


class Consumer(BaseConsumer):
    def consume_data(self, data, current_topic):
        # Implementation goes here. Return True on success, False on failure.
        print(f"Custom logic processing topic {current_topic} with data: {data}")
        return True


if __name__ == "__main__":
    Consumer(KafkaConfig.BaseConsumerConfig).listen()