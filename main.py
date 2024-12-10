import asyncio
import os

import cloudinary
import stripe
import uvicorn
from aiohttp import web
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import services.socketio_service
from controllers import auth_controller, user_controller, category_controller, auction_controller, \
    file_upload_controller
from db_management import models
from db_management.database import engine
from tasks.auction_finished_task import scheduler, reload_tracked_auctions, check_auctions
from utils.constants import fastapi_logger as logger

app = FastAPI()
app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(category_controller.router)
app.include_router(auction_controller.router)
app.include_router(file_upload_controller.router)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.add_event_handler('startup', lambda: (reload_tracked_auctions(), check_auctions(), scheduler.start()))
app.add_event_handler('shutdown', lambda: (scheduler.shutdown()))

models.Base.metadata.create_all(bind=engine)

load_dotenv()

CLOUD_NAME = os.getenv("CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


async def start_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info", proxy_headers=True,
                            forwarded_allow_ips='*')
    server = uvicorn.Server(config)
    await server.serve()


async def start_socketio():
    await web._run_app(services.socketio_service.app)


def start_socketio_sync():
    web.run_app(services.socketio_service.app, host='0.0.0.0', port=8001)


async def start():
    await asyncio.gather(start_socketio())


if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Gather both FastAPI and SocketIO tasks to run concurrently
        loop.run_until_complete(
            asyncio.gather(
                start_fastapi(),
                start_socketio()
            )
        )
    except KeyboardInterrupt:
        logger.info("Shutting down server")
