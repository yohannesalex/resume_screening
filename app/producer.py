import aio_pika
from app.config import Config
import json
from tenacity import retry, wait_fixed

@retry(wait=wait_fixed(2))
async def publish_application(message):
    connection = await aio_pika.connect(Config.RABBITMQ_URL)
    channel = await connection.channel()
    await channel.declare_queue(Config.QUEUE_NAME, durable=True)
    
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(message).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key=Config.QUEUE_NAME
    )
    await connection.close()