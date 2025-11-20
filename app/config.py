import os
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("API_KEY")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
