import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union

import django
import requests

logger = logging.getLogger("NetworkManager")


@dataclass
class NetworkRequestDetail:
    """
    Data contract for all external network requests.
    """
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    cert: Optional[Any] = None
    auth: Optional[Any] = None
    json: Optional[Dict[str, Any]] = None
    data: Optional[Union[Dict[str, Any], str]] = None
    params: Optional[Dict[str, Any]] = None
    files: Optional[Any] = None
    timeout: int = 30


class NetworkManager:
    """
    Central Network Manager to handle HTTP Requests globally.
    Closes old DB connections organically and executes requests securely.
    """
    
    @staticmethod
    def send_request(request_detail: NetworkRequestDetail) -> requests.Response:
        """
        Executes a network request based on the provided configuration.
        """
        # Ensure stale database connections are closed before doing heavy I/O
        django.db.close_old_connections()
        
        logger.info(f"Initiating network call: [{request_detail.method}] {request_detail.url}")
        
        try:
            response = requests.request(
                method=request_detail.method,
                url=request_detail.url,
                headers=request_detail.headers,
                cert=request_detail.cert,
                auth=request_detail.auth,
                json=request_detail.json,
                data=request_detail.data,
                params=request_detail.params,
                files=request_detail.files,
                timeout=request_detail.timeout,
            )
            
            logger.info(f"Response received: [{response.status_code}] {request_detail.url}")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network call failed: {request_detail.url} | Error: {str(e)}")
            raise
