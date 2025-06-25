"""CLI principal de Sales Command - Versión completa."""

from __future__ import annotations

import typer
from rich.console import Console

from src.utils.logging import get_logger
from src.cli.commands import transactions_app, budgets_app, investments_app, reports_app

# Configurar aplicación principal
app = typer.Typer(
    name="sales",
    help="💰 Sales Command - Gestión financiera personal completa",
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Agregar subcomandos
app.add_typer(transactions_app, name="transactions", help="💳 Gestión de transacciones")
app.add_typer(budgets_app, name="budgets", help="💰 Gestión de presupuestos")
app.add_typer(investments_app, name="investments", help="📈 Gestión de inversiones")
app.add_typer(reports_app, name="reports", help="📊 Generación de reportes")

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
        from src.services.transaction_service import TransactionService
        from datetime import date, timedelta

        console.print(f"\n[bold blue]📋 Resumen Financiero - {period.title()}[/bold blue]")
        console.print("=" * 50)

        # Calcular fechas según el período
        end_date = date.today()
        if period == "today":
            start_date = end_date
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default a mes

        # Obtener datos reales
        service = TransactionService()
        summary_data = service.get_summary(start_date=start_date, end_date=end_date)

        # Mostrar resumen
        console.print(f"💰 [green]Ingresos:[/green] ${summary_data['income_total']:,.2f}")
        console.print(f"💸 [red]Gastos:[/red] ${summary_data['expense_total']:,.2f}")
        console.print(f"📊 [blue]Balance:[/blue] ${summary_data['balance']:,.2f}")

        console.print(f"\n[bold]📋 Transacciones:[/bold] {summary_data['total_transactions']}")

        if summary_data['top_categories']:
            console.print("\n[bold]🏷️ Top Categorías:[/bold]")
            for i, category in enumerate(summary_data['top_categories'][:3], 1):
                console.print(f"  {i}. {category['name']}: ${category['amount']:,.2f}")

        console.print()
        service.close()

    except Exception as e:
        console.print(f"[red]Error al generar resumen: {e}[/red]")
        logger.error(f"Error en comando summary: {e}")
        raise typer.Exit(1)


@app.command()
def quick_add(
    amount: float = typer.Argument(..., help="Monto de la transacción"),
    description: str = typer.Argument(..., help="Descripción"),
    category: str = typer.Option("general", "-c", "--category", help="Categoría"),
    transaction_type: str = typer.Option("expense", "-t", "--type", help="Tipo (income/expense)")
) -> None:
    """➕ Agregar transacción rápida."""
    try:
        from src.services.transaction_service import TransactionService
        from src.database.models import TransactionType
        from decimal import Decimal

        # Validar tipo
        if transaction_type.lower() not in ["income", "expense"]:
            console.print("[red]❌ Tipo debe ser 'income' o 'expense'[/red]")
            raise typer.Exit(1)

        trans_type = TransactionType.INCOME if transaction_type.lower() == "income" else TransactionType.EXPENSE

        # Crear transacción
        service = TransactionService()
        transaction = service.create_transaction(
            amount=Decimal(str(amount)),
            description=description,
            transaction_type=trans_type,
            category_name=category
        )

        console.print(f"\n[green]✅ Transacción agregada exitosamente:[/green]")
        console.print(f"💰 Monto: ${transaction.amount:,.2f}")
        console.print(f"📝 Descripción: {transaction.description}")
        console.print(f"🏷️ Categoría: {transaction.category.name}")
        console.print(f"📊 Tipo: {transaction.transaction_type.value}")
        console.print()

        service.close()
        logger.info(f"Transacción agregada: {amount} - {description}")

    except Exception as e:
        console.print(f"[red]Error al agregar transacción: {e}[/red]")
        logger.error(f"Error en comando quick_add: {e}")
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
