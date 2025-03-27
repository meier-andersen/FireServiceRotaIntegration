import json
import log_writer
import message_handler
import request_handler
from datetime import datetime, timedelta
from decouple import config
import time

MODULE_NAME = "IncidentHandler"

current_incidents: list = []

def handle_incident(wrapper: json) -> None:
    """
    """
    try:
      _update_list()
      log_writer.to_incident_log(wrapper)

      msg = wrapper.get("message")

      if _is_in_list(msg.get("id")):
         _handle_existing_incident(msg)
      else:
         _push_new_incident(msg)
      _check_if_responding(msg)
    except Exception as e:
      _to_error("Handle new incident", str(e), "")


def _push_new_incident(msg: json): 
  try:
    _to_terminal("----- NEW INCIDENT -----")
    _to_terminal(msg.get("body"))
    _add_to_list(msg)
    _update_people(msg)

    pushover_msg: str = message_handler.generate_message(msg)
    request_handler.push_to_pushover(pushover_msg, "default")
  except Exception as e:
    _to_error("Handle a new message", str(e), "")


def _handle_existing_incident(msg):
   global current_incidents
   _update_people(msg)
   incident = next((entry for entry in current_incidents if entry["id"] == msg.get("id")), None)
   threshold = incident["timestamp"] + timedelta(seconds=7)

   if incident["hasSentPeople"]:
      return
   if datetime.now() < threshold:
      return
   
   incident["hasSentPeople"] = True
   _send_update(msg)


def _update_people(msg: json):
   global current_incidents
   incident = next((entry for entry in current_incidents if entry["id"] == msg.get("id")), None)
   for user in msg["incident_responses"]:
      if user.get("status") == "acknowledged" and not any(entry == user.get("user_name") for entry in incident["people"]):
         print("adding " + user.get("user_name"))
         incident["people"].append(user.get("user_name"))


def _add_to_list(msg: json):
  global current_incidents
  obj = {
     "id": msg.get("id"),
     "timestamp": datetime.now(),
     "isResponding": False,
     "people": [],
     "hasSentPeople": False
  }
  current_incidents.append(obj)


def _update_list():
  global current_incidents
  threshold = datetime.now() - timedelta(minutes=10)
  current_incidents = [entry for entry in current_incidents if entry["timestamp"] >= threshold]


def _is_in_list(id: str) -> bool:
   global current_incidents
   return any(entry["id"] == id for entry in current_incidents)


def _check_if_responding(msg: json) -> None: 
   global current_incidents
   if not config('ENABLE_RESPONDING', cast=bool, default=False):
      return
   userName = config('RESPONDING_USER_NAME')
   user = next((item for item in msg.get("incident_responses") if item.get("user_name") == userName), None)
   incident = next((entry for entry in current_incidents if entry["id"] == msg.get("id")), None)

   if user == None:
      return
   if incident == None:
      return
   if incident["isResponding"] == True:
      return
   if user.get("status") != "acknowledged":
      return
   
   incident["isResponding"] = True
   request_handler.push_to_pushover(config('RESPONDING_MSG'))


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

def _send_update(msg: json) -> None:
   incident = next((entry for entry in current_incidents if entry["id"] == msg.get("id")), None)
   people = len(incident["people"])
   message = str(people) + ' retursvar'
   request_handler.push_to_pushover(message)