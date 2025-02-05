import log_writer as w

MODULE_NAME = "MessageHandler"


def generate_message(msg: dict) -> str:
    """
    Generate a message by appending a Google Maps link button.

    Args:
        msg (dict): A dictionary containing message details.
            Expected keys:
                - "body": The primary message text.
                - "location": A location string.
                - "address": A dictionary with keys 'latitude' and 'longitude'.

    Returns:
        str: The generated message with the appended map link.
    """
    res = msg.get("body", "")

    try:
        coor = _generate_url(msg.get("location", ""), msg.get("address", {}))
        res += "\n\n" + _add_html_button(coor)
    except Exception as e:
        _to_error("Convert location to link", e.__class__.__name__, "")
    return res


def _generate_url(loc: str, addr: dict) -> str:
    """
    Generate a Google Maps search URL using provided location or address coordinates.

    Args:
        loc (str): A string representing location information.
        addr (dict): A dictionary containing address details with keys 'latitude' and 'longitude'.

    Returns:
        str: A URL string to search the location on Google Maps.
    """
    return f"https://www.google.dk/maps/search/{_build_coordinates(loc, addr)}"


def _build_coordinates(loc: str, addr: dict) -> str:
    """
    Build a coordinate string based on the location string or address details.

    If the location string contains "LV RUTE" or "MTV", use the latitude and longitude
    from the address dictionary. Otherwise, return the original location string.

    Args:
        loc (str): A string representing location information.
        addr (dict): A dictionary with 'latitude' and 'longitude' keys.

    Returns:
        str: A string containing coordinates or the original location.
    """
    if "LV RUTE" in loc or "MTV" in loc:
        return f"{addr.get('latitude')},{addr.get('longitude')}"
    return loc


def _add_html_button(url: str) -> str:
    """
    Create an HTML anchor tag that links to the given URL.

    Args:
        url (str): The URL for the map link.

    Returns:
        str: An HTML string with a clickable link.
    """
    return f'<a href="{url}" target="_blank">Link til kort</a>'


def _to_error(tried_to: str, err_msg: str, extra_info: str) -> None:
    """
    Log an error message using the writer module.

    Args:
        tried_to (str): A description of the operation that was attempted.
        err_msg (str): The error message or exception name.
        extra_info (str): Additional context or information.
    """
    w.to_error(MODULE_NAME, tried_to, err_msg, extra_info)
