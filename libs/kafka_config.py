class KafkaConfig:
    class BaseConsumerConfig:
        """
        Generic Consumer Config. 
        Inherit this class for specific consumers to maintain uniform configurations.
        """
        TOPICS = []
        GROUP = ""
        MAX_POLL_INTERVAL_MS = 300000
        MAX_POLL_RECORDS = 5
        AUTO_OFFSET_RESET = "latest"
        API_VERSION = (2, 0, 1)