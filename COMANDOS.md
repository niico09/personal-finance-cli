# 📚 Sales Command - Guía Completa de Comandos

Esta guía documenta todos los comandos disponibles en **Sales Command**, una aplicación CLI completa para la gestión financiera personal.

## 🚀 Comandos de Inicio

### Comando Base
```bash
uv run python -m src.main [OPTIONS] COMMAND [ARGS]...
```

### Opciones Globales
- `--verbose` (`-v`): Habilitar salida detallada
- `--debug` (`-d`): Habilitar modo debug
- `--help` (`-h`): Mostrar ayuda
- `--install-completion`: Instalar autocompletado para el shell actual
- `--show-completion`: Mostrar autocompletado para el shell actual

---

## 📋 Comandos Principales

### 1. `summary` - Resumen Financiero Rápido
**Propósito**: Mostrar un resumen financiero del período especificado

```bash
uv run python -m src.main summary [OPTIONS]
```

**Opciones**:
- `--period` (`-p`): Período para el resumen
  - Valores: `today`, `week`, `month`, `year`
  - Predeterminado: `today`

**Ejemplos**:
```bash
# Resumen del día actual
uv run python -m src.main summary

# Resumen semanal
uv run python -m src.main summary --period week

# Resumen mensual
uv run python -m src.main summary --period month

# Resumen anual
uv run python -m src.main summary --period year
```

### 2. `quick-add` - Agregar Transacción Rápida
**Propósito**: Interfaz rápida para agregar transacciones

```bash
uv run python -m src.main quick-add
```

### 3. `status` - Estado del Sistema
**Propósito**: Verificar el estado y configuración del sistema

```bash
uv run python -m src.main status
```

### 4. `version` - Información de Versión
**Propósito**: Mostrar información de la versión actual

```bash
uv run python -m src.main version
```

---

## 💳 Módulo de Transacciones

### Comando Base
```bash
uv run python -m src.main transactions [COMMAND] [OPTIONS]
```

### Subcomandos Disponibles

#### `add` - Agregar Nueva Transacción
**Propósito**: Registrar una nueva transacción (ingreso o gasto)

```bash
uv run python -m src.main transactions add [OPTIONS] AMOUNT DESCRIPTION
```

**Argumentos Requeridos**:
- `AMOUNT` (float): Monto de la transacción
- `DESCRIPTION` (texto): Descripción de la transacción

**Opciones**:
- `--category` (`-c`): Categoría (predeterminado: `general`)
- `--type` (`-t`): Tipo de transacción
  - Valores: `income` (ingreso), `expense` (gasto)
  - Predeterminado: `expense`
- `--account` (`-a`): Cuenta asociada (predeterminado: `default`)
- `--payment` (`-p`): Método de pago (predeterminado: `cash`)
- `--tags`: Etiquetas separadas por comas
- `--notes` (`-n`): Notas adicionales

**Ejemplos**:
```bash
# Agregar un gasto básico
uv run python -m src.main transactions add 25.50 "Almuerzo en restaurante"

# Agregar gasto con categoría específica
uv run python -m src.main transactions add 25.50 "Almuerzo" --category comida --type expense

# Agregar ingreso
uv run python -m src.main transactions add 3500.00 "Salario mensual" --category salario --type income

# Transacción completa con todas las opciones
uv run python -m src.main transactions add 45.00 "Gasolina" \
  --category transporte \
  --type expense \
  --account "Cuenta Principal" \
  --payment "tarjeta_credito" \
  --tags "combustible,auto" \
  --notes "Gasolinera Shell"
```

#### `list` - Listar Transacciones
**Propósito**: Mostrar lista de transacciones recientes

```bash
uv run python -m src.main transactions list [OPTIONS]
```

**Opciones**:
- `--limit`: Número máximo de transacciones a mostrar
- `--category`: Filtrar por categoría específica
- `--type`: Filtrar por tipo (income/expense)
- `--from-date`: Fecha de inicio (YYYY-MM-DD)
- `--to-date`: Fecha de fin (YYYY-MM-DD)

**Ejemplos**:
```bash
# Listar últimas transacciones
uv run python -m src.main transactions list

# Listar solo gastos
uv run python -m src.main transactions list --type expense

# Listar por categoría
uv run python -m src.main transactions list --category comida

# Listar con límite
uv run python -m src.main transactions list --limit 10
```

#### `summary` - Resumen de Transacciones
**Propósito**: Mostrar resumen estadístico de transacciones

```bash
uv run python -m src.main transactions summary [OPTIONS]
```

#### `delete` - Eliminar Transacción
**Propósito**: Eliminar una transacción existente

```bash
uv run python -m src.main transactions delete [TRANSACTION_ID]
```

**Argumentos**:
- `TRANSACTION_ID`: ID de la transacción a eliminar

**Ejemplo**:
```bash
# Eliminar transacción por ID
uv run python -m src.main transactions delete fd1f22eb-aaa9-42cc-b40b-12f48b2406a8

# También funciona con ID parcial
uv run python -m src.main transactions delete fd1f22eb
```

---

## 💰 Módulo de Presupuestos

### Comando Base
```bash
uv run python -m src.main budgets [COMMAND] [OPTIONS]
```

### Subcomandos Disponibles

#### `create` - Crear Nuevo Presupuesto
**Propósito**: Crear un nuevo presupuesto para control de gastos

```bash
uv run python -m src.main budgets create [OPTIONS] NAME
```

**Argumentos Requeridos**:
- `NAME` (texto): Nombre del presupuesto

**Opciones**:
- `--period` (`-p`): Tipo de período
  - Valores: `monthly`, `yearly`
  - Predeterminado: `monthly`
- `--year` (`-y`): Año del presupuesto (entero)
- `--month` (`-m`): Mes del presupuesto (1-12)
- `--description` (`-d`): Descripción del presupuesto

**Ejemplos**:
```bash
# Crear presupuesto mensual básico
uv run python -m src.main budgets create "Presupuesto Junio"

# Crear presupuesto con descripción
uv run python -m src.main budgets create "Presupuesto Junio" \
  --description "Presupuesto familiar para junio 2025"

# Crear presupuesto anual
uv run python -m src.main budgets create "Presupuesto 2025" \
  --period yearly --year 2025

# Crear presupuesto para mes específico
uv run python -m src.main budgets create "Presupuesto Diciembre" \
  --month 12 --year 2025
```

#### `add-category` - Agregar Categoría al Presupuesto
**Propósito**: Asignar monto presupuestado a una categoría específica

```bash
uv run python -m src.main budgets add-category [OPTIONS] BUDGET_ID CATEGORY AMOUNT
```

**Argumentos Requeridos**:
- `BUDGET_ID` (texto): ID del presupuesto
- `CATEGORY` (texto): Nombre de la categoría
- `AMOUNT` (float): Monto asignado a la categoría

**Opciones**:
- `--description` (`-d`): Descripción de la categoría

**Ejemplos**:
```bash
# Agregar categoría básica
uv run python -m src.main budgets add-category 69bdbb3b-e9bd-4083-9b2b-33b36ba7fe83 comida 400.00

# Agregar categoría con descripción
uv run python -m src.main budgets add-category 69bdbb3b-e9bd-4083-9b2b-33b36ba7fe83 \
  transporte 150.00 --description "Gastos de transporte público y combustible"

# Múltiples categorías (ejecutar por separado)
uv run python -m src.main budgets add-category [BUDGET_ID] comida 400.00
uv run python -m src.main budgets add-category [BUDGET_ID] transporte 150.00
uv run python -m src.main budgets add-category [BUDGET_ID] entretenimiento 200.00
```

#### `list` - Listar Presupuestos
**Propósito**: Mostrar todos los presupuestos existentes

```bash
uv run python -m src.main budgets list [OPTIONS]
```

**Opciones**:
- `--active-only`: Mostrar solo presupuestos activos
- `--period`: Filtrar por período (monthly/yearly)

#### `analyze` - Analizar Progreso del Presupuesto
**Propósito**: Mostrar análisis detallado de un presupuesto específico

```bash
uv run python -m src.main budgets analyze [BUDGET_ID]
```

#### `current` - Mostrar Presupuesto Actual
**Propósito**: Mostrar el presupuesto activo del período actual

```bash
uv run python -m src.main budgets current
```

#### `delete` - Eliminar Presupuesto
**Propósito**: Eliminar un presupuesto existente

```bash
uv run python -m src.main budgets delete [BUDGET_ID]
```

---

## 📈 Módulo de Inversiones

### Comando Base
```bash
uv run python -m src.main investments [COMMAND] [OPTIONS]
```

### Subcomandos Disponibles

#### `add` - Agregar Nueva Inversión
**Propósito**: Registrar una nueva inversión en el portafolio

```bash
uv run python -m src.main investments add [OPTIONS] NAME INVESTMENT_TYPE AMOUNT
```

**Argumentos Requeridos**:
- `NAME` (texto): Nombre de la inversión
- `INVESTMENT_TYPE` (texto): Tipo de inversión
- `AMOUNT` (float): Monto inicial invertido

**Tipos de Inversión Disponibles**:
- `stock`: Acciones
- `bond`: Bonos
- `fund`: Fondos mutuos/ETFs
- `crypto`: Criptomonedas
- `real_estate`: Bienes raíces
- `commodity`: Materias primas
- `other`: Otros tipos

**Opciones**:
- `--shares` (`-s`): Número de acciones/unidades (float)
- `--price` (`-p`): Precio de compra por unidad (float)
- `--description` (`-d`): Descripción de la inversión
- `--date`: Fecha de compra (YYYY-MM-DD)

**Ejemplos**:
```bash
# Inversión básica en acciones
uv run python -m src.main investments add "Apple Stock" stock 1500.00

# Inversión completa con detalles
uv run python -m src.main investments add "Apple Stock" stock 1500.00 \
  --shares 10 \
  --price 150.00 \
  --description "Acciones de Apple Inc." \
  --date 2025-06-24

# Inversión en criptomonedas
uv run python -m src.main investments add "Bitcoin" crypto 5000.00 \
  --shares 0.1 \
  --price 50000.00 \
  --description "Bitcoin comprado en exchange"

# Fondo de inversión
uv run python -m src.main investments add "S&P 500 ETF" fund 2500.00 \
  --shares 50 \
  --price 50.00 \
  --description "ETF que sigue el índice S&P 500"
```

#### `list` - Listar Inversiones
**Propósito**: Mostrar todas las inversiones del portafolio

```bash
uv run python -m src.main investments list [OPTIONS]
```

**Opciones**:
- `--type`: Filtrar por tipo de inversión
- `--sort-by`: Ordenar por campo específico
- `--limit`: Número máximo de inversiones a mostrar

#### `update-value` - Actualizar Valor de Inversión
**Propósito**: Actualizar el valor actual de mercado de una inversión

```bash
uv run python -m src.main investments update-value [INVESTMENT_ID] [NEW_VALUE]
```

**Argumentos**:
- `INVESTMENT_ID`: ID de la inversión
- `NEW_VALUE`: Nuevo valor total de la inversión

**Ejemplo**:
```bash
# Actualizar valor de una inversión
uv run python -m src.main investments update-value f1aaf8a4-02a4-41d8-9715-c2b3ed6dc572 1650.00
```

#### `portfolio` - Resumen del Portafolio
**Propósito**: Mostrar resumen completo del portafolio de inversiones

```bash
uv run python -m src.main investments portfolio [OPTIONS]
```

**Opciones**:
- `--detailed`: Mostrar información detallada
- `--group-by`: Agrupar por tipo de inversión

#### `performance` - Rendimiento Detallado
**Propósito**: Mostrar análisis de rendimiento de una inversión específica

```bash
uv run python -m src.main investments performance [INVESTMENT_ID]
```

#### `delete` - Eliminar Inversión
**Propósito**: Eliminar una inversión del portafolio

```bash
uv run python -m src.main investments delete [INVESTMENT_ID]
```

---

## 📊 Módulo de Reportes

### Comando Base
```bash
uv run python -m src.main reports [COMMAND] [OPTIONS]
```

### Subcomandos Disponibles

#### `monthly` - Reporte Mensual
**Propósito**: Generar reporte financiero completo mensual

```bash
uv run python -m src.main reports monthly [OPTIONS]
```

**Opciones**:
- `--month`: Mes específico (1-12)
- `--year`: Año específico
- `--export`: Exportar a archivo (CSV/JSON)
- `--detailed`: Incluir información detallada

**Ejemplos**:
```bash
# Reporte del mes actual
uv run python -m src.main reports monthly

# Reporte de mes específico
uv run python -m src.main reports monthly --month 5 --year 2025

# Reporte detallado
uv run python -m src.main reports monthly --detailed

# Exportar reporte
uv run python -m src.main reports monthly --export csv
```

#### `yearly` - Reporte Anual
**Propósito**: Generar reporte financiero completo anual

```bash
uv run python -m src.main reports yearly [OPTIONS]
```

**Opciones**:
- `--year`: Año específico
- `--export`: Exportar a archivo
- `--include-projections`: Incluir proyecciones

**Ejemplos**:
```bash
# Reporte del año actual
uv run python -m src.main reports yearly

# Reporte de año específico
uv run python -m src.main reports yearly --year 2024
```

#### `categories` - Reporte por Categorías
**Propósito**: Generar análisis detallado por categorías de gastos

```bash
uv run python -m src.main reports categories [OPTIONS]
```

**Opciones**:
- `--period`: Período de análisis (month/year)
- `--top-n`: Mostrar top N categorías
- `--include-subcategories`: Incluir subcategorías

**Ejemplos**:
```bash
# Reporte de categorías básico
uv run python -m src.main reports categories

# Top 5 categorías del mes
uv run python -m src.main reports categories --period month --top-n 5

# Análisis anual de categorías
uv run python -m src.main reports categories --period year
```

#### `cash-flow` - Reporte de Flujo de Efectivo
**Propósito**: Generar análisis de flujo de efectivo

```bash
uv run python -m src.main reports cash-flow [OPTIONS]
```

**Opciones**:
- `--period`: Período de análisis
- `--granularity`: Granularidad (daily/weekly/monthly)
- `--forecast`: Incluir proyección

**Ejemplos**:
```bash
# Flujo de efectivo básico
uv run python -m src.main reports cash-flow

# Flujo mensual con proyección
uv run python -m src.main reports cash-flow --granularity monthly --forecast
```

---

## 🛠️ Comandos de Configuración y Utilidades

### Variables de Entorno
Puedes configurar el comportamiento con variables de entorno:

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

### Comandos de Sistema

#### Autocompletado
```bash
# Instalar autocompletado para bash
uv run python -m src.main --install-completion bash

# Instalar autocompletado para PowerShell
uv run python -m src.main --install-completion powershell

# Mostrar script de autocompletado
uv run python -m src.main --show-completion
```

---

## 📝 Flujos de Trabajo Comunes

### 1. Configuración Inicial
```bash
# 1. Verificar estado del sistema
uv run python -m src.main status

# 2. Crear primer presupuesto
uv run python -m src.main budgets create "Mi Primer Presupuesto" --description "Presupuesto inicial"

# 3. Agregar categorías principales
uv run python -m src.main budgets add-category [BUDGET_ID] comida 400.00
uv run python -m src.main budgets add-category [BUDGET_ID] transporte 150.00
uv run python -m src.main budgets add-category [BUDGET_ID] entretenimiento 200.00
```

### 2. Uso Diario
```bash
# 1. Ver resumen del día
uv run python -m src.main summary

# 2. Agregar transacciones del día
uv run python -m src.main transactions add 5.50 "Metro" --category transporte
uv run python -m src.main transactions add 18.75 "Almuerzo" --category comida

# 3. Verificar progreso del presupuesto
uv run python -m src.main budgets analyze [BUDGET_ID]
```

### 3. Análisis Mensual
```bash
# 1. Generar reporte mensual completo
uv run python -m src.main reports monthly

# 2. Analizar categorías
uv run python -m src.main reports categories --period month

# 3. Revisar flujo de efectivo
uv run python -m src.main reports cash-flow --granularity monthly
```

### 4. Gestión de Inversiones
```bash
# 1. Agregar nueva inversión
uv run python -m src.main investments add "Mi Inversión" stock 1000.00 --shares 10 --price 100.00

# 2. Ver portafolio
uv run python -m src.main investments portfolio

# 3. Actualizar valores
uv run python -m src.main investments update-value [INVESTMENT_ID] 1100.00
```

---

## 🚨 Manejo de Errores Comunes

### Error: "ID no encontrado"
**Causa**: Usar ID incompleto o incorrecto
**Solución**: Usar el ID completo o al menos 8 caracteres iniciales
```bash
# ❌ Incorrecto
uv run python -m src.main budgets analyze 69bd

# ✅ Correcto
uv run python -m src.main budgets analyze 69bdbb3b-e9bd-4083-9b2b-33b36ba7fe83
# o al menos:
uv run python -m src.main budgets analyze 69bdbb3b
```

### Error: Base de datos no inicializada
**Causa**: Primera ejecución o base de datos corrupta
**Solución**: La base de datos se inicializa automáticamente
```bash
# Si persiste el problema, verificar permisos del directorio
uv run python -m src.main status
```

### Error: Comando no reconocido
**Causa**: Sintaxis incorrecta o comando inexistente
**Solución**: Usar --help para ver comandos disponibles
```bash
# Ver comandos principales
uv run python -m src.main --help

# Ver subcomandos específicos
uv run python -m src.main transactions --help
```

---

## 📈 Tips y Mejores Prácticas

### 1. Organización de Categorías
- Usa categorías consistentes: `comida`, `transporte`, `entretenimiento`
- Evita crear demasiadas categorías específicas
- Agrupa gastos similares bajo la misma categoría

### 2. Gestión de Presupuestos
- Crea presupuestos realistas basados en historial
- Revisa y ajusta mensualmente
- Usa categorías principales para mejor control

### 3. Seguimiento de Inversiones
- Actualiza valores regularmente
- Diversifica tipos de inversión
- Mantén descripciones detalladas

### 4. Reportes y Análisis
- Genera reportes mensualmente
- Compara períodos para identificar tendencias
- Exporta datos para análisis externos

### 5. Automatización
- Configura autocompletado para mayor eficiencia
- Usa alias para comandos frecuentes
- Considera crear scripts para tareas repetitivas

---

## 🔗 Referencias Rápidas

### Comandos Más Usados
```bash
# Agregar gasto rápido
uv run python -m src.main transactions add 25.50 "Descripción" --category comida

# Ver resumen
uv run python -m src.main summary

# Listar transacciones
uv run python -m src.main transactions list

# Reporte mensual
uv run python -m src.main reports monthly

# Estado del sistema
uv run python -m src.main status
```

### Estructura de IDs
- Los IDs son UUID de 36 caracteres
- Puedes usar versiones cortas (8+ caracteres)
- Ejemplo: `69bdbb3b-e9bd-4083-9b2b-33b36ba7fe83` → `69bdbb3b`

### Formatos de Fecha
- Formato estándar: `YYYY-MM-DD`
- Ejemplo: `2025-06-24`
- Si no se especifica, usa fecha actual

---

Esta guía cubre todos los comandos disponibles en Sales Command. Para más información específica sobre cualquier comando, usa la opción `--help` con el comando correspondiente.

**¡Feliz gestión financiera! 💰**
