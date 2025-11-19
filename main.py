import requests
from typing import Union
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/weather/{city}")
def get_weather(city: str):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/next7days?unitGroup=metric&key=HMRFP2UWG2MMCZRAG5LSVKQMH&contentType=json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        message = f"The weather in {city} is {data['days'][0]['tempmin']}-{data['days'][0]['tempmax']}\u00b0C"
    else:
        message = "Data not found."
    return message
