import json
import log_writer
import message_handler
import request_handler
from datetime import datetime, timedelta

MODULE_NAME = "IncidentHandler"

current_incidents: list = []

def handle_incident(msg: json) -> None:
    """
    """
    try:
      _update_list()
      log_writer.to_incident_log(msg)

      if _is_in_list(msg.get("id")):
        _existing_incident(msg)
      else:
         _push_new_incident(msg)     
    except Exception as e:
      _to_error("Handle new incident", str(e), "")


def _push_new_incident(msg: json): 
  try:
    _to_terminal("----- NEW INCIDENT -----")
    _to_terminal(msg.get("body"))
    _add_to_list(msg)

    pushover_msg: str = message_handler.generate_message(msg)
    request_handler.push_to_pushover(pushover_msg, "default")
  except Exception as e:
    _to_error("Handle a new message", str(e), "")


def _existing_incident(msg: json):
   print("existing incident")


def _add_to_list(msg):
  global current_incidents
  obj = {
     "id": msg.get("id"),
     "timestamp": datetime.now()
  }
  current_incidents.append(obj)


def _update_list():
  global current_incidents
  threshold = datetime.now() - timedelta(minutes=5)
  current_incidents = [entry for entry in current_incidents if entry["timestamp"] >= threshold]


def _is_in_list(id: str) -> bool:
   global current_incidents
   return any(entry["id"] == id for entry in current_incidents)


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

