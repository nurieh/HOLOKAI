from fastapi import FastAPI
from app.routers import (
    products,
    categories,
    product_images,
    users,
    auth
)

app = FastAPI(
    title="HOLOKAI API",
    description="API REST para la plataforma HOLOKAI",
    version="1.0.0"
)

app.include_router(products.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(product_images.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/")
def home():
    return {
        "message": "Bienvenido a HOLOKAI API",
        "status": "online"
    }


@app.get("/health")
def health():
    return {"status": "ok"}