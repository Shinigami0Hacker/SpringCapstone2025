from fastapi import APIRouter
from fastapi import WebSocket, APIRouter, WebSocketDisconnect
import psutil
import asyncio

router = APIRouter()
model = None

@router.websocket("/metrics")
async def metrics_socket(websocket: WebSocket):
    async def get_cpu_usage():
        cpu_usage = await asyncio.to_thread(psutil.cpu_percent, 1)
        return cpu_usage
    
    await websocket.accept()
    try:
        while True:
            cpu_usage = await get_cpu_usage()
            ram = psutil.virtual_memory()
            ram_percent = ram.percent    
            await websocket.send_json({
                "cpu": round(cpu_usage, 2),
                "ram_percent": round(ram_percent, 2),
                "ram_total": ram.total,
                "ram_available": ram.available
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


