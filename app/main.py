import requests
import json
import redis
import logging
from fastapi import FastAPI, HTTPException, Request
from app.config import API_KEY, CACHE_EXPIRATION, REDIS_HOST
from app.redis_client import get_redis_client
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# logging config

# the module name will be "main"
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


limiter = Limiter(
    # track each visitor by their IP address
    key_func=get_remote_address,
    storage_uri=f"redis://{REDIS_HOST}:6379",
)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
r = get_redis_client()


@app.get("/")
def read_root():
    return {"message": "Weather API is running!"}


@app.get("/weather/{city}/{start_date}/{end_date}")
@limiter.limit("10/minute")
def get_weather(request: Request, city: str, start_date: str, end_date: str):
    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

    url = f"{BASE_URL}/{city}/{start_date}/{end_date}?unitGroup=metric&key={API_KEY}&contentType=json&include=days&elements=datetime,tempmax,tempmin,feelslike"

    try:
        cache_key = f"weather:{city}, {start_date}-{end_date}"
        cached_data = r.get(cache_key)
        if cached_data:
            logger.info(f"Cache HIT for {city}")
            return json.loads(cached_data)

        logger.info(f"Cache MISS for {city}. Fetching from API...")

    except redis.ConnectionError as error:
        logger.error(f"Redis connection error: {error}")
        raise HTTPException(
            status_code=503, detail=f"Redis connection error: {error}", exc_info=True
        )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        data_str = json.dumps(data)

        try:
            logger.info(f"Cached data for {city} (TTL: {CACHE_EXPIRATION}s)")
            r.set(cache_key, data_str, ex=CACHE_EXPIRATION)
        except redis.ConnectionError as error:
            logger.error(f"Redis connection error: {error}", exc_info=True)
            raise HTTPException(
                status_code=503, detail=f"Redis connection error: {error}"
            )

        return data

    # errors from visual crossing api
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTPError from Visual Crossing: {e.response.status_code}", exc_info=True
        )
        if e.response.status_code == 400:
            raise HTTPException(
                status_code=404,
                detail=f"Data is not available. Either '{city}' is not a valid city or date is inserted incorrectly.",
            )
        elif e.response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Too many requests to weather service, please try again later.",
            )
        elif e.response.status_code == 500:
            raise HTTPException(
                status_code=500,
                detail="Internal service error",
            )
        else:
            # catching other errors from visual crossing api
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Weather API returned an error: {e.response.status_code}",
            )
    # general errors
    except requests.exceptions.RequestException as error:
        logger.error(f"Error contacting weather service: {error}")
        raise HTTPException(
            status_code=503,
            detail=f"Error contacting weather service: {error}",
        )
