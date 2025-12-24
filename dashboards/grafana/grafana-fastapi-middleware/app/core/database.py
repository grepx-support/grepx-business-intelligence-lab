from pymongo import MongoClient
from app.core.config import CONNECTION_STRING

client = MongoClient(CONNECTION_STRING)
db = client.get_default_database()
