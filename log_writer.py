"""
Module: writer
Purpose: Provides functions to log messages, errors, and incidents locally,
         and to send notifications (via pushover) to the administrator.
"""

import datetime
import os
import request_handler

DEST_LOG = "Log"
DEST_ERROR = "Error"
DEST_INCIDENT_LOG = "Incident"


def ensure_dir(directory: str) -> None:
    """
    Ensure that a directory exists. Create it if it does not exist.

    Args:
        directory (str): The path to the directory.
    """
    os.makedirs(directory, exist_ok=True)


def to_terminal(module: str, msg: str) -> None:
    """
    Log a message to the terminal and write it to the daily log file.

    Args:
        module (str): Name of the module originating the message.
        msg (str): The message to log.
    """
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output = f"{now}\t{module}\t{msg}"
        _to_log(output)
        print(output)
    except Exception as e:
        _send_pushover_to_admin("Writer", "Write to terminal", e.__class__, "")


def _to_log(msg: str) -> None:
    """
    Write a log message to the daily log file in the log directory.

    Args:
        msg (str): The message to write.
    """
    try:
        ensure_dir(DEST_LOG)
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
        path = os.path.join(DEST_LOG, filename)
        with open(path, 'a+', encoding="utf-8") as f:
            f.write(f"{msg}\n")
    except Exception as e:
        _send_pushover_to_admin("Writer", "Write to log", e.__class__, "")


def to_error(module: str, tried_to: str, err_msg: Exception, elem: object) -> None:
    """
    Log an error message to the error log file and notify the admin.

    Args:
        module (str): The module where the error occurred.
        tried_to (str): A description of the operation attempted.
        err_msg (Exception): The error/exception encountered.
        elem (object): The element or context associated with the error.
    """
    err_msg_repr = repr(err_msg)
    try:
        to_terminal("Writer", "Exception occurred - Check error log")
        ensure_dir(DEST_ERROR)
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
        path = os.path.join(DEST_ERROR, filename)
        with open(path, 'a+', encoding="utf-8") as f:
            log_entry = (
                "-----------\n"
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Module: {module}\n"
                f"Tried to: {tried_to}\n"
                f"Error message: {err_msg_repr}\n"
                f"Element: {elem}\n"
                "-----------\n"
            )
            f.write(log_entry)
        _send_pushover_to_admin(module, tried_to, err_msg_repr, elem)
    except Exception as e:
        _send_pushover_to_admin(module, "Exception while handling an error", e.__class__, " ")


def to_incident_log(msg: str) -> None:
    """
    Write an incident message to the incident log file.

    Args:
        msg (str): The incident message to log.
    """
    try:
        ensure_dir(DEST_INCIDENT_LOG)
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
        path = os.path.join(DEST_INCIDENT_LOG, filename)
        with open(path, 'a+', encoding="utf-8") as f:
            f.write(f"{msg}\n")
    except Exception as e:
        _send_pushover_to_admin("Writer", "Write to incident log", e.__class__, "")


def _send_pushover_to_admin(module: str, tried_to: str, err_msg: object, elem: object) -> None:
    """
    Send a notification to the administrator via Pushover.

    Args:
        module (str): The module where the error occurred.
        tried_to (str): Description of the operation attempted.
        err_msg (object): The error message or exception.
        elem (object): The element or context associated with the error.
    """
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = (
            f"{now}\n"
            f"Module: {module}\n"
            f"Tried to: {tried_to}\n"
            f"Error message: {err_msg}\n"
            f"Element: {elem}"
        )
        request_handler.push_to_pushover_admin(msg, "default")
    except Exception as e:
        print("Exception in sending pushover to Admin")
        print(e)
