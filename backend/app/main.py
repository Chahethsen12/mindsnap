from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models  # Loads all models so Base creates the tables

from app.routes import auth, snaps

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MindSnap API",
    description="AI-powered visual second brain — save, recognize, and search anything.",
    version="1.0.0"
)

# Allow React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(auth.router)
app.include_router(snaps.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "MindSnap API is running 🚀"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
