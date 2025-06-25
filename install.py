#!/usr/bin/env python3
"""Script de instalación rápida para Sales Command."""

import subprocess
import sys
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """Ejecutar comando y mostrar resultado."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Comando no encontrado: {command.split()[0]}")
        return False

def main():
    """Función principal de instalación."""
    print("🚀 Instalación rápida de Sales Command")
    print("=" * 40)

    # Verificar Python
    if sys.version_info < (3, 9):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} no compatible. Requiere Python 3.9+")
        sys.exit(1)

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

    # Crear entorno virtual si no existe
    venv_path = Path("venv")
    if not venv_path.exists():
        if not run_command("python -m venv venv", "Creando entorno virtual"):
            sys.exit(1)
    else:
        print("✅ Entorno virtual ya existe")

    # Detectar sistema operativo para activación
    if sys.platform == "win32":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"

    # Actualizar pip
    run_command(f"{python_cmd} -m pip install --upgrade pip", "Actualizando pip")

    # Instalar uv
    if not run_command(f"{pip_cmd} install uv", "Instalando uv"):
        sys.exit(1)

    # Sincronizar dependencias
    if not run_command("uv sync --dev", "Instalando dependencias"):
        print("⚠️  Error con uv sync, intentando instalación alternativa...")
        # Fallback a pip install
        if Path("pyproject.toml").exists():
            run_command(f"{pip_cmd} install -e .", "Instalación con pip")

    # Verificar instalación
    print("\n🔍 Verificando instalación...")

    # Probar importaciones básicas
    try:
        subprocess.run([
            python_cmd, "-c",
            "from src.config.settings import get_settings; print('✅ Importaciones OK')"
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Error en importaciones básicas")
        sys.exit(1)

    print("\n🎉 ¡Instalación completada exitosamente!")
    print("\nPróximos pasos:")
    print("1. Activar entorno virtual:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Abrir VS Code: code .")
    print("3. Seleccionar intérprete Python (Ctrl+Shift+P)")
    print("4. Ejecutar tests: uv run pytest")
    print("5. Probar aplicación: uv run python -m src.main --help")

if __name__ == "__main__":
    main()
