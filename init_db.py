"""Script para inicializar la base de datos."""

from __future__ import annotations

from sqlalchemy import text

from src.database.connection import get_engine, get_db_session
from src.database.models import Base
from src.utils.logging import get_logger

logger = get_logger(__name__)


def init_database():
    """Inicializar base de datos creando todas las tablas."""
    try:
        engine = get_engine()

        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)

        logger.info("Base de datos inicializada correctamente")
        print("✅ Base de datos inicializada correctamente")        # Verificar conexión
        with get_db_session() as session:
            session.execute(text("SELECT 1"))

        print("✅ Conexión a la base de datos verificada")

    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        print(f"❌ Error al inicializar base de datos: {e}")
        raise


if __name__ == "__main__":
    init_database()
