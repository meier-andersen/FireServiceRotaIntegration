from decouple import config
import requests

access_token = None
refresh_token = None

def get_token(forceUpdate):
  global access_token
  if access_token and not forceUpdate:
    return access_token
  return _generate_new_token()


def _generate_new_token():
  global access_token

  url = "https://www.fireservicerota.co.uk/oauth/token"
  data = {
      "grant_type": "password",
      "username": config("FSR_USERNAME"),
      "password": config("FSR_PASSWORD"),
  }
  response = requests.post(url, data=data)
  if response.status_code != 200:
    raise Exception(response.json())
  
  response_data = response.json()
  access_token = response_data.get("access_token")
  if access_token:
    return access_token 
  raise Exception("No access token found in body")