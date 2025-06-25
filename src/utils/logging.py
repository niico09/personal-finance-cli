"""Configuración de logging para Sales Command."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True,
) -> None:
    """
    Configurar sistema de logging con Rich.

    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Archivo donde guardar logs (opcional)
        console_output: Si mostrar logs en consola
    """
    # Configurar formato de logs
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configurar handlers
    handlers: list[logging.Handler] = []

    # Handler para consola con Rich
    if console_output:
        console_handler = RichHandler(
            console=Console(stderr=True),
            show_time=True,
            show_path=True,
            rich_tracebacks=True,
        )
        console_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(console_handler)

    # Handler para archivo
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            log_file,
            mode="a",
            encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    # Configurar logging básico
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=handlers,
        format=log_format,
    )

    # Configurar loggers específicos
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.WARNING)

    # Logger principal de la aplicación
    logger = logging.getLogger("sales_command")
    logger.info(f"Sistema de logging configurado - Nivel: {level}")


def get_logger(name: str) -> logging.Logger:
    """
    Obtener logger configurado para un módulo específico.

    Args:
        name: Nombre del logger (normalmente __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(f"sales_command.{name}")


class LoggerMixin:
    """Mixin para agregar capacidades de logging a cualquier clase."""

    @property
    def logger(self) -> logging.Logger:
        """Logger específico para la clase."""
        return get_logger(self.__class__.__name__)
