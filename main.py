# main.py

from fastapi import FastAPI
from core.database import Base, engine
from core.config import settings

from routes.user_routes import router as user_router
from routes.auth_routes import router as auth_router
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(user_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}
