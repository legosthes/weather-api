import requests
from fastapi import FastAPI, HTTPException, Response
from app.config import API_KEY


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/weather/{city}")
def get_weather(city: str):
    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    url = f"{BASE_URL}/{city}/next7days?unitGroup=metric&key={API_KEY}&contentType=json"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            return data
    except requests.exceptions.RequestException as error:
        raise HTTPException(
            status_code=503, detail=f"Error contacting weather service: {error}"
        )
