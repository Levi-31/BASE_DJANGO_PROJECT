import json
import os
import sys
import time
import traceback
import logging
import threading

import django

# Initialize Django environment safely before anything else happens
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.local")
django.setup()

from abc import ABC

from django.conf import settings
from kafka import KafkaConsumer
from kafka.structs import OffsetAndMetadata, TopicPartition


logger = logging.getLogger("KafkaBaseConsumer")

# Thread-local storage to track request_id across consumer execution
# Dropped log_request_id dependency to ensure it works cleanly without third-party tools
local = threading.local()

# --- Mocking missing dependencies for generic usage ---
class MockAlertManager:
    @staticmethod
    def send_medium_priority_alert(message):
        logger.error(f"[MEDIUM PRIORITY ALERT]: {message}")

AlertManager = MockAlertManager()
# ----------------------------------------------------


class BaseConsumer(ABC):
    def __init__(self, KAFKA_CONFIG):
        self.topics = KAFKA_CONFIG.TOPICS
        self.consumer = KafkaConsumer(
            *KAFKA_CONFIG.TOPICS,
            bootstrap_servers=settings.CACHES["default"].get("LOCATION", "redis://127.0.0.1:6379/1") if not hasattr(settings, "KAFKA_URLS") else settings.KAFKA_URLS,  # Fallback to defaults
            group_id=KAFKA_CONFIG.GROUP,
            auto_offset_reset=KAFKA_CONFIG.AUTO_OFFSET_RESET,
            api_version=KAFKA_CONFIG.API_VERSION,
            max_poll_interval_ms=KAFKA_CONFIG.MAX_POLL_INTERVAL_MS,
            max_poll_records=KAFKA_CONFIG.MAX_POLL_RECORDS,
        )

    def listen(self):
        logger.info("-------------------------------------START LISTEN---------------------------------------------")

        for msg in self.consumer:
            start_time = time.time()
            request_id = f"T{msg.topic}_P{msg.partition}_O{msg.offset}_{start_time}"
            local.request_id = request_id

            try:
                logger.debug("-------------------------------------START MESSGE PROCESSING---------------------------------------------")
                data = self.extract_data(msg)
                if not data:
                    continue

                current_topic = msg.topic
                logger.info(f"Data going to consumer {current_topic} :{data}")

                success = self.consume_data(data, current_topic)
                logger.info(f"Data came after consumer with success :{success}")

                if success:
                    self.close_old_connections()
                    self.commit_message(msg)
                else:
                    message = f"*Failure in data: Not consumed {msg.topic}* {data}"
                    AlertManager.send_medium_priority_alert(message)

            except Exception as e:
                self.close_old_connections()
                message = f"*Error in consumer {msg.topic}* {msg.value} {e}\n{traceback.format_exc()}"
                AlertManager.send_medium_priority_alert(message)
                continue

            logger.info(f"TIME TAKEN :{time.time() - start_time}")
            logger.debug("-------------------------------------END MESSAGE PROCESSING---------------------------------------------")

    def close_old_connections(self):
        django.db.close_old_connections()

    def extract_data(self, msg):
        try:
            data = msg.value.decode("utf-8")
        except AttributeError:
            data = msg.value
        
        if not data:
            message = f"No data received in consumer {msg.topic}"
            AlertManager.send_medium_priority_alert(message)
            self.commit_message(msg)
            return None

        try:
            data = json.loads(data)
        except Exception:
            message = f"JSON parsing error - {data} in consumer {msg.topic}"
            AlertManager.send_medium_priority_alert(message)
            self.commit_message(msg)
            return None

        return data

    def commit_message(self, msg):
        try:
            tp = TopicPartition(msg.topic, msg.partition)
            offsets = {tp: OffsetAndMetadata(msg.offset + 1, None)}
            self.consumer.commit(offsets=offsets)
            logger.info(f"Committed offset {msg.offset + 1} for topic {msg.topic}")
        except Exception as e:
            logger.warning(f"Error committing message offset: {str(e)}")

    def consume_data(self, data, current_topic):
        """
        To be implemented by child classes.
        Must return boolean indicating success.
        """
        raise NotImplementedError("Child consumer class must implement 'consume_data' method")
