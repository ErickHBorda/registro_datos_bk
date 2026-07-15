# Configura el motor de base de datos asíncrono
# y provee la sesión que usan los endpoints

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# ── Motor asíncrono ────────────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={"statement_cache_size": 0},  # Requerido para Supabase pooler
)

# ── Fábrica de sesiones ────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Evita errores al acceder a datos post-commit
)


# ── Clase base para los modelos SQLAlchemy ─────────────────
class Base(DeclarativeBase):
    pass


# ── Dependencia de FastAPI ─────────────────────────────────
# Se inyecta en cada endpoint que necesite acceso a la BD
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
