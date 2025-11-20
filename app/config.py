import os
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("The API_KEY is not set.")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
CACHE_EXPIRATION = 43200
