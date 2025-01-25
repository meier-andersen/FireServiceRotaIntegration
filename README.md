# Introduction
This repo is an integration to Fire Service Rota (FSR) using their public api https://www.fireservicerota.co.uk/apidocs/
The project runs in Python and allows members which have a FSR user, to run a terminal project, which sends push notifications via pushover.
For most users, which use call out via mobile app, this will not make a huge difference, but it works well for people using pagers and want to be notified.
In the future, the project will be expanded so it is possible to make http calls to external endpoints (etc Home Assistant or other home automation)

## Setup: 
- Clone the repo
- Make a copy of .env.example and rename it to .env
- Fill out all the information in the .env file.
  - You can create a profile and find all information needed for pushover at https://pushover.net/
  - If you do not want admin messages or pushover messages, set the value to 0 instead of 1 at the top of the file
- Install python-decouple, websocket-client and requests using pip
  - pip install python-decouple / pip3 install python-decouple
  - pip install websocket-client / pip3 install websocket-client
  - pip install python-decouple / pip3 install python-decouple

## Run:
- Run app.py (etc python app.py on Windows)

This is my very first version of the integration and I expect it to grow in size over the next months
