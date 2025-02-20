import asyncio
import json
import os
from config_local import Config
from screening import scoreResume
from models import ApplicationResult
import aio_pika
from concurrent.futures import ThreadPoolExecutor
from generate_skill_for_interview import analyse_job_skills
from file_reader import extract_text_from_file

executor = ThreadPoolExecutor()

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():  
        try:
            print("Processing message...")
            data = json.loads(message.body.decode())
            print(f"Processing {data['job_requirements_path']}")

            # Score resume
            llm_output, kw_score, vec_score = scoreResume(
                data['job_requirements_path'],
                data['resume_path']
            )
            job_text = extract_text_from_file(data['job_requirements_path'])
            skill_fetch = analyse_job_skills(job_text)
            final_score = (llm_output['overall_score'] * 0.6) + kw_score + vec_score

            result = {
                "application_id": data['application_id'],
                "job_id": data['job_id'],
                "final_score": round(final_score, 1),
                "score_breakdown": llm_output['score_breakdown'],
                "details": llm_output,
                "required_skills": skill_fetch
            }

            # Save to MongoDB
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(executor, ApplicationResult.create, result)

            # Cleanup files
            for path in [data['resume_path'], data['job_requirements_path']]:
                if os.path.exists(path):
                    os.remove(path)

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