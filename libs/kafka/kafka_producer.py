import datetime
import json
import logging
import threading
import traceback
import uuid
from decimal import Decimal
from functools import wraps

from django.conf import settings
from kafka import KafkaProducer

from libs.constant import Constant


logger = logging.getLogger("KafkaProducer")


# --- Mocking missing dependencies for generic usage ---
class MockAlertManager:
    @staticmethod
    def send_kafka_alerts(message):
        logger.error(f"[KAFKA ALERT]: {message}")

    @staticmethod
    def send_transaction_alert(message):
        logger.error(f"[TRANSACTION ALERT]: {message}")


def exception_handler(priority):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"[{priority} PRIORITY ERROR] in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
        return wrapper
    return decorator

AlertManager = MockAlertManager()
# ----------------------------------------------------


def obj_converter(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    elif isinstance(o, datetime.date):
        return o.isoformat()
    elif isinstance(o, Decimal):
        return float(o)
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


def get_kafka_producer_key(data, topic_name):
    key = ""
    return key


@exception_handler(Constant.ExceptionPriority.MEDIUM)
def push_data_in_kafka_async(data, topic_name):
    th = threading.Thread(target=push_data_in_kafka, args=(data, topic_name))
    th.daemon = True
    th.start()


def push_data_in_kafka(data, topic_name, is_retry_call=False):
    key = get_kafka_producer_key(data, topic_name)

    try:
        if key:
            producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_URLS,
                api_version=(2, 0, 1),
                value_serializer=lambda v: json.dumps(v, default=obj_converter).encode("utf-8"),
                batch_size=128,
                key_serializer=lambda m: m.encode("utf8"),
            )
            fmd = producer.send(topic_name, data, key=key)
            if is_retry_call:
                fmd.add_errback(retry_err_back, topic_name, data)
            else:
                fmd.add_errback(err_back, topic_name, data)
            producer.close()

        else:
            producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_URLS,
                api_version=(2, 0, 1),
                value_serializer=lambda v: json.dumps(v, default=obj_converter).encode("utf-8"),
                batch_size=128,
            )
            fmd = producer.send(topic_name, data)
            if is_retry_call:
                fmd.add_errback(retry_err_back, topic_name, data)
            else:
                fmd.add_errback(err_back, topic_name, data)
            producer.close()
    except Exception as e:
        if is_retry_call:
            message = f"*Error in retry producing {topic_name}* {data} {e} {traceback.format_exc()}"
            AlertManager.send_kafka_alerts(message)
            return False, e
        else:
            message = f"*Error in producing {topic_name} hence going for retry* {data} {e} {traceback.format_exc()}"
            AlertManager.send_kafka_alerts(message)
            return push_data_in_kafka(data, topic_name, is_retry_call=True)
    return True, None


def push_data_in_kafka_v2(data, topic_name, is_retry_call=False):
    key = get_kafka_producer_key(data, topic_name)
    try:
        if key:
            producer = settings.KEY_SERIALIZER_KAFKA_PRODUCER
            fmd = producer.send(topic_name, data, key=key)
            fmd.add_errback(err_back_v2, topic_name, data)

        else:
            producer = settings.KAFKA_PRODUCER
            fmd = producer.send(topic_name, data)
            fmd.add_errback(err_back_v2, topic_name, data)

    except Exception as e:
        if is_retry_call:
            message = f"*Error in retry producing {topic_name}* {data} {e} {traceback.format_exc()}"
            AlertManager.send_kafka_alerts(message)
            return False, e
        else:
            message = f"*Error in producing {topic_name} hence going for retry* {data} {e} {traceback.format_exc()}"
            AlertManager.send_kafka_alerts(message)
            return push_data_in_kafka_v2(data, topic_name, is_retry_call=True)

    return True, None


def err_back(topic_name, data, e):
    message = f"*Error in producing {topic_name} hence going for retry* {data} {e}"
    AlertManager.send_kafka_alerts(message)
    push_data_in_kafka(data, topic_name, is_retry_call=True)


def err_back_v2(topic_name, data, e):
    message = f"*Error in producing {topic_name} hence going for retry* {data} {e}"
    AlertManager.send_kafka_alerts(message)
    push_data_in_kafka_v2(data, topic_name, is_retry_call=True)


def retry_err_back(topic_name, data, e):
    message = f"*Error in retry producing {topic_name}* {data} {e}"
    AlertManager.send_kafka_alerts(message)


def push_data_in_kafka_via_chunk_thread(data_list, topic_name):
    try:
        CHUNK_LENGTH = 10

        for i in range(0, len(data_list), CHUNK_LENGTH):
            data_chunk = data_list[i : i + CHUNK_LENGTH]
            push_data_in_kafka(data_chunk, topic_name)

    except Exception as e:
        text = f"*Error in pushing data in kafka via chunks in thread {topic_name}*. {traceback.format_exc()}"
        text += f" {data_list}"
        AlertManager.send_transaction_alert(text)


def push_data_in_kafka_in_chunks(data_list, chunk_size, topic_name):
    try:
        for i in range(0, len(data_list), chunk_size):
            data_chunk = data_list[i : i + chunk_size]
            push_data_in_kafka(data_chunk, topic_name)

    except Exception as e:
        text = f"*Error in pushing data in kafka in chunks {topic_name}*. {traceback.format_exc()}"
        text += f" {data_list}"
        AlertManager.send_transaction_alert(text)


def push_data_in_kafka_request_logs(data, topic_name, is_retry_call=False):
    if not data.get("created_at"):
        data.update({"created_at": datetime.datetime.now()})
    if not data.get("updated_at"):
        data.update({"updated_at": datetime.datetime.now()})

    if not data.get("request_tracking_id"):
        data.update({"request_tracking_id": str(uuid.uuid4())})

    request_data = {"request_data": data, "service_name": "parkplus_used_car", "table_name": "request_logs"}

    try:
        producer = settings.KAFKA_PRODUCER_REQUEST_LOGS
        fmd = producer.send(topic_name, request_data)
        fmd.add_errback(err_back_rl, topic_name, request_data)

    except Exception as e:
        if is_retry_call:
            message = f"*Error in retry producing {topic_name}* {request_data} {e} {traceback.format_exc()}"
            AlertManager.send_kafka_alerts(message)
            return False, e
        else:
            message = (
                f"*Error in producing {topic_name} hence going for retry* {request_data} {e} {traceback.format_exc()}"
            )
            AlertManager.send_kafka_alerts(message)
            return push_data_in_kafka_request_logs(request_data, topic_name, is_retry_call=True)

    return True, None


def err_back_rl(topic_name, data, e):
    message = f"*Error in producing {topic_name} hence going for retry* {data} {e}"
    AlertManager.send_kafka_alerts(message)
    push_data_in_kafka_request_logs(data, topic_name, is_retry_call=True)
