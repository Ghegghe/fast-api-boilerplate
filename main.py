from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import bearer
from routers import (
    person,
    user,
    vehicle,
)


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(bearer.router)
app.include_router(user.router)

app.include_router(person.router)
app.include_router(vehicle.router)
