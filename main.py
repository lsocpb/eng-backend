from fastapi import FastAPI

from cloudinary import config
from dotenv import load_dotenv
import os

from controllers import auth_controller, user_controller, category_controller, product_controller
from starlette.middleware.cors import CORSMiddleware
from db_management.database import engine
from db_management import models

app = FastAPI()
app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(category_controller.router)
app.include_router(product_controller.router)


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

models.Base.metadata.create_all(bind=engine)

load_dotenv()

CLOUD_NAME = os.getenv("CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

config(
    cloud_name=CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)
