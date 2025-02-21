import asyncio
import json
import os
from config_local import Config
from screening import scoreResume
from models import ResultDocument, JobDocument
import aio_pika
from concurrent.futures import ThreadPoolExecutor
from generate_skill_for_interview import analyse_job_skills

executor = ThreadPoolExecutor()

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():  
        try:
            print("Processing message...")
            data = json.loads(message.body.decode())

            # Score resume
            
            job_id = data["job_id"]
            job_fetch = JobDocument.getJob_by_id(job_id)
            job_text = job_fetch['job_requirements']
            skill_fetch = analyse_job_skills(job_text)
            llm_output, kw_score, vec_score , parsed_resume= scoreResume(
                job_text,
                data['resume_path']
            )
            final_score = (llm_output['overall_score'] * 0.6) + kw_score + vec_score

            result = {
                "application_id": data['application_id'],
                "job_id": data['job_id'],
                "final_score": round(final_score, 1),
                "score_breakdown": llm_output['score_breakdown'],
                "required_skills": skill_fetch,
                "parsed_resume":parsed_resume
            }

            # Save to MongoDB
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(executor, ResultDocument.create, result)

            # Cleanup files
            if os.path.exists(data['resume_path']):
                os.remove(data['resume_path'])

        except Exception as e:
            print(f"Error processing message: {e}")
            raise  

async def consume_messages():
    connection = await aio_pika.connect_robust(url=Config.RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(Config.QUEUE_NAME, durable=True)
    
    await queue.consume(process_message)
    print(" [*] Waiting for messages. To exit press CTRL+C")
    await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(consume_messages())