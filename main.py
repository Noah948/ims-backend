from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import Base, engine
from core.config import settings
from models import *

from routes.auth_routes import router as auth_router
from routes.category_routes import router as category_router
from routes.product_routes import router as product_router  
from routes.job_routes import router as job_router  
from routes.team_routes import router as team_router  
from routes.sale_routes import router as sale_router  
from routes.expense_routes import router as expense_router
from utils.audit_listener import register_audit_listeners

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ✅ CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#audit function
register_audit_listeners()
# ✅ Routers
app.include_router(category_router)
app.include_router(product_router)
app.include_router(sale_router)
app.include_router(job_router)
app.include_router(team_router)
app.include_router(expense_router)
app.include_router(auth_router)


@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Backend is running!"}
