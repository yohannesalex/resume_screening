from database import results_collection
from datetime import datetime

class ApplicationResult:
    @classmethod
    def create(cls, result_data):  # Remove async
        print(' create database is called')
        result_data["created_at"] = datetime.utcnow()
        results_collection.insert_one(result_data)  # Synchronous insert
        return result_data

    @classmethod
    def get_by_id(cls, application_id):  # Remove async
        print(application_id)
        result = results_collection.find_one({"application_id": application_id})  # Synchronous find
        if result:
            result["_id"] = str(result["_id"])  # Convert ObjectId to string
            
        return result