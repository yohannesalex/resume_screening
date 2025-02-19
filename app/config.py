import os

class Config:
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017/resume_db")
    QUEUE_NAME = "application_queue"
    UPLOAD_DIR = "/shared_volume"