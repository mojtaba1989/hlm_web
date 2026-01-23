from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from nodes.core import core_ as core

router = APIRouter()

@router.get('/logs')
def stream_logs():
    def event_stream():
        while True:
            msg = core.logger.log_queue.get()
            yield f"data: {msg}\n\n"
    return StreamingResponse(event_stream(), media_type='text/event-stream')