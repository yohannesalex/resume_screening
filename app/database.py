from pymongo import MongoClient
import os


client = MongoClient(MONGO_URI)


db = client.resume_db
results_collection = db["results"]
job_collection = db["jobs"]
applications_collection = db["applications"]
