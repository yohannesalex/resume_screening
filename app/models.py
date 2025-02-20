from database import results_collection
from datetime import datetime

class ApplicationResult:
    @classmethod
    def create(cls, result_data):  
        print(' create database is called')
        result_data["created_at"] = datetime.utcnow()
        results_collection.insert_one(result_data)  
        return result_data

    @classmethod
    def get_by_id(cls, application_id):  
        print(application_id)
        result = results_collection.find_one({"application_id": application_id}) 
        if result:
            result["_id"] = str(result["_id"])  
            
        return result