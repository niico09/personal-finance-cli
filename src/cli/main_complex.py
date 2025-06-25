"""CLI principal de Sales Command."""

from __future__ import annotations

import typer
from rich.console import Console

from src.cli.commands.transactions import transactions_app
from src.cli.commands.budgets import budgets_app
from src.cli.commands.reports import reports_app
from src.cli.commands.investments import investments_app
from src.cli.commands.accounts import accounts_app
from src.cli.commands.categories import categories_app
from src.utils.logging import get_logger

# Configurar aplicación principal
app = typer.Typer(
    name="sales",
    help="💰 Sales Command - Gestión financiera personal completa",
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

console = Console()
logger = get_logger(__name__)

# Registrar subcomandos
app.add_typer(transactions_app, name="add", help="➕ Agregar transacciones")
app.add_typer(budgets_app, name="budget", help="💳 Gestionar presupuestos")
app.add_typer(reports_app, name="report", help="📊 Generar reportes")
app.add_typer(investments_app, name="investments", help="📈 Gestionar inversiones")
app.add_typer(accounts_app, name="accounts", help="🏦 Gestionar cuentas")
app.add_typer(categories_app, name="categories", help="🏷️ Gestionar categorías")


@app.command()
def summary(
    period: str = typer.Option(
        "today",
        "--period", "-p",
        help="Período para el resumen (today, week, month, year)"
    )
) -> None:
    """📋 Mostrar resumen financiero rápido."""
    from src.services.report_service import ReportService

    try:
        report_service = ReportService()
        summary_data = report_service.get_summary(period)

        console.print(f"\n[bold blue]📋 Resumen Financiero - {period.title()}[/bold blue]")
        console.print("=" * 50)

        # Mostrar datos del resumen
        console.print(f"💰 [green]Ingresos:[/green] ${summary_data.get('income', 0):,.2f}")
        console.print(f"💸 [red]Gastos:[/red] ${summary_data.get('expenses', 0):,.2f}")
        console.print(f"📊 [blue]Balance:[/blue] ${summary_data.get('balance', 0):,.2f}")

        # Categorías principales
        if summary_data.get('top_categories'):
            console.print("\n[bold]🏷️ Top Categorías:[/bold]")
            for category, amount in summary_data['top_categories']:
                console.print(f"  • {category}: ${amount:,.2f}")

        console.print()

    except Exception as e:
        console.print(f"[red]Error al generar resumen: {e}[/red]")
        logger.error(f"Error en comando summary: {e}")
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """🚦 Verificar estado del sistema."""
    from src.database.connection import get_engine
    from src.config.settings import get_settings

    try:
        console.print("\n[bold blue]🚦 Estado del Sistema[/bold blue]")
        console.print("=" * 30)

        # Verificar base de datos
        engine = get_engine()
        with engine.connect() as conn:
            console.print("[green]✅ Base de datos:[/green] Conectada")

        # Verificar configuración
        settings = get_settings()
        console.print(f"[blue]⚙️ Configuración:[/blue] {settings.app_name} v{settings.app_version}")
        console.print(f"[blue]💾 Base de datos:[/blue] {settings.database_url}")
        console.print(f"[blue]📁 Directorio de datos:[/blue] {settings.data_dir}")

        console.print("\n[green]🎉 Sistema funcionando correctamente[/green]\n")

    except Exception as e:
        console.print(f"[red]❌ Error en el sistema: {e}[/red]")
        logger.error(f"Error en comando status: {e}")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """📦 Mostrar información de versión."""
    from src import __version__, __author__

    console.print(f"\n[bold blue]📦 Sales Command[/bold blue]")
    console.print(f"[blue]Versión:[/blue] {__version__}")
    console.print(f"[blue]Autor:[/blue] {__author__}")
    console.print(f"[blue]Descripción:[/blue] Sistema completo de gestión financiera personal")
    console.print()


@app.callback()
def main(
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Habilitar salida detallada"
    ),
    debug: bool = typer.Option(
        False,
        "--debug", "-d",
        help="Habilitar modo debug"
    )
) -> None:
    """
    💰 Sales Command - Sistema completo de gestión financiera personal.

    Herramienta de línea de comandos para gestionar tus finanzas personales
    incluyendo transacciones, presupuestos, inversiones y reportes detallados.
    """
    if verbose:
        import logging
        logging.getLogger("sales_command").setLevel(logging.INFO)

    if debug:
        import logging
        logging.getLogger("sales_command").setLevel(logging.DEBUG)
        console.print("[yellow]Modo debug habilitado[/yellow]")


if __name__ == "__main__":
    app()
