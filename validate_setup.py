#!/usr/bin/env python3
"""Validar configuración de VS Code para Python - Sales Command."""

import json
import subprocess
import sys
from pathlib import Path

def validate_vscode_setup():
    """Validar que VS Code esté configurado correctamente."""

    # Verificar archivos de configuración
    required_files = [
        ".vscode/settings.json",
        ".vscode/launch.json",
        ".vscode/tasks.json",
        ".vscode/extensions.json"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print("❌ Archivos de configuración faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        return False

    # Verificar configuración de Python
    settings_file = Path(".vscode/settings.json")
    if settings_file.exists():
        try:
            with open(settings_file) as f:
                settings = json.load(f)

            # Verificar configuraciones críticas
            critical_settings = {
                "python.analysis.typeCheckingMode": "strict",
                "ruff.enable": True,
                "editor.formatOnSave": True
            }

            missing_settings = []
            for key, expected_value in critical_settings.items():
                if settings.get(key) != expected_value:
                    missing_settings.append(f"{key}: {expected_value}")

            if missing_settings:
                print("❌ Configuraciones críticas faltantes:")
                for setting in missing_settings:
                    print(f"   - {setting}")
                return False

        except json.JSONDecodeError:
            print("❌ Error al leer .vscode/settings.json")
            return False

    print("✅ Configuración de VS Code validada correctamente")
    return True

def validate_python_environment():
    """Validar entorno Python."""

    # Verificar Python version
    if sys.version_info < (3, 9):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} no soportado. Requiere Python 3.9+")
        return False

    print("✅ Entorno Python validado correctamente")
    return True

def validate_project_structure():
    """Validar estructura del proyecto."""

    required_files = [
        "pyproject.toml",
        "README.md",
        ".gitignore"
    ]

    recommended_dirs = [
        "src/",
        "tests/",
        ".vscode/"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    missing_dirs = []
    for dir_path in recommended_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)

    if missing_files:
        print("❌ Archivos requeridos faltantes:")
        for file in missing_files:
            print(f"   - {file}")

    if missing_dirs:
        print("⚠️  Directorios recomendados faltantes:")
        for dir in missing_dirs:
            print(f"   - {dir}")

    if missing_files:
        return False

    print("✅ Estructura de proyecto validada")
    return True

def validate_sales_command():
    """Validar estructura específica de Sales Command."""

    required_modules = [
        "src/__init__.py",
        "src/main.py",
        "src/config/settings.py",
        "src/database/models.py",
        "src/cli/main.py",
        "tests/test_basic.py"
    ]

    missing_modules = []
    for module_path in required_modules:
        if not Path(module_path).exists():
            missing_modules.append(module_path)

    if missing_modules:
        print("❌ Módulos de Sales Command faltantes:")
        for module in missing_modules:
            print(f"   - {module}")
        return False

    print("✅ Estructura de Sales Command validada")
    return True

def test_imports():
    """Probar importaciones básicas."""
    try:
        # Verificar que los módulos principales se pueden importar
        from src.config.settings import get_settings
        from src.database.models import Transaction

        settings = get_settings()
        print(f"✅ Importaciones validadas - App: {settings.app_name}")
        return True

    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Validando configuración de Sales Command...\n")

    checks = [
        validate_python_environment(),
        validate_project_structure(),
        validate_vscode_setup(),
        validate_sales_command(),
        test_imports()
    ]

    if all(checks):
        print("\n🎉 ¡Configuración completa y correcta!")
        print("\nPróximos pasos:")
        print("1. Abrir VS Code: code .")
        print("2. Seleccionar intérprete Python: Ctrl+Shift+P → 'Python: Select Interpreter'")
        print("3. Instalar dependencias: Ctrl+Shift+P → 'Tasks: Run Task' → 'Python: Setup Proyecto'")
        print("4. Ejecutar tests: Ctrl+Shift+P → 'Python: Run All Tests'")
        print("5. Probar aplicación: python -m src.main --help")
        print("6. Comenzar desarrollo 🚀")
    else:
        print("\n❌ Configuración incompleta. Corregir errores arriba.")
        sys.exit(1)
