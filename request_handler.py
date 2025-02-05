"""
Module: request_handler
Purpose: Provides functions to send push notifications via Pushover,
         including separate functions for general and admin notifications.
"""

import requests
from decouple import config
import log_writer

MODULE_NAME = "Request Handler"


def push_to_pushover(msg: str, priority: str = "default") -> None:
    """
    Send a push notification via Pushover if ENABLE_PUSHOVER is enabled.
    
    Args:
        msg (str): The message to send.
        priority (str): The priority of the message. Defaults to "default".
    """
    try:
        if config('ENABLE_PUSHOVER', cast=bool, default=False):
            data = {
                'title': config('PUSHOVER_HEADER'),
                'token': config('PUSHOVER_TOKEN'),
                'user': config('PUSHOVER_USER_KEY'),
                'message': msg,
                'html': "1"
            }
            if priority != "default":
                data['priority'] = priority
            endpoint = "https://api.pushover.net/1/messages.json"
            _handle_http_post(endpoint, data)
    except Exception as e:
        _to_error("Push to pushover", str(e), msg)


def push_to_pushover_admin(msg: str, priority: str = "default") -> None:
    """
    Send an admin push notification via Pushover if ENABLE_ADMIN is enabled.
    
    Args:
        msg (str): The message to send.
        priority (str): The priority of the message. Defaults to "default".
    """
    try:
        if config('ENABLE_ADMIN', cast=bool, default=False):
            data = {
                'title': config('PUSHOVER_HEADER_ADMIN'),
                'token': config('PUSHOVER_TOKEN_ADMIN'),
                'user': config('PUSHOVER_USER_KEY_ADMIN'),
                'message': msg,
                'html': "1"
            }
            if priority != "default":
                data['priority'] = priority
            endpoint = "https://api.pushover.net/1/messages.json"
            _handle_http_post(endpoint, data)
    except Exception as e:
        print("Exception in sending pushover to Admin:", e)


def _handle_http_post(dest: str, data: dict) -> None:
    """
    Handle the HTTP POST request to the specified destination.
    
    Args:
        dest (str): The URL endpoint for the POST request.
        data (dict): The payload data to be sent.
    """
    try:
        response = requests.post(url=dest, data=data, timeout=10)
        response_data = response.json()
        if response_data.get("status") == 1:
            _to_terminal("Response from Pushover: Success")
        else:
            _to_terminal("Response from Pushover: Failure - See error log")
            _to_error("Got error msg from pushover", response.text, data)
    except Exception as e:
        _to_error("Handle push to pushover", str(e), dest)


def _to_terminal(msg: str) -> None:
    """
    Log a message to the terminal using the writer module.
    
    Args:
        msg (str): The message to log.
    """
    log_writer.to_terminal(MODULE_NAME, msg)


def _to_error(tried_to: str, err_msg: str, obj: object) -> None:
    """
    Log an error using the writer module.
    
    Args:
        tried_to (str): Description of the operation attempted.
        err_msg (str): The error message.
        obj (object): The context or data related to the error.
    """
    log_writer.to_error(MODULE_NAME, tried_to, err_msg, obj)
