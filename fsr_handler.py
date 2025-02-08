"""
Module: fsr_handler
Purpose: Manages the WebSocket connection to the Fire Service Rota (FSR) API,
         handles incoming messages, and delegates processing to other modules.
"""

import json
import time
from websocket import WebSocketApp
import request_handler
import log_writer
import oauth_handler
import incident_handler

# Module constants and global variables
MODULE_NAME = "FSR Handler"
force_update: bool = False
alive_counter: int = 0


def run() -> None:
    """
    Runs the WebSocket client and attempts reconnection on disconnection.
    """
    keep_running: bool = True
    while keep_running:
        try:
            url: str = _generate_url()
            ws: WebSocketApp = WebSocketApp(
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
            keep_running = False


def _generate_url() -> str:
    """
    Generates the WebSocket URL using a valid OAuth token.
    
    Returns:
        str: The WebSocket URL with an embedded access token.
    """
    global force_update
    token: str = oauth_handler.get_token(force_update)
    url: str = f"wss://www.fireservicerota.co.uk/cable?access_token={token}"
    force_update = False
    return url


def on_open(ws: WebSocketApp) -> None:
    """
    Callback when the WebSocket connection is opened.
    
    Sends a subscription message to the Incident Notifications channel.
    
    Args:
        ws (WebSocketApp): The WebSocket connection instance.
    """
    _to_terminal("WebSocket connected")
    msg = {
        "command": "subscribe",
        "identifier": json.dumps({
            "channel": "IncidentNotificationsChannel"
        })
    }
    ws.send(json.dumps(msg))


def on_message(ws: WebSocketApp, message: str) -> None:
    """
    Callback when a message is received from the WebSocket.
    
    Processes different message types and handles them accordingly.
    
    Args:
        ws (WebSocketApp): The WebSocket connection instance.
        message (str): The received message in JSON format.
    """
    global force_update, alive_counter
    try:
        msg = json.loads(message)

        # Handle 'ping' messages to manage connection liveness.
        if msg.get("type") == "ping":
            alive_counter -= 1
            if alive_counter <= 0:
                _to_terminal("Alive ping")
                alive_counter = 999

        # Ignore further processing for ping or welcome messages.
        if msg.get("type") in ["ping", "welcome"]:
            return

        # Handle subscription confirmation.
        if msg.get("type") == "confirm_subscription":
            _to_terminal("New connection established")
            alive_counter = 0
            return

        # Check for an unauthorized disconnect.
        if msg.get("type") == "disconnect" and msg.get("reason") == "unauthorized":
            force_update = True
            request_handler.push_to_pushover_admin(
                "Connection was closed because the user was not authorized", "default"
            )
            return
        
        incident_handler.handle_incident(msg)
        
        


    except Exception as e:
        print(e)
        #_to_error("Handle a new message", str(e), "")


def on_close(ws: WebSocketApp, close_status_code: int, close_msg: str) -> None:
    """
    Callback when the WebSocket connection is closed.
    
    Args:
        ws (WebSocketApp): The WebSocket connection instance.
        close_status_code (int): The status code for the close.
        close_msg (str): The close message.
    """
    _to_terminal("WebSocket closed")


def on_error(ws: WebSocketApp, error: Exception) -> None:
    """
    Callback when an error occurs on the WebSocket.
    
    Args:
        ws (WebSocketApp): The WebSocket connection instance.
        error (Exception): The error encountered.
    """
    _to_terminal(f"WebSocket error {str(error)}")


def _to_terminal(msg: str) -> None:
    """
    Log a message to the terminal using the writer module.
    
    Args:
        msg (str): The message to log.
    """
    log_writer.to_terminal(MODULE_NAME, msg)


def _to_error(tried_to: str, err_msg: str, obj: object) -> None:
    """
    Log an error message using the writer module.
    
    Args:
        tried_to (str): Description of the operation attempted.
        err_msg (str): The error message.
        obj (object): Additional context for the error.
    """
    log_writer.to_error(MODULE_NAME, tried_to, err_msg, obj)
