"""Configuración de conexión a la base de datos."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.config.settings import get_settings
from src.database.models import Base
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Engine global de SQLAlchemy
_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Obtener engine de SQLAlchemy (singleton)."""
    global _engine
    if _engine is None:
        settings = get_settings()

        # Configurar engine basado en el tipo de base de datos
        if settings.database_url.startswith("sqlite"):
            _engine = create_engine(
                settings.database_url,
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 20,
                },
                echo=settings.debug,
            )

            # Habilitar foreign keys para SQLite
            @event.listens_for(_engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        else:
            _engine = create_engine(
                settings.database_url,
                pool_size=settings.db_pool_size,
                max_overflow=10,
                echo=settings.debug,
            )

        logger.info(f"Engine de base de datos creado: {settings.database_url}")

    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Obtener factory de sesiones (singleton)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
        logger.info("Session factory creado")

    return _session_factory


def create_db_session() -> Session:
    """
    Crear una nueva sesión de base de datos.

    Returns:
        Session: Nueva sesión de SQLAlchemy

    Note:
        Es responsabilidad del llamador cerrar la sesión.
    """
    session_factory = get_session_factory()
    return session_factory()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager para obtener sesión de base de datos.

    Yields:
        Session: Sesión de SQLAlchemy

    Example:
        with get_db_session() as session:
            transactions = session.query(Transaction).all()
    """
    session_factory = get_session_factory()
    session = session_factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_database() -> None:
    """Inicializar base de datos creando todas las tablas."""
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        raise


def reset_database() -> None:
    """Resetear base de datos eliminando y recreando todas las tablas."""
    try:
        engine = get_engine()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.warning("Base de datos reseteada completamente")
    except Exception as e:
        logger.error(f"Error al resetear base de datos: {e}")
        raise


def close_connections() -> None:
    """Cerrar todas las conexiones de base de datos."""
    global _engine, _session_factory

    if _engine:
        _engine.dispose()
        _engine = None
        logger.info("Conexiones de base de datos cerradas")

    _session_factory = None
