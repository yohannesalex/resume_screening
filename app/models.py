from database import results_collection, job_collection , applications_collection
from datetime import datetime

class ResultDocument:
    @classmethod
    def create(cls, result_data):  
        # result_data["created_at"] = datetime.utcnow()
        results_collection.insert_one(result_data)  
        return result_data

    @classmethod
    def get_by_id(cls, application_id):  
        print(application_id)
        result = results_collection.find_one({"application_id": application_id}) 
        if result:
            result["_id"] = str(result["_id"])  
            
        return result
class JobDocument:
    @classmethod
    def createApplication(cls, result_data):  
        result_data["created_at"] = datetime.utcnow()
        job_collection.insert_one(result_data)  
        return result_data

    @classmethod
    def getJob_by_id(cls, job_id):  
        result = job_collection.find_one({"job_id": job_id}) 
        if result:
            result["_id"] = str(result["_id"])  
            
        return result
class ApplicationDocumnet:
    @classmethod
    def createApplication(cls, result_data):  
        result_data["created_at"] = datetime.utcnow()
        applications_collection.insert_one(result_data)  
        return result_data

    @classmethod
    def getApplication_by_id(cls, application_id):  
        result = applications_collection.find_one({"application_id": application_id}) 
        if result:
            result["_id"] = str(result["_id"])  
            
        return result