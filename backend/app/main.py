from fastapi import FastAPI
from app.routers import exercise_router, program_router
from app import models

app = FastAPI()

app.include_router(exercise_router.router)
app.include_router(program_router.router)