import json
import time
from websocket import WebSocketApp
import requestHandler as rs
import writer as w
import oauthHandler as oAuth

ModuleName = "FSR Handler"
forceUpdate = False

def run():
        keepRunning = True
        while keepRunning:
            try:
                url = _generate_url()
                
                ws = WebSocketApp(
                    url,
                    on_open=on_open,
                    on_message=on_message,
                    on_close=on_close,
                    on_error=on_error
                )
                
                ws.run_forever()
                
                time.sleep(1)
                _to_terminal("Attempting to establish new connection")
            except KeyboardInterrupt:
                keepRunning = False


def _generate_url():
    global forceUpdate
    token = oAuth.get_token(forceUpdate)
    url = f"wss://www.fireservicerota.co.uk/cable?access_token={token}"
    forceUpdate = False
    return url

def on_open(ws):
    _to_terminal('WebSocket connected')
    msg = {
        "command": "subscribe",
        "identifier": json.dumps({
            "channel": "IncidentNotificationsChannel"
        })
    }
    ws.send(json.dumps(msg))

def on_message(ws, message):
    global forceUpdate
    msg = json.loads(message)
    
    if msg.get("type") == "ping" or msg.get("type") == "welcome":
      return

    if msg.get("type") == "confirm_subscription":
      _to_terminal("New connection established")
      return
    
    if msg.get("type") == "disconnect" and msg.get("type") == "unauthorized":
        forceUpdate = True
        rs.push_to_pushover_admin("Connection was closed because the user was not authorized", "default")
        return

    if msg.get("body"):
        rs.push_to_pushover(msg.get("body"), "default")

    _to_terminal("----- ALARM -----")
    print(msg)
    _to_terminal("----- ALARM -----")

def on_close(ws, close_status_code, close_msg):
    _to_terminal('WebSocket closed')


def on_error(ws, error):
    _to_error('WebSocket error: ', error)


def _to_terminal(msg):
    w.to_terminal(ModuleName, msg)


def _to_error(tried_to, err_msg, obj):
    w.to_error(ModuleName, tried_to, err_msg, obj)