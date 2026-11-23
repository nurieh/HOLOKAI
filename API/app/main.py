
from fastapi import FastAPI
from app.routers import products, categories, events

app = FastAPI(
    title="HOLOKAI API",
    description="API REST para la plataforma HOLOKAI",
    version="1.0.0"
)

# Endpoints de productos
app.include_router(
    products.router,
    prefix="/api/v1"
)

# Endpoints de categorias
app.include_router(
    categories.router,
    prefix="/api/v1"
)

app.include_router(
    events.router,
    prefix="/api/v1"
)


@app.get("/")
def home():
    return {
        "message": "Bienvenido a HOLOKAI API",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
