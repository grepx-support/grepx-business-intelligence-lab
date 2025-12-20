from dotenv import load_dotenv
import os

load_dotenv()

CONNECTION_STRING = os.getenv("CONNECTION_STRING")

if not CONNECTION_STRING:
    raise RuntimeError("CONNECTION_STRING not set in .env")
