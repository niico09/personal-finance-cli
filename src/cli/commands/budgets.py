"""Comandos CLI para gestión de presupuestos."""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn

from src.services.budget_service import BudgetService
from src.utils.logging import get_logger

# Crear subcomando para presupuestos
budgets_app = typer.Typer(
    name="budgets",
    help="💰 Gestión de presupuestos y planificación financiera",
    no_args_is_help=True
)

console = Console()
logger = get_logger(__name__)


@budgets_app.command("create")
def create_budget(
    name: str = typer.Argument(..., help="Nombre del presupuesto"),
    period_type: str = typer.Option("monthly", "-p", "--period", help="Tipo de período (monthly/yearly)"),
    year: int = typer.Option(None, "-y", "--year", help="Año del presupuesto"),
    month: Optional[int] = typer.Option(None, "-m", "--month", help="Mes del presupuesto (1-12)"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="Descripción del presupuesto")
) -> None:
    """📝 Crear nuevo presupuesto."""
    try:
        service = BudgetService()

        # Validar tipo de período
        if period_type not in ["monthly", "yearly"]:
            console.print("[red]❌ Tipo de período debe ser 'monthly' o 'yearly'[/red]")
            raise typer.Exit(1)

        # Usar año actual si no se especifica
        if year is None:
            year = datetime.now().year

        # Validar mes para presupuestos mensuales
        if period_type == "monthly":
            if month is None:
                month = datetime.now().month
            elif month < 1 or month > 12:
                console.print("[red]❌ El mes debe estar entre 1 y 12[/red]")
                raise typer.Exit(1)
        else:
            month = None  # Para presupuestos anuales

        # Crear presupuesto
        budget = service.create_budget(
            name=name,
            period_type=period_type,
            year=year,
            month=month,
            description=description
        )

        # Mostrar confirmación
        period_str = f"{year}"
        if month:
            period_str = f"{year}-{month:02d}"

        panel_content = f"""
[green]✅ Presupuesto creado exitosamente[/green]

[bold]ID:[/bold] {budget.id[:8]}...
[bold]📝 Nombre:[/bold] {budget.name}
[bold]📅 Período:[/bold] {period_str} ({period_type})
[bold]📋 Descripción:[/bold] {budget.description or 'Sin descripción'}
[bold]🎯 Estado:[/bold] Activo
"""

        console.print(Panel(panel_content, title="💰 Nuevo Presupuesto", border_style="green"))
        console.print("\n[yellow]💡 Tip: Use 'budgets add-category' para agregar categorías al presupuesto[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Error al crear presupuesto: {e}[/red]")
        logger.error(f"Error en create_budget: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@budgets_app.command("add-category")
def add_budget_category(
    budget_id: str = typer.Argument(..., help="ID del presupuesto"),
    category: str = typer.Argument(..., help="Nombre de la categoría"),
    amount: float = typer.Argument(..., help="Monto asignado"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="Descripción de la categoría")
) -> None:
    """➕ Agregar categoría a presupuesto."""
    try:
        service = BudgetService()

        # Verificar que el presupuesto existe
        budget = service.get_budget_by_id(budget_id)
        if not budget:
            console.print(f"[red]❌ Presupuesto no encontrado: {budget_id}[/red]")
            raise typer.Exit(1)

        # Agregar categoría
        budget_category = service.add_budget_category(
            budget_id=budget_id,
            category_name=category,
            allocated_amount=Decimal(str(amount)),
            description=description
        )

        # Mostrar confirmación
        console.print(f"[green]✅ Categoría agregada al presupuesto '{budget.name}'[/green]")
        console.print(f"🏷️ Categoría: {category}")
        console.print(f"💰 Monto asignado: ${amount:,.2f}")
        if description:
            console.print(f"📋 Descripción: {description}")

    except ValueError as e:
        console.print(f"[red]❌ Error de validación: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error al agregar categoría: {e}[/red]")
        logger.error(f"Error en add_budget_category: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@budgets_app.command("list")
def list_budgets(
    all_budgets: bool = typer.Option(False, "--all", "-a", help="Mostrar todos los presupuestos (incluidos inactivos)")
) -> None:
    """📋 Listar presupuestos."""
    try:
        service = BudgetService()

        budgets = service.get_budgets(active_only=not all_budgets)

        if not budgets:
            console.print("[yellow]ℹ️ No se encontraron presupuestos[/yellow]")
            return

        # Crear tabla
        table = Table(title=f"💰 Presupuestos {'(Todos)' if all_budgets else '(Activos)'}")
        table.add_column("ID", style="dim")
        table.add_column("Nombre", style="white")
        table.add_column("Período", style="cyan")
        table.add_column("Tipo", justify="center")
        table.add_column("Estado", justify="center")
        table.add_column("Creado", style="dim")

        for budget in budgets:
            # Formatear período
            if budget.period_type == "monthly" and budget.month:
                period_str = f"{budget.year}-{budget.month:02d}"
            else:
                period_str = str(budget.year)

            # Estado con colores
            status_str = "[green]✅ Activo[/green]" if budget.is_active else "[red]❌ Inactivo[/red]"

            table.add_row(
                budget.id[:8] + "...",
                budget.name,
                period_str,
                budget.period_type.title(),
                status_str,
                budget.created_at.strftime("%Y-%m-%d")
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Error al listar presupuestos: {e}[/red]")
        logger.error(f"Error en list_budgets: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@budgets_app.command("analyze")
def analyze_budget(
    budget_id: str = typer.Argument(..., help="ID del presupuesto a analizar")
) -> None:
    """📊 Analizar progreso del presupuesto."""
    try:
        service = BudgetService()

        # Obtener análisis
        analysis = service.get_budget_analysis(budget_id)

        # Mostrar información del presupuesto
        budget_info = analysis['budget']
        period_info = analysis['period']
        totals = analysis['totals']

        # Panel principal con resumen
        period_str = f"{budget_info['year']}"
        if budget_info['month']:
            period_str = f"{budget_info['year']}-{budget_info['month']:02d}"

        panel_content = f"""
[bold blue]📊 Análisis de Presupuesto[/bold blue]
[bold]Nombre:[/bold] {budget_info['name']}
[bold]Período:[/bold] {period_str} ({budget_info['period_type']})
[bold]Fechas:[/bold] {period_info['start_date']} a {period_info['end_date']}

💰 [blue]Presupuesto Total:[/blue] ${totals['allocated_amount']:,.2f}
💸 [red]Gastado:[/red] ${totals['spent_amount']:,.2f}
💵 [green]Restante:[/green] ${totals['remaining_amount']:,.2f}
📊 [yellow]Progreso:[/yellow] {totals['percentage_used']:.1f}% usado
"""

        # Añadir alerta si se excedió el presupuesto
        if analysis['is_over_budget']:
            panel_content += "\n[bold red]⚠️ PRESUPUESTO EXCEDIDO[/bold red]"

        console.print(Panel(panel_content, border_style="blue"))

        # Mostrar progreso general con barra
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task(
                "Progreso General",
                total=100,
                completed=min(totals['percentage_used'], 100)
            )

        # Tabla de categorías
        if analysis['categories']:
            console.print("\n[bold]🏷️ Análisis por Categorías:[/bold]")

            categories_table = Table()
            categories_table.add_column("Categoría", style="white")
            categories_table.add_column("Presupuesto", justify="right", style="blue")
            categories_table.add_column("Gastado", justify="right", style="red")
            categories_table.add_column("Restante", justify="right", style="green")
            categories_table.add_column("Progreso", justify="center")
            categories_table.add_column("Estado", justify="center")

            for category in analysis['categories']:
                # Formatear progreso
                progress_pct = category['percentage_used']
                if progress_pct >= 100:
                    progress_str = f"[red]{progress_pct:.1f}%[/red]"
                elif progress_pct >= 80:
                    progress_str = f"[yellow]{progress_pct:.1f}%[/yellow]"
                else:
                    progress_str = f"[green]{progress_pct:.1f}%[/green]"

                # Estado
                if category['is_over_budget']:
                    status_str = "[red]⚠️ Excedido[/red]"
                elif progress_pct >= 90:
                    status_str = "[yellow]⚡ Cerca[/yellow]"
                else:
                    status_str = "[green]✅ OK[/green]"

                categories_table.add_row(
                    category['category_name'],
                    f"${category['allocated_amount']:,.2f}",
                    f"${category['spent_amount']:,.2f}",
                    f"${category['remaining_amount']:,.2f}",
                    progress_str,
                    status_str
                )

            console.print(categories_table)
        else:
            console.print("\n[yellow]ℹ️ No hay categorías definidas para este presupuesto[/yellow]")
            console.print("[dim]Use 'budgets add-category' para agregar categorías[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error al analizar presupuesto: {e}[/red]")
        logger.error(f"Error en analyze_budget: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@budgets_app.command("current")
def show_current_budget(
    year: Optional[int] = typer.Option(None, "-y", "--year", help="Año (por defecto: actual)"),
    month: Optional[int] = typer.Option(None, "-m", "--month", help="Mes (por defecto: actual)")
) -> None:
    """📅 Mostrar presupuesto actual."""
    try:
        service = BudgetService()

        # Usar fecha actual si no se especifica
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month

        # Buscar presupuesto mensual primero
        budget = service.get_current_budget(year, month)

        # Si no hay mensual, buscar anual
        if not budget:
            budget = service.get_current_budget(year, None)

        if not budget:
            console.print(f"[yellow]ℹ️ No se encontró presupuesto para {year}-{month:02d}[/yellow]")
            console.print("[dim]Use 'budgets create' para crear un presupuesto[/dim]")
            return

        # Mostrar análisis del presupuesto actual
        console.print(f"[bold blue]📅 Presupuesto Actual ({year}-{month:02d})[/bold blue]")

        # Redirigir al comando analyze
        analyze_budget(budget.id)

    except Exception as e:
        console.print(f"[red]❌ Error al obtener presupuesto actual: {e}[/red]")
        logger.error(f"Error en show_current_budget: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@budgets_app.command("delete")
def delete_budget(
    budget_id: str = typer.Argument(..., help="ID del presupuesto a eliminar"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirmar eliminación sin preguntar")
) -> None:
    """🗑️ Eliminar presupuesto."""
    try:
        service = BudgetService()

        # Buscar presupuesto
        budget = service.get_budget_by_id(budget_id)
        if not budget:
            console.print(f"[red]❌ Presupuesto no encontrado: {budget_id}[/red]")
            raise typer.Exit(1)

        # Mostrar detalles del presupuesto
        period_str = f"{budget.year}"
        if budget.month:
            period_str = f"{budget.year}-{budget.month:02d}"

        console.print(f"\n[bold]Presupuesto a eliminar:[/bold]")
        console.print(f"ID: {budget.id}")
        console.print(f"Nombre: {budget.name}")
        console.print(f"Período: {period_str}")
        console.print(f"Tipo: {budget.period_type}")

        # Confirmar eliminación
        if not confirm:
            confirm = typer.confirm("\n¿Está seguro que desea eliminar este presupuesto?")

        if confirm:
            if service.delete_budget(budget_id):
                console.print("[green]✅ Presupuesto eliminado exitosamente[/green]")
            else:
                console.print("[red]❌ Error al eliminar el presupuesto[/red]")
                raise typer.Exit(1)
        else:
            console.print("[yellow]ℹ️ Eliminación cancelada[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Error al eliminar presupuesto: {e}[/red]")
        logger.error(f"Error en delete_budget: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


if __name__ == "__main__":
    budgets_app()
