from fastapi import FastAPI
from app.routers import exercise_router
app = FastAPI()

app.include_router(exercise_router.router)