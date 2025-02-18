import asyncio
import aio_pika
import json
import os
from app.config import Config
from app.screening import scoreResume
from app.models import ApplicationResult
from app.database import results_collection

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try: 
            print('888888888888888888888888888888888888888888888888888888888888888888')
            data = json.loads(message.body.decode())
            print(f"Processing {data['application_id']}")

            # Score resume
            llm_output, kw_score, vec_score = scoreResume(
                data['job_requirements_path'],
                data['resume_path']
            )

            # Calculate final score
            final_score = (llm_output['overall_score'] * 0.6) + kw_score + vec_score

            # Create result document
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
            await ApplicationResult.create(result)

            # Cleanup files
            for path in [data['resume_path'], data['job_requirements_path']]:
                if os.path.exists(path):
                    os.remove(path)

        except Exception as e:
            print(f"Error processing message: {e}")
            await message.nack()

async def start_consumer():
    connection = await aio_pika.connect(Config.RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(Config.QUEUE_NAME, durable=True)
    
    await queue.consume(process_message)
    print("Consumer started. Waiting for messages...")
    
    # Keep connection open
    await asyncio.Future()