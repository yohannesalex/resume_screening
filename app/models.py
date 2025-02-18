from app.database import results_collection
from datetime import datetime

class ApplicationResult:
    @classmethod
    async def create(cls, result_data):
        result_data["created_at"] = datetime.utcnow()
        await results_collection.insert_one(result_data)
        return result_data

    @classmethod
    async def get_by_id(cls, application_id):
        return await results_collection.find_one({"application_id": application_id})