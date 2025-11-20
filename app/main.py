import requests
import json
from fastapi import FastAPI, HTTPException
from app.config import API_KEY, CACHE_EXPIRATION
from app.redis_client import get_redis_client


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
        data = response.json()
        r = get_redis_client()

        if response.status_code == 200:
            cached_data = r.get(f"weather:{city}")

            if cached_data is None:
                data_str = json.dumps(data)
                r.set(f"weather:{city}", data_str, ex=CACHE_EXPIRATION)
                return data
            else:
                return json.loads(cached_data)

    except requests.exceptions.RequestException as error:
        raise HTTPException(
            status_code=503, detail=f"Error contacting weather service: {error}"
        )
