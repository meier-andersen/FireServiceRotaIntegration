import writer as w

module_name = "MessageHandler"

def generateMessage(msg): 
  res = msg.get("body")

  try:
    coor = _generate_url(msg.get("location"), msg.get("address"))
    res = res + "\n\n" + _add_html_button(coor)
  except Exception as e:
    _to_error("Convert location to link", e.__class__, "")

  return res


def _generate_url(loc, addr): 
  return f"https://www.google.dk/maps/search/{_build_coordinates(loc, addr)}"


def _build_coordinates(loc, addr):
  if "LV RUTE" in loc or "MTV" in loc:
    return f"{addr.get('latitude')},{addr.get('longitude')}"
  return loc


def _add_html_button(msg):
    return "<a href=\"" + msg + "\" target=\"_blank\">Link til kort</a>"


def _to_error(tried_to, err_msg, str):
    w.to_error(module_name, tried_to, err_msg, str)