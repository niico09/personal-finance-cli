#!/usr/bin/env python3
"""
Punto de entrada principal para Sales Command CLI.
Gestión financiera personal completa via línea de comandos.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.traceback import install

# Configurar rich para tracebacks mejorados
install(show_locals=True)

# Importar comandos CLI
from src.cli.main import app
from src.config.settings import get_settings
from src.database.connection import init_database
from src.utils.logging import setup_logging

console = Console()

def setup_application() -> None:
    """Configurar la aplicación antes de ejecutar comandos."""
    try:
        # Configurar logging
        settings = get_settings()
        setup_logging(settings.log_level, settings.log_file)

        # Inicializar base de datos
        init_database()

    except Exception as e:
        console.print(f"[red]Error al inicializar la aplicación: {e}[/red]")
        sys.exit(1)

def main() -> None:
    """Función principal de la aplicación."""
    try:
        # Configurar aplicación
        setup_application()

        # Ejecutar CLI
        app()

    except KeyboardInterrupt:
        console.print("\n[yellow]Operación cancelada por el usuario[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error inesperado: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
