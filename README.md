# 💰 Sales Command - Gestión Financiera Personal CLI

**Sales Command** es una aplicación de línea de comandos completa para la gestión financiera personal. Diseñada para proporcionar control total sobre tus finanzas mediante una interfaz CLI intuitiva y potente.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-pytest-yellow.svg)](https://pytest.org/)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-red.svg)](https://github.com/astral-sh/ruff)

## 🚀 Características Principales

### 🏦 Gestión Inteligente de Transacciones
- ✅ Registro automático de fecha y hora
- ✅ Descripciones contextuales detalladas
- ✅ Transacciones recurrentes configurables
- ✅ Sistema de categorización personalizable

### 📊 Presupuestos y Control
- ✅ Presupuestos personalizados por categoría
- ✅ Alertas en tiempo real
- ✅ Seguimiento de objetivos financieros
- ✅ Monitor de límites de gasto

### 📈 Análisis y Reportes
- ✅ Informes detallados por categoría
- ✅ Balance de ingresos vs gastos
- ✅ Tendencias temporales
- ✅ Exportación a CSV/JSON

### 💳 Gestión de Tarjetas
- ✅ Control de límites de crédito
- ✅ Calendario de pagos
- ✅ Seguimiento de deudas
- ✅ Historial por tarjeta

### 💰 Módulo de Inversiones
- ✅ Portafolio diversificado
- ✅ Historial de operaciones
- ✅ Seguimiento de rendimientos
- ✅ Valoración de cartera

## 📦 Instalación

### Requisitos Previos
- Python 3.9 o superior
- pip o uv (recomendado)

### Instalación con uv (recomendado)
```bash
# Clonar el repositorio
git clone https://github.com/username/sales-command.git
cd sales-command

# Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
pip install uv
uv sync --dev

# Configurar base de datos
uv run python -m src.database.setup
```

### Instalación con pip
```bash
# Clonar el repositorio
git clone https://github.com/username/sales-command.git
cd sales-command

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate

# Instalar dependencias
pip install -e .
pip install -r requirements-dev.txt

# Configurar base de datos
python -m src.database.setup
```

## 🎯 Uso Rápido

### Comandos Básicos

```bash
# Agregar un gasto
sales add gasto -c comida -m 25.50 -d "Almuerzo en restaurante"

# Ver resumen del día
sales summary today

# Revisar estado del presupuesto
sales budget status

# Generar reporte mensual
sales report monthly

# Agregar ingreso
sales add ingreso -m 3500.00 -d "Salario mensual"

# Configurar presupuesto
sales budget set -c transporte -a 200.00 -p monthly
```

### Gestión de Tarjetas

```bash
# Agregar tarjeta
sales cards add -n "Visa Principal" -l 5000.00 -c 15 -v 10

# Ver estado de tarjetas
sales cards status

# Registrar pago de tarjeta
sales cards pay -n "Visa Principal" -m 500.00
```

### Módulo de Inversiones

```bash
# Agregar inversión
sales investments add -t acciones -s AAPL -q 10 -p 150.00

# Ver portafolio
sales investments portfolio

# Registrar dividendo
sales investments dividend -s AAPL -m 25.00
```

## 📊 Ejemplos de Uso

### Flujo de Trabajo Diario

```bash
# Iniciar el día revisando el resumen
sales summary today

# Agregar gastos del día
sales add gasto -c transporte -m 5.50 -d "Metro"
sales add gasto -c comida -m 18.75 -d "Almuerzo"
sales add gasto -c entretenimiento -m 12.00 -d "Café"

# Revisar cómo va el presupuesto
sales budget status

# Ver tendencias de la semana
sales trends weekly
```

### Configuración Inicial

```bash
# Configurar categorías principales
sales categories add transporte "Gastos de transporte"
sales categories add comida "Alimentación y restaurantes"
sales categories add entretenimiento "Ocio y entretenimiento"
sales categories add servicios "Servicios y utilidades"

# Establecer presupuestos
sales budget set -c transporte -a 150.00 -p monthly
sales budget set -c comida -a 400.00 -p monthly
sales budget set -c entretenimiento -a 200.00 -p monthly

# Configurar ingresos recurrentes
sales recurring add -t ingreso -a 3500.00 -d "Salario" -f monthly
```

## 🛠️ Desarrollo

### Configuración del Entorno de Desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/username/sales-command.git
cd sales-command

# Configurar entorno de desarrollo
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
pip install uv
uv sync --dev

# Configurar pre-commit hooks
uv run pre-commit install
```

### Ejecutar Tests

```bash
# Ejecutar todos los tests
uv run pytest

# Ejecutar tests con coverage
uv run pytest --cov

# Ejecutar tests específicos
uv run pytest tests/test_transactions.py -v

# Ejecutar tests en modo watch
uv run pytest-watch
```

### Linting y Formateo

```bash
# Verificar código con ruff
uv run ruff check .

# Formatear código
uv run ruff format .

# Verificar tipos con mypy
uv run mypy src/

# Ejecutar todas las verificaciones
uv run pre-commit run --all-files
```

## 📁 Estructura del Proyecto

```
sales-command/
├── .vscode/                 # Configuración de VS Code
│   ├── settings.json
│   ├── launch.json
│   ├── tasks.json
│   └── extensions.json
├── src/                     # Código fuente principal
│   ├── __init__.py
│   ├── main.py             # Punto de entrada CLI
│   ├── cli/                # Comandos CLI
│   ├── models/             # Modelos de datos
│   ├── database/           # Configuración de base de datos
│   ├── services/           # Lógica de negocio
│   ├── utils/              # Utilidades comunes
│   └── config/             # Configuración
├── tests/                  # Tests unitarios e integración
├── docs/                   # Documentación
├── pyproject.toml          # Configuración del proyecto
├── .gitignore             # Archivos ignorados por git
├── .env.example           # Variables de entorno ejemplo
├── README.md              # Este archivo
└── LICENSE                # Licencia MIT
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Copia `.env.example` a `.env` y personaliza:

```bash
# Configuración de base de datos
DATABASE_URL=sqlite:///sales_data.db

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=./logs/sales-command.log

# Configuración de la aplicación
DEFAULT_CURRENCY=USD
DECIMAL_PLACES=2
```

### Configuración de la Base de Datos

```bash
# Crear base de datos inicial
uv run python -m src.database.setup

# Ejecutar migraciones
uv run alembic upgrade head

# Crear migración nueva
uv run alembic revision --autogenerate -m "descripción"
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

### Estándares de Código

- Seguir PEP 8 (aplicado automáticamente con Ruff)
- Type hints obligatorios
- Docstrings en funciones públicas
- Tests para nueva funcionalidad
- Coverage mínimo del 80%

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🎯 Roadmap

### Versión 1.0
- [x] Gestión básica de transacciones
- [x] Sistema de presupuestos
- [x] Reportes básicos
- [ ] Módulo de inversiones completo
- [ ] Exportación de datos
- [ ] Actualizacion precios cryptos e inversiones
---

> **Sales Command** - Transformando la gestión financiera personal mediante herramientas CLI potentes y fáciles de usar.

Hecho con ❤️ por la comunidad de desarrolladores financieros.
