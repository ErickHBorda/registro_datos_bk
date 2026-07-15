# Punto de entrada principal de la aplicación FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import personal, fotos, auth, admin, solicitudes
from app.models import solicitudes as solicitudes_models  # noqa: F401

# ── Importar todos los modelos para que Base los registre ──
from app.models import personal as personal_models  # noqa: F401
from app.models import academico as academico_models  # noqa: F401


# ── Ciclo de vida de la aplicación ─────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Se ejecuta al iniciar y al cerrar el servidor.
    - Inicio : verifica la conexión a la base de datos
    - Cierre : libera el pool de conexiones
    """
    # Inicio
    async with engine.begin() as conn:
        # Verifica que la conexión a Supabase funciona
        await conn.run_sync(lambda c: None)
    print("✅ Conexión a Supabase establecida correctamente")
    print(f"🚀 {settings.app_name} v{settings.app_version} iniciado")

    yield  # La aplicación corre aquí

    # Cierre
    await engine.dispose()
    print("🔒 Conexión a Supabase cerrada correctamente")


# ── Instancia principal de FastAPI ──────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## Ficha Digital de Registro de Personal — UNAMBA 2025

API REST para el registro y gestión de datos del personal
docente y no docente de la Universidad Nacional Micaela
Bastidas de Apurímac (UNAMBA).

**Oficina de Recursos Humanos — Sub Oficina de Escalafón**
    """,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    lifespan=lifespan,
)


# ── Middleware CORS ─────────────────────────────────────────
# Permite que el frontend React en Vercel consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# ── Registro de routers ─────────────────────────────────────
app.include_router(personal.router)
app.include_router(fotos.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(solicitudes.router_publico)
app.include_router(solicitudes.router_admin)


# ── Endpoint raíz ───────────────────────────────────────────
@app.get("/", tags=["Estado"])
async def raiz():
    return {
        "aplicacion": settings.app_name,
        "version": settings.app_version,
        "estado": "en línea",
        "docs": "/docs",
    }


# ── Health check ────────────────────────────────────────────
@app.get("/health", tags=["Estado"])
async def health_check():
    return {"status": "ok"}
