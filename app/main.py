from config import Config
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import uuid
import os
from producer import publish_application
from models import ApplicationResult
import aiofiles
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

class ApplicationRequest(BaseModel):
    job_id: str

@app.post("/submit")
async def submit_application(
    job_id: str,
    job_requirements: UploadFile = File(...),
    resume: UploadFile = File(...)
):
    try:
        application_id = str(uuid.uuid4())
        os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

        # Save files
        job_req_path = f"{Config.UPLOAD_DIR}/{application_id}{job_requirements.filename}"
        resume_path = f"{Config.UPLOAD_DIR}/{application_id}{resume.filename}"
        
        async with aiofiles.open(job_req_path, "wb") as f:
            await f.write(await job_requirements.read())
       
        async with aiofiles.open(resume_path, "wb") as f:
            await f.write(await resume.read())
        # Publish to queue
        await publish_application({
            "application_id": application_id,
            "job_id": job_id,
            "resume_path": resume_path,
            "job_requirements_path": job_req_path
        })
        return {
            'application_id':application_id
        }
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/results/{application_id}")
def get_results(application_id: str):  # Remove async
    result = ApplicationResult.get_by_id(application_id)  # Synchronous call
    if not result:
        raise HTTPException(status_code=404, detail="Application not found")
    return result