"""Configuración de la aplicación Sales Command."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración principal de la aplicación Sales Command."""

    # Información de la aplicación
    app_name: str = Field(default="Sales Command", description="Nombre de la aplicación")
    app_version: str = Field(default="1.0.0", description="Versión de la aplicación")
    debug: bool = Field(default=False, description="Modo debug")

    # Base de datos
    database_url: str = Field(
        default="sqlite:///sales_data.db",
        description="URL de conexión a la base de datos"
    )
    db_pool_size: int = Field(default=5, description="Tamaño del pool de conexiones")

    # Logging
    log_level: str = Field(default="INFO", description="Nivel de logging")
    log_file: Optional[Path] = Field(
        default=Path("logs/sales-command.log"),
        description="Archivo de logs"
    )

    # Rutas de datos
    data_dir: Path = Field(default=Path("data"), description="Directorio de datos")
    exports_dir: Path = Field(default=Path("exports"), description="Directorio de exportaciones")
    backups_dir: Path = Field(default=Path("backups"), description="Directorio de backups")

    # Configuración financiera
    default_currency: str = Field(default="USD", description="Moneda por defecto")
    decimal_places: int = Field(default=2, description="Lugares decimales para montos")

    # Configuración de reportes
    enable_notifications: bool = Field(
        default=True,
        description="Habilitar notificaciones"
    )
    notification_threshold_days: int = Field(
        default=7,
        description="Días para notificaciones de presupuesto"
    )

    # Configuración de exportación
    default_export_format: str = Field(
        default="csv",
        description="Formato de exportación por defecto"
    )
    max_export_records: int = Field(
        default=10000,
        description="Máximo número de registros para exportar"    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    def __post_init__(self) -> None:
        """Crear directorios necesarios después de la inicialización."""
        for directory in [self.data_dir, self.exports_dir, self.backups_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Crear directorio de logs si se especifica un archivo
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Instancia global de configuración
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Obtener instancia singleton de configuración."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.__post_init__()
    return _settings


def reload_settings() -> Settings:
    """Recargar configuración (útil para tests)."""
    global _settings
    _settings = None
    return get_settings()
