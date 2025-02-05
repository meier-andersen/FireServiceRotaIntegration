import writer as W
import requests
import json
from decouple import config

ModuleName = "Request Handler"

def push_to_pushover(msg, priority):
    try:
        if config('ENABLE_PUSHOVER'):
            data = {'title': config('PUSHOVER_HEADER'),
                    'token': config('PUSHOVER_TOKEN'),
                    'user': config('PUSHOVER_USER_KEY'),
                    'message': msg,
                    'html': "1"}
            if priority != "default":
                data['priority'] = priority
            endpoint = "https://api.pushover.net/1/messages.json"
            _handle_http_post(endpoint, data)
    except Exception as e:
        _to_error("Push to pushover", e.__class__, msg)


def push_to_pushover_admin(msg, priority = "default"):
    try:
        if config('ENABLE_ADMIN'):
            data = {'title': config('PUSHOVER_HEADER_ADMIN'),
                    'token': config('PUSHOVER_TOKEN_ADMIN'),
                    'user': config('PUSHOVER_USER_KEY_ADMIN'),
                    'message': msg,
                    'html': "1"}
            if priority != "default":
                data['priority'] = priority
            endpoint = "https://api.pushover.net/1/messages.json"
            _handle_http_post(endpoint, data)
    except Exception as e:
        print("Exception in sending pushover to Admin")

def _handle_http_post(dest, data):
    try:
        r = requests.post(url=dest, data=data)
        pastebin_url = json.loads(r.text)
        if pastebin_url["status"] == 1:
            _to_terminal("Response from Pushover: Success")
        else:
            _to_terminal("Response from Pushover: Failture - See error log")
            _to_error("Got error msg from pushover", r.text, data)
    except Exception as e:
        _to_error("Handle push to pushover", e.__class__, dest)


def _to_terminal(msg):
    W.to_terminal(ModuleName, msg)


def _to_error(tried_to, err_msg, obj):
    W.to_error(ModuleName, tried_to, err_msg, obj)