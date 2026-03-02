from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
from redis import asyncio as aioredis
from nodes.logger_ import logger_ as logger

router = APIRouter()

@router.get('/logs')
async def stream_logs():
    async def event_stream():
        # Use the async client for the stream
        async_redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)
        
        # --- PHASE 1: Send History ---
        history = await async_redis.lrange("app_logs_history", 0, -1)
        for log in history:
            yield f"data: {log}\n\n"
        
        # --- PHASE 2: Live Stream ---
        pubsub = async_redis.pubsub()
        await pubsub.subscribe("log_stream")

        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    yield f"data: {message['data']}\n\n"
                else:
                    yield ": heartbeat\n\n"
                
                await asyncio.sleep(0.1)
        finally:
            await pubsub.unsubscribe("log_stream")
            await async_redis.close()

    return StreamingResponse(event_stream(), media_type='text/event-stream')