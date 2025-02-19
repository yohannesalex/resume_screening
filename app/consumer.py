import asyncio
import json
import os
from config import Config
from screening import scoreResume
from models import ApplicationResult
import aio_pika
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():  # Auto-ack/nack based on exceptions
        try:
            print("Processing message...")
            data = json.loads(message.body.decode())
            print(f"Processing {data['job_requirements_path']}")

            # Score resume
            llm_output, kw_score, vec_score = scoreResume(
                data['job_requirements_path'],
                data['resume_path']
            )
            final_score = (llm_output['overall_score'] * 0.6) + kw_score + vec_score

            result = {
                "application_id": data['application_id'],
                "job_id": data['job_id'],
                "final_score": round(final_score, 1),
                "score_breakdown": {
                    "llm_score": llm_output['overall_score'],
                    "keyword_score": kw_score,
                    "vector_score": vec_score
                },
                "details": llm_output
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
            raise  # Re-raise to ensure message is nacked/requeued

async def consume_messages():
    connection = await aio_pika.connect_robust(Config.RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(Config.QUEUE_NAME, durable=True)
    
    await queue.consume(process_message)
    print(" [*] Waiting for messages. To exit press CTRL+C")
    await asyncio.Future()  # Run indefinitely

if __name__ == "__main__":
    asyncio.run(consume_messages())