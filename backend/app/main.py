from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, products, sales, customers, dashboard

# Create FastAPI app
app = FastAPI(
    title="SaaS POS System API",
    description="Multi-tenant Point of Sale System",
    version="0.1.0",
    debug=settings.DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "SaaS POS System API",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "features": {
            "stripe_enabled": settings.STRIPE_ENABLED,
            "email_enabled": settings.EMAIL_ENABLED,
            "subscription_checks_enabled": settings.SUBSCRIPTION_CHECKS_ENABLED
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
