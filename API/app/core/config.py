
import os
from dotenv import load_dotenv

load_dotenv()

# CONFIGURACIÓN DE SEGURIDAD
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "No se ha configurado SECRET_KEY en el archivo .env"
    )

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
