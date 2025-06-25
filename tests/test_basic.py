"""Test básico para validar configuración del proyecto."""

import pytest
from pathlib import Path

def test_project_structure():
    """Verificar que la estructura del proyecto existe."""
    base_path = Path(__file__).parent.parent

    # Verificar directorios principales
    assert (base_path / "src").exists()
    assert (base_path / "tests").exists()
    assert (base_path / ".vscode").exists()

    # Verificar archivos de configuración
    assert (base_path / "pyproject.toml").exists()
    assert (base_path / "README.md").exists()
    assert (base_path / ".gitignore").exists()


def test_import_main_modules():
    """Verificar que los módulos principales se pueden importar."""
    from src.config.settings import get_settings
    from src.database.models import Transaction, Category, Budget
    from src.utils.logging import get_logger

    # Verificar que las importaciones funcionan
    settings = get_settings()
    assert settings.app_name == "Sales Command"

    logger = get_logger("test")
    assert logger is not None


def test_database_models():
    """Verificar que los modelos de base de datos están bien definidos."""
    from src.database.models import Transaction, Category, Budget, Account

    # Verificar que las clases existen y tienen las propiedades esperadas
    assert hasattr(Transaction, '__tablename__')
    assert hasattr(Category, '__tablename__')
    assert hasattr(Budget, '__tablename__')
    assert hasattr(Account, '__tablename__')

    assert Transaction.__tablename__ == "transactions"
    assert Category.__tablename__ == "categories"


def test_settings_configuration():
    """Verificar configuración de la aplicación."""
    from src.config.settings import get_settings

    settings = get_settings()

    # Verificar valores por defecto
    assert settings.app_name == "Sales Command"
    assert settings.app_version == "1.0.0"
    assert settings.default_currency == "USD"
    assert settings.decimal_places == 2

    # Verificar tipos
    assert isinstance(settings.debug, bool)
    assert isinstance(settings.decimal_places, int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
