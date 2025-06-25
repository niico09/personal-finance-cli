#!/usr/bin/env python3
"""
Validación completa del proyecto Sales Command.

Este script valida que el proyecto cumple con:
- Python Rules 2024-2025 para VS Code
- Estructura de proyecto correcta
- Configuraciones requeridas
- Funcionalidad básica
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict


def check_mark(condition: bool) -> str:
    """Retorna marca de verificación o X según condición."""
    return "✅" if condition else "❌"

def validate_project_structure() -> bool:
    """Validar estructura del proyecto."""
    print("🏗️  Validando estructura del proyecto...")

    required_files = [
        "pyproject.toml",
        "README.md",
        ".gitignore",
        ".env.example",
        "Makefile",
        "init_db.py",
        "validate_setup.py"
    ]

    required_dirs = [
        "src/",
        "src/cli/",
        "src/cli/commands/",
        "src/config/",
        "src/database/",
        "src/services/",
        "src/utils/",
        "tests/",
        ".vscode/"
    ]

    vscode_files = [
        ".vscode/settings.json",
        ".vscode/launch.json",
        ".vscode/tasks.json",
        ".vscode/extensions.json",
        ".vscode/snippets/python.json"
    ]

    all_valid = True

    for file_path in required_files:
        exists = Path(file_path).exists()
        print(f"  {check_mark(exists)} {file_path}")
        if not exists:
            all_valid = False

    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        print(f"  {check_mark(exists)} {dir_path}")
        if not exists:
            all_valid = False

    print("  📁 Configuración VS Code:")
    for file_path in vscode_files:
        exists = Path(file_path).exists()
        print(f"    {check_mark(exists)} {file_path}")
        if not exists:
            all_valid = False

    return all_valid

def validate_python_environment() -> bool:
    """Validar entorno Python."""
    print("🐍 Validando entorno Python...")

    version_ok = sys.version_info >= (3, 9)
    print(f"  {check_mark(version_ok)} Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    tools = {
        "ruff": ["ruff", "--version"],
        "mypy": ["mypy", "--version"],
        "pytest": ["pytest", "--version"]
    }

    tools_ok = True
    for tool_name, cmd in tools.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            version = result.stdout.strip().split()[1] if result.stdout else "unknown"
            print(f"  {check_mark(True)} {tool_name} {version}")
        except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
            print(f"  {check_mark(False)} {tool_name} (no disponible)")
            tools_ok = False

    return version_ok and tools_ok

def validate_vscode_settings() -> bool:
    """Validar configuración de VS Code."""
    print("⚙️  Validando configuración VS Code...")

    settings_file = Path(".vscode/settings.json")
    if not settings_file.exists():
        print(f"  {check_mark(False)} settings.json no encontrado")
        return False

    try:
        with open(settings_file, encoding='utf-8') as f:
            settings = json.load(f)

        required_settings = {
            "python.testing.pytestEnabled": True,
            "ruff.enable": True,
            "editor.formatOnSave": True,
            "python.analysis.typeCheckingMode": "strict"
        }

        all_good = True
        for key, expected_value in required_settings.items():
            actual_value = settings.get(key)
            is_correct = actual_value == expected_value
            print(f"  {check_mark(is_correct)} {key}: {actual_value}")
            if not is_correct:
                all_good = False

        return all_good

    except json.JSONDecodeError:
        print(f"  {check_mark(False)} settings.json inválido")
        return False

def validate_dependencies() -> bool:
    """Validar dependencias del proyecto."""
    print("📦 Validando dependencias...")

    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        print(f"  {check_mark(False)} pyproject.toml no encontrado")
        return False

    try:
        import pydantic_settings
        import rich
        import sqlalchemy
        import typer
        print(f"  {check_mark(True)} Dependencias principales instaladas")

        dev_deps_ok = True
        try:
            import pytest
            import ruff
            print(f"  {check_mark(True)} Dependencias de desarrollo instaladas")
        except ImportError:
            print(f"  {check_mark(False)} Dependencias de desarrollo faltantes")
            dev_deps_ok = False

        return dev_deps_ok

    except ImportError as e:
        print(f"  {check_mark(False)} Dependencias faltantes: {e}")
        return False

def validate_database() -> bool:
    """Validar configuración de base de datos."""
    print("🗄️  Validando base de datos...")

    try:
        from src.database.connection import get_engine
        from src.database.models import Base, Budget, Investment, Transaction

        print(f"  {check_mark(True)} Modelos de base de datos importables")

        db_file = Path("sales_data.db")
        if db_file.exists():
            print(f"  {check_mark(True)} Base de datos existe")
        else:
            print("  ⚠️  Base de datos no existe (se creará automáticamente)")

        return True

    except ImportError as e:
        print(f"  {check_mark(False)} Error importando modelos: {e}")
        return False

def validate_cli_functionality() -> bool:
    """Validar funcionalidad básica del CLI."""
    print("🖥️  Validando funcionalidad CLI...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.main", "--help"],
            check=False, capture_output=True,
            text=True,
            timeout=10
        )

        cli_works = result.returncode == 0 and ("Sales Command" in result.stdout or "sales command" in result.stdout.lower())
        print(f"  {check_mark(cli_works)} CLI principal funcional")

        if cli_works:
            subcommands = ["transactions", "budgets", "investments", "reports"]
            subcommands_ok = True

            for cmd in subcommands:
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "src.main", cmd, "--help"],
                        check=False, capture_output=True,
                        text=True,
                        timeout=5
                    )
                    cmd_works = result.returncode == 0
                    print(f"    {check_mark(cmd_works)} {cmd}")
                    if not cmd_works:
                        subcommands_ok = False
                except subprocess.TimeoutExpired:
                    print(f"    {check_mark(False)} {cmd} (timeout)")
                    subcommands_ok = False

            return subcommands_ok

        return False

    except Exception as e:
        print(f"  {check_mark(False)} Error probando CLI: {e}")
        return False

def run_tests() -> bool:
    """Ejecutar tests del proyecto."""
    print("🧪 Ejecutando tests...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            check=False, capture_output=True,
            text=True,
            timeout=30
        )

        tests_passed = result.returncode == 0

        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if "passed" in line and ("failed" in line or "error" in line or "warning" in line):
                print(f"  📊 {line.strip()}")
                break

        print(f"  {check_mark(tests_passed)} Tests ejecutados exitosamente")

        return tests_passed

    except subprocess.TimeoutExpired:
        print(f"  {check_mark(False)} Tests timeout")
        return False
    except Exception as e:
        print(f"  {check_mark(False)} Error ejecutando tests: {e}")
        return False

def generate_summary(results: Dict[str, bool]) -> None:
    """Generar resumen final."""
    print("\n" + "="*60)
    print("📋 RESUMEN DE VALIDACIÓN")
    print("="*60)

    total_checks = len(results)
    passed_checks = sum(results.values())

    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")

    print("-"*60)
    print(f"Total: {passed_checks}/{total_checks} verificaciones pasadas")

    if passed_checks == total_checks:
        print("\n🎉 ¡PROYECTO COMPLETAMENTE VALIDADO!")
        print("\nPróximos pasos:")
        print("1. Abrir VS Code: code .")
        print("2. Seleccionar intérprete Python (Ctrl+Shift+P)")
        print("3. Ejecutar: python -m src.main --help")
        print("4. Comenzar desarrollo 🚀")
    elif passed_checks >= total_checks * 0.8:
        print("\n⚠️  PROYECTO MAYORMENTE FUNCIONAL")
        print("Corregir elementos faltantes para validación completa.")
    else:
        print("\n❌ PROYECTO NECESITA TRABAJO ADICIONAL")
        print("Revisar elementos fallidos arriba.")

def main() -> None:
    """Función principal de validación."""
    print("🔍 VALIDADOR SALES COMMAND - Python Rules 2024-2025")
    print("="*60)

    validation_results = {
        "Estructura del Proyecto": validate_project_structure(),
        "Entorno Python": validate_python_environment(),
        "Configuración VS Code": validate_vscode_settings(),
        "Dependencias": validate_dependencies(),
        "Base de Datos": validate_database(),
        "Funcionalidad CLI": validate_cli_functionality(),
        "Tests": run_tests()
    }

    generate_summary(validation_results)

    total_passed = sum(validation_results.values())
    total_checks = len(validation_results)

    if total_passed == total_checks:
        sys.exit(0)
    elif total_passed >= total_checks * 0.8:
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
