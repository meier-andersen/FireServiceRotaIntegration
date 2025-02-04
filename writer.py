import datetime
import os
import requestHandler as re

dest_log = "Log/"
dest_error = "Error/"
dest_incident_log = "Incident/"

def to_terminal(module, msg):
    output = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\t" + module + "\t" + msg
    _to_log(output)
    print(output)


def _to_log(msg):
    if not os.path.isdir(dest_log):  # Creates dir if it doesn't exist
        os.mkdir(dest_log)

    path = os.path.join(dest_log, datetime.datetime.now().strftime("%Y-%m-%d") + ".log")
    with open(path, 'a+') as f:
        f.write(msg +
                "\n")


def to_error(module, tried_to, err_msg, elem):
    err_msg = repr(err_msg)
    try:
        to_terminal("Writer", "Exception occurred - Check error log")
        if not os.path.isdir(dest_error):  # Creates dir if it doesn't exist
            os.mkdir(dest_error)

        path = os.path.join(dest_error, datetime.datetime.now().strftime("%Y-%m-%d") + ".log")
        with open(path, 'a+') as f:
            f.write("-----------\n" +
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                    "\nModule: " + module +
                    "\nTried to: " + tried_to +
                    "\nError message: " + str(err_msg) +
                    "\nElement: " + str(elem) +
                    "\n-----------\n")
        _send_pushover_to_admin(module, tried_to, err_msg, elem)
    except Exception as e:
        _send_pushover_to_admin(module, "Exception while handling an error", e.__class__, " ")

def to_incident_log(msg): 
    if not os.path.isdir(dest_incident_log):  # Creates dir if it doesn't exist
        os.mkdir(dest_incident_log)

    path = os.path.join(dest_incident_log, datetime.datetime.now().strftime("%Y-%m-%d") + ".log")
    with open(path, 'a+') as f:
        f.write(msg +
                "\n")

def _send_pushover_to_admin(module, tried_to, err_msg, elem):
    try:
        msg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + \
                "\nModule: " + module + \
                "\nTried to: " + tried_to + \
                "\nError message: " + str(err_msg) + \
                "\nElement: " + str(elem)
        re.push_to_pushover_admin(msg, "default")
    except Exception as e:
        print("Exception in sending pushover to Admin")
        print(e)