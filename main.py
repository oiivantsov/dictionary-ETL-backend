from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import words, web_fetch

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(words.router)
app.include_router(web_fetch.router)
