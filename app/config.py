import os

class Config:
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin@rabbitmq:5672/")
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017/resume_db")
    QUEUE_NAME = "application_queue"
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/shared_volume")