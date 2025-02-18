from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGODB_URL", "mongodb://mongodb:27017/resume_db")

client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()
results_collection = db["results"]