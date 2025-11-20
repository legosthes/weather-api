import requests
import json
from fastapi import FastAPI, HTTPException
from app.config import API_KEY, CACHE_EXPIRATION
from app.redis_client import get_redis_client


app = FastAPI()
r = get_redis_client()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/weather/{city}")
def get_weather(city: str):
    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    url = f"{BASE_URL}/{city}/next7days?unitGroup=metric&key={API_KEY}&contentType=json"

    try:
        cache_key = f"weather:{city}"
        cached_data = r.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            data_str = json.dumps(data)
            r.set(f"weather:{city}", data_str, ex=CACHE_EXPIRATION)

            return data
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Weather API error: {response.status_code}",
            )

    except requests.exceptions.RequestException as error:
        raise HTTPException(
            status_code=503, detail=f"Error contacting weather service: {error}"
        )
