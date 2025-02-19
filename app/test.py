import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import asyncio

# Load environment variables
MONGO_URI = os.getenv("MONGODB_URL", "mongodb://localhost:27017/resume_db")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def connect_to_mongo():
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URI)
        db = client.get_database()  # Get default database (can be modified)
        logger.info("MongoDB connected successfully")

        # Perform a quick ping to check connection
        await db.command("ping")
        logger.info("MongoDB is up and running")
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return None

# Example of using this connection
async def main():
    db = await connect_to_mongo()
    if db is not None:  # Fixed the truth value testing
        results_collection = db["results"]
        # Now you can interact with the 'results' collection
        # For example, you could fetch some data
        cursor = results_collection.find()
        async for document in cursor:
            print(document)
    else:
        logger.error("Failed to connect to MongoDB")

asyncio.run(main())
