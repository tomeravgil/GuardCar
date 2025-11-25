import asyncio
from detection.processing.detection_manager import DetectionManager
import threading

async def main():
    loop = asyncio.get_running_loop()
    manager = DetectionManager(model="yolo11n.pt")
    manager.connection_manager.asyncio_loop = loop

    # Start RabbitMQ in background thread
    manager.connection_manager.run_in_background()

    # Start event listener (async)
    asyncio.create_task(manager.event_listener())

    # Start video processing in a thread (async coroutine!)
    threading.Thread(
        target=lambda: asyncio.run(manager.run()),
        daemon=True
    ).start()

    # Keep the main loop alive forever
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
