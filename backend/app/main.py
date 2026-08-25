from fastapi import FastAPI
from app.routers import exercise_router, program_router, program_week_router, workout_day_router, \
    workout_exercise_router, planned_set_router, auth_router
from app import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exercise_router.router)
app.include_router(program_router.router)
app.include_router(program_week_router.router)
app.include_router(workout_day_router.router)
app.include_router(workout_exercise_router.router)
app.include_router(planned_set_router.router)
app.include_router(auth_router.router)