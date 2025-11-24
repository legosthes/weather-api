import requests
import json
import redis
from fastapi import FastAPI, HTTPException
from app.config import API_KEY, CACHE_EXPIRATION
from app.redis_client import get_redis_client


app = FastAPI()
r = get_redis_client()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/weather/{city}/{start_date}/{end_date}")
def get_weather(city: str, start_date, end_date):
    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    url = f"{BASE_URL}/{city}/{start_date}/{end_date}?unitGroup=metric&key={API_KEY}&contentType=json&include=days&elements=datetime,tempmax,tempmin,feelslike"

    try:
        cache_key = f"weather:{city}, {start_date}"
        cached_data = r.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

    except redis.ConnectionError as error:
        raise f"Connection error: {error}"

    try:
        response = requests.get(url)

        response.raise_for_status()

        data = response.json()
        print(data)
        data_str = json.dumps(data)
        r.set(f"weather:{city}", data_str, ex=CACHE_EXPIRATION)

        return data

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise HTTPException(
                status_code=404,
                detail=f"Data is not available. Either '{city}' is not a valid city or date is insert incorrectly.",
            )
        elif e.response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
            )
        elif e.response.status_code == 500:
            raise HTTPException(
                status_code=500,
                detail="Internal service error",
            )
