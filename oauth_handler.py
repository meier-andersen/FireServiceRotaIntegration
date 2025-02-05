"""
Module: oAuthHandler
Purpose: Handles OAuth token generation and caching for accessing the API.
"""

from decouple import config
import requests

# Global variables to cache tokens.
access_token = None

class OAuthError(Exception):
    """Custom exception for OAuth related errors."""
    pass

def get_token(force_update: bool = False) -> str:
    """
    Retrieve a valid access token.
    
    If a token is already cached and force_update is False, returns the cached token.
    Otherwise, generates a new token.
    
    Args:
        force_update (bool): If True, forces the retrieval of a new token even if one is cached.
    
    Returns:
        str: A valid access token.
    
    Raises:
        OAuthError: If token generation fails.
    """
    global access_token
    if access_token and not force_update:
        return access_token
    return _generate_new_token()

def _generate_new_token() -> str:
    """
    Generate a new access token by making an OAuth request.
    
    Returns:
        str: The new access token.
    
    Raises:
        OAuthError: If the token request fails or no access token is found in the response.
    """
    global access_token

    url = "https://www.fireservicerota.co.uk/oauth/token"
    data = {
        "grant_type": "password",
        "username": config("FSR_USERNAME"),
        "password": config("FSR_PASSWORD"),
    }

    response = requests.post(url, data=data)

    if response.status_code != 200:
        # Raise a custom exception with error details.
        raise OAuthError(f"Token request failed (status code {response.status_code}): {response.json()}")

    response_data = response.json()
    access_token = response_data.get("access_token")
    if access_token:
        return access_token

    raise OAuthError("No access token found in response body")
