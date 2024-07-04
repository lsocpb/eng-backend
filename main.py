from fastapi import FastAPI

from controllers import auth_controller, user_controller
from starlette.middleware.cors import CORSMiddleware
from db_management.database import engine
from db_management import models

app = FastAPI()
app.include_router(auth_controller.router)
app.include_router(user_controller.router)

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