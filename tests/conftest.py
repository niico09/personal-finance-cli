"""Configuración común para tests de Sales Command."""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch

from src.config.settings import get_settings, reload_settings
from src.database.connection import init_database, reset_database, close_connections


@pytest.fixture(scope="session")
def test_data_dir():
    """Crear directorio temporal para datos de test."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def test_settings(test_data_dir):
    """Configuración de test con base de datos temporal."""
    test_db_path = test_data_dir / "test_sales.db"

    with patch.dict("os.environ", {
        "DATABASE_URL": f"sqlite:///{test_db_path}",
        "DEBUG": "True",
        "LOG_LEVEL": "DEBUG",
    }):
        settings = reload_settings()
        yield settings
        close_connections()


@pytest.fixture(scope="function")
def test_db(test_settings):
    """Base de datos de test inicializada."""
    init_database()
    yield
    reset_database()
    close_connections()


@pytest.fixture
def sample_categories():
    """Categorías de ejemplo para tests."""
    return [
        {"name": "alimentacion", "description": "Comida y bebidas"},
        {"name": "transporte", "description": "Transporte público y combustible"},
        {"name": "entretenimiento", "description": "Ocio y diversión"},
        {"name": "salud", "description": "Gastos médicos"},
    ]


@pytest.fixture
def sample_accounts():
    """Cuentas de ejemplo para tests."""
    return [
        {
            "name": "Cuenta Corriente",
            "account_type": "bank",
            "balance": 1500.00
        },
        {
            "name": "Tarjeta Visa",
            "account_type": "credit_card",
            "balance": 0.00,
            "credit_limit": 3000.00,
            "closing_day": 15,
            "due_day": 10
        }
    ]
