from pymongo import MongoClient
import os

# Load environment variables
MONGO_URI = os.getenv("MONGODB_URL", "mongodb+srv://yohannesabdia:yohannes6460@cluster0.2almc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Connect to MongoDB
client = MongoClient(MONGO_URI)


# Use the specified database
db = client.resume_db
results_collection = db["results"]