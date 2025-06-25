"""CLI principal de Sales Command - Versión básica."""

from __future__ import annotations

import typer
from rich.console import Console

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


@app.command()
def summary(
    period: str = typer.Option(
        "today",
        "--period", "-p",
        help="Período para el resumen (today, week, month, year)"
    )
) -> None:
    """📋 Mostrar resumen financiero rápido."""
    try:
        console.print(f"\n[bold blue]📋 Resumen Financiero - {period.title()}[/bold blue]")
        console.print("=" * 50)

        # Datos de ejemplo por ahora
        console.print("💰 [green]Ingresos:[/green] $3,500.00")
        console.print("💸 [red]Gastos:[/red] $1,250.75")
        console.print("📊 [blue]Balance:[/blue] $2,249.25")

        console.print("\n[bold]🏷️ Top Categorías:[/bold]")
        console.print("  • Alimentación: $450.00")
        console.print("  • Transporte: $200.50")
        console.print("  • Entretenimiento: $125.75")

        console.print()

    except Exception as e:
        console.print(f"[red]Error al generar resumen: {e}[/red]")
        logger.error(f"Error en comando summary: {e}")
        raise typer.Exit(1)


@app.command()
def add(
    amount: float = typer.Option(..., "--amount", "-a", help="Monto de la transacción"),
    description: str = typer.Option(..., "--description", "-d", help="Descripción"),
    category: str = typer.Option("general", "--category", "-c", help="Categoría"),
    transaction_type: str = typer.Option("expense", "--type", "-t", help="Tipo (income/expense)")
) -> None:
    """➕ Agregar nueva transacción."""
    try:
        # Por ahora solo mostramos lo que se agregaría
        console.print(f"\n[green]✅ Transacción agregada:[/green]")
        console.print(f"💰 Monto: ${amount:,.2f}")
        console.print(f"📝 Descripción: {description}")
        console.print(f"🏷️ Categoría: {category}")
        console.print(f"📊 Tipo: {transaction_type}")
        console.print()

        logger.info(f"Transacción agregada: {amount} - {description}")

    except Exception as e:
        console.print(f"[red]Error al agregar transacción: {e}[/red]")
        logger.error(f"Error en comando add: {e}")
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """🚦 Verificar estado del sistema."""
    from src.config.settings import get_settings

    try:
        console.print("\n[bold blue]🚦 Estado del Sistema[/bold blue]")
        console.print("=" * 30)

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
