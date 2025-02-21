from config_local import Config
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from pydantic import BaseModel
import uuid
import os
from producer import publish_application
from models import ResultDocument , JobDocument, ApplicationDocumnet
import aiofiles
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/job_post")
async def post_job(job_requirements: str = Form(...)):
    if not job_requirements.strip():  # Check if job_requirements is empty
        raise HTTPException(status_code=400, detail="Job requirements cannot be empty")

    job_id = str(uuid.uuid4())  # Generate a unique job ID
    job_data = {
        "job_id": job_id,
        "job_requirements": job_requirements
    }

    try:
        JobDocument.createApplication(job_data)

        # if result.inser:  # If insertion is successful
        return {"job_id": job_id, "message": "Job posted successfully"}
        # else:
        #     raise HTTPException(status_code=500, detail="Failed to insert job data")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@app.get("/jobs/{job_id}")
def get_results(job_id: str):  
    result = JobDocument.getJob_by_id(job_id)  
    if not result:
        raise HTTPException(status_code=404, detail="job not found")
    return result


@app.post("/submit")
async def submit_application(
    job_id: str = Form(...),
    resume: UploadFile = File(...),
    name: str = Form(...),
    email: str = Form(...)

):
    try:
        application_id = str(uuid.uuid4())
        os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

        # Create file paths
        resume_path = os.path.join(Config.UPLOAD_DIR, f"{application_id}_{resume.filename}")
        
        # Save the resume file
        async with aiofiles.open(resume_path, "wb") as f:
            await f.write(await resume.read())

        application_data = {
            "application_id": application_id,
            "job_id": job_id,
            "name": name,
            "email" : email,
            "resume_url": resume_path
        }
        # store the application into the database
        ApplicationDocumnet.createApplication(application_data)

        # Publish to queue with the application details
        await publish_application({
            "application_id": application_id,
            "resume_path": resume_path,
            "job_id": job_id,
        })
        
        return {"application_id": application_id,
                "message": "application submitted successfully"
                }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/{application_id}")
def get_results(application_id: str):  
    result = ResultDocument.get_by_id(application_id)  
    if not result:
        raise HTTPException(status_code=404, detail="Application not found")
    return result