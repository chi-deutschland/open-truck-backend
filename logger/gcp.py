import json
import uuid

from datetime import datetime
from typing import Union
from flask import request

from .severity import Severity


class Stackdriver:
    def __init__(self, service_name: str, path: str, app_id: str):
        self.request_id = f'{uuid.uuid4()}'
        self.service_name = service_name
        self.path = path
        self.app_id = app_id

    def _log(self, severity: Severity, message: Union[str, dict]):
        structured_message: dict = {
            "severity": severity.value,
            "timestamp": datetime.utcnow().isoformat(),
            "labels": {
                "service_name": self.service_name,
                "path": self.path,
                "app_id": self.app_id,
                "request_id": self.request_id,
            }
        }
        if type(message) == dict:
            structured_message['jsonPayload'] = message
        elif type(message) == str:
            structured_message['textPayload'] = message
        print(json.dumps(structured_message))

    def debug(self, message: Union[str, dict]) -> None:
        self._log(severity=Severity.debug, message=message,)

    def info(self, message: Union[str, dict]) -> None:
        self._log(severity=Severity.info, message=message,)

    def warning(self, message: Union[str, dict]) -> None:
        self._log(severity=Severity.warning, message=message,)

    def error(self, message: Union[str, dict]) -> None:
        self._log(severity=Severity.error, message=message,)


def init_stackdriver(service_name: str, req: request) -> Stackdriver:
    return Stackdriver(
        service_name=service_name,
        path=req.path,
        app_id=request.args.get('app_id'),)
