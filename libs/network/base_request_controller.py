import datetime
import os
import logging
from typing import Union, Dict, Any

from libs.constant import Constant
from libs.network.network_manager import NetworkManager, NetworkRequestDetail

logger = logging.getLogger("BaseRequestController")

# --- Mocking missing dependencies ---
class MockAlertManager:
    @staticmethod
    def send_response_related_alert(message, icon=None):
        logger.error(f"[NETWORK ALERT] {icon or ''}: {message}")

class MockRequestTrackingManager:
    def send_to_create_tracking_data(self, data):
        logger.info(f"Tracking data ready: {data}")

AlertManager = MockAlertManager()
# -------------------------------------

class BaseRequestController:
    """
    Extensible Controller for managing and tracking HTTP networking lifecycle.
    Automatically handles network headers, requests mapping, tracking, and alerting.
    """
    request_service_call_type = Constant.RequestServiceCallType.OUTGOING

    request_tracking_id = None
    request_data: dict = {}
    request_time = None
    response = None
    response_time = None
    response_data = None
    response_content = None
    response_json = None
    response_status_code = None
    request_time_taken = None
    exception = None
    remark = None
    auth_type: list = []
    content_type = None

    extra_headers_data: dict = {}
    decrypted_request_data = None
    encrypted_request_data = None

    encrypted_response_data = None
    decrypted_response_data = None
    request_service_type = ""
    request_service = ""

    user_id = None
    reference = None

    url: Union[str, None] = None
    api_endpoint: Union[str, None] = None
    method: Union[str, None] = "GET"
    headers: dict = {}
    cert = None
    auth = None
    json: Union[dict, None] = None
    data: dict = {}
    params: dict = {}
    timeout: Union[int, None] = 30
    files = None

    is_extra_response_data_present = False
    request_tracking_manager = MockRequestTrackingManager()

    def __init__(self):
        self.network_manager = NetworkManager()

    def send_request(self):
        self.set_request_details()

        error = None
        try:
            self.response = self.network_manager.send_request(self.get_network_request_detail())
        except Exception as err:
            error = err

        self.set_response_details(error)

        try:
            self.check_and_send_alert(error)
        except Exception:
            pass

        if self.check_to_track() and not self.is_extra_response_data_present:
            self.request_tracking_manager.send_to_create_tracking_data(self.get_create_only_tracking_data())

        self.check_and_log_internal_apis()

    def get_create_only_tracking_data(self):
        return {**self.get_request_data_for_tracking(), **self.get_response_data_for_tracking()}

    def get_create_only_extra_tracking_data_included(self):
        return {
            **self.get_request_data_for_tracking(),
            **self.get_response_data_for_tracking(),
            **self.get_extra_response_data_for_tracking(),
        }

    def check_and_log_internal_apis(self):
        if (
            self.request_service_type == Constant.RequestServiceType.MICROSERVICE
            and self.response_status_code
            and self.response_status_code != 200
        ):
            message = f"MICROSERVICE URL : {self.url} \nRESPONSE_STATUS_CODE: {self.response_status_code} \nRESPONSE_JSON: {self.response_json}"
            logger.info(message)

    def check_to_track(self):
        return self.request_service_type in [
            Constant.RequestServiceType.THIRD_PARTY, 
            Constant.RequestServiceType.MICROSERVICE
        ]

    def get_network_request_detail(self):
        return NetworkRequestDetail(
            url=self.url,
            method=self.method,
            cert=self.cert,
            auth=self.auth,
            data=self.data,
            json=self.json,
            params=self.params,
            headers=self.headers,
            files=self.files,
            timeout=self.timeout,
        )

    def set_request_details(self):
        self.headers = self.generate_headers()
        self.request_data = self.create_request_data()
        self.request_time = datetime.datetime.now()

    def get_request_data_for_tracking(self):
        return {
            "url": self.url,
            "method": self.method,
            "headers": self.headers,
            "json": self.json,
            "data": self.data,
            "params": self.params,
            "timeout": self.timeout,
            "request_data": self.request_data,
            "request_time": self.request_time,
            "request_service_call_type": self.request_service_call_type,
            "request_service_type": self.request_service_type,
            "request_service": self.request_service,
            "user_id": self.user_id,
            "reference": os.getenv("DEPLOYMENT", "LOCAL"),
        }

    def set_response_details(self, error=None):
        if self.response is None:
            self.remark = "No Response"
            self.response_status_code = None
            self.response_content = None
            self.response_text = None
            self.response_data = None
            self.response_time = datetime.datetime.now()
            self.request_time_taken = (self.response_time - self.request_time).total_seconds()
            self.response_json = None
        else:
            self.remark = None
            self.response_status_code = self.response.status_code
            self.response_content = self.response.content
            self.response_data = self.response_content
            self.response_text = self.response.text
            self.response_time = datetime.datetime.now()

            try:
                self.request_time_taken = self.response.elapsed.total_seconds()
            except Exception:
                self.request_time_taken = (self.response_time - self.request_time).total_seconds()

            try:
                self.response_json = self.response.json() if self.response is not None else None
            except Exception:
                self.response_json = None

            if self.response_status_code and self.response_status_code < 400:
                self.remark = "Successful Request"
            elif self.response_status_code and self.response_status_code < 500:
                self.remark = "Bad Request"
            else:
                self.remark = "Server Error"

        if error:
            self.exception = repr(error)[:254]
            self.remark = "Exception"

    def get_response_data_for_tracking(self):
        return {
            "response_data": self.response_data,
            "response_status_code": self.response_status_code,
            "response_time": self.response_time,
            "request_time_taken": self.request_time_taken,
            "remark": self.remark,
            "exception": self.exception,
        }

    def track_extra_response_data(self):
        self.request_tracking_manager.send_to_create_tracking_data(self.get_create_only_extra_tracking_data_included())

    def get_extra_response_data_for_tracking(self):
        return {
            "encrypted_response_data": self.encrypted_response_data,
            "decrypted_response_data": self.decrypted_response_data,
            "exception": self.exception,
            "remark": self.remark,
        }

    def check_and_send_alert(self, error):
        error = repr(error) if error else None

        if error:
            message = f"Error occurred in sending request. Error: {error}\nURL:{self.url}\nRequested Data:{self.request_data}"
            AlertManager.send_response_related_alert(message, icon=":boom:")

        elif self.response is not None:
            if self.response.status_code >= 500:
                message = f"Error occurred in sending request.\nStatus Code:{self.response.status_code}\nURL:{self.url}"
                AlertManager.send_response_related_alert(message)

            if hasattr(self.response, "elapsed") and self.response.elapsed.total_seconds() > 120:
                message = f"High Response Time. Time Taken:{self.response.elapsed.total_seconds()}\nURL:{self.url}"
                AlertManager.send_response_related_alert(message, icon=":hourglass:")

    def generate_headers(self):
        headers = dict(self.headers)

        if Constant.AuthenticationType.CLIENT_AUTH in self.auth_type:
            headers["client-id"] = getattr(self, "client_id", "")
            headers["client-secret"] = getattr(self, "client_secret", "")

        if Constant.AuthenticationType.SERVICE_AUTH in self.auth_type:
            headers["x-api-key"] = getattr(self, "x_api_key", "")

        if Constant.AuthenticationType.USER_AUTH in self.auth_type:
            headers["Authorization"] = getattr(self, "jwt_token", "")

        if Constant.AuthenticationType.MERCHANT_AUTH in self.auth_type:
            headers["merchant-id"] = getattr(self, "merchant_id", "")
            headers["merchant-key"] = getattr(self, "merchant_key", "")

        if self.content_type:
            headers["Content-Type"] = self.content_type

        if self.extra_headers_data:
            headers.update(self.extra_headers_data)

        return headers

    def create_request_data(self):
        req_data = {}
        if self.data and isinstance(self.data, dict):
            req_data.update(self.data)

        if self.json and isinstance(self.json, dict):
            req_data.update(self.json)

        if self.params and isinstance(self.params, dict):
            req_data.update(self.params)

        if self.files and isinstance(self.files, dict):
            req_data.update(self.files)

        return req_data if req_data else self.request_data
