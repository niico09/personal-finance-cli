"""Comandos CLI para gestión de transacciones."""

from __future__ import annotations

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.services.transaction_service import TransactionService
from src.database.models import TransactionType
from src.utils.logging import get_logger

# Crear subcomando para transacciones
transactions_app = typer.Typer(
    name="transactions",
    help="💳 Gestión de transacciones (ingresos y gastos)",
    no_args_is_help=True
)

console = Console()
logger = get_logger(__name__)


@transactions_app.command("add")
def add_transaction(
    amount: float = typer.Argument(..., help="Monto de la transacción"),
    description: str = typer.Argument(..., help="Descripción de la transacción"),
    category: str = typer.Option("general", "-c", "--category", help="Categoría"),
    trans_type: str = typer.Option("expense", "-t", "--type", help="Tipo: income/expense"),
    account: str = typer.Option("default", "-a", "--account", help="Cuenta"),
    payment_method: str = typer.Option("cash", "-p", "--payment", help="Método de pago"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Etiquetas separadas por comas"),
    notes: Optional[str] = typer.Option(None, "-n", "--notes", help="Notas adicionales")
) -> None:
    """➕ Agregar nueva transacción."""
    try:
        service = TransactionService()

        # Validar tipo de transacción
        if trans_type.lower() not in ["income", "expense"]:
            console.print("[red]❌ Tipo de transacción debe ser 'income' o 'expense'[/red]")
            raise typer.Exit(1)

        transaction_type = TransactionType.INCOME if trans_type.lower() == "income" else TransactionType.EXPENSE

        # Procesar etiquetas
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else None

        # Crear transacción
        transaction = service.create_transaction(
            amount=Decimal(str(amount)),
            description=description,
            transaction_type=transaction_type,
            category_name=category,
            account_name=account,
            payment_method=payment_method,
            tags=tag_list,
            notes=notes
        )

        # Mostrar confirmación
        panel_content = f"""
[green]✅ Transacción agregada exitosamente[/green]

[bold]ID:[/bold] {transaction.id[:8]}...
[bold]💰 Monto:[/bold] ${transaction.amount:,.2f}
[bold]📝 Descripción:[/bold] {transaction.description}
[bold]🏷️ Categoría:[/bold] {transaction.category.name}
[bold]📊 Tipo:[/bold] {transaction.transaction_type.value}
[bold]💳 Método:[/bold] {transaction.payment_method}
[bold]📅 Fecha:[/bold] {transaction.transaction_date.strftime('%Y-%m-%d %H:%M')}
"""

        if transaction.parsed_tags:
            panel_content += f"[bold]🏷️ Tags:[/bold] {', '.join(transaction.parsed_tags)}\n"

        if transaction.notes:
            panel_content += f"[bold]📋 Notas:[/bold] {transaction.notes}\n"

        console.print(Panel(panel_content, title="💳 Nueva Transacción", border_style="green"))

    except ValueError as e:
        console.print(f"[red]❌ Error de validación: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error al agregar transacción: {e}[/red]")
        logger.error(f"Error en add_transaction: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@transactions_app.command("list")
def list_transactions(
    limit: int = typer.Option(20, "-l", "--limit", help="Número de transacciones a mostrar"),
    trans_type: Optional[str] = typer.Option(None, "-t", "--type", help="Filtrar por tipo (income/expense)"),
    category: Optional[str] = typer.Option(None, "-c", "--category", help="Filtrar por categoría"),
    account: Optional[str] = typer.Option(None, "-a", "--account", help="Filtrar por cuenta"),
    search: Optional[str] = typer.Option(None, "-s", "--search", help="Buscar en descripción")
) -> None:
    """📋 Listar transacciones recientes."""
    try:
        service = TransactionService()

        # Preparar filtros
        transaction_type = None
        if trans_type:
            if trans_type.lower() == "income":
                transaction_type = TransactionType.INCOME
            elif trans_type.lower() == "expense":
                transaction_type = TransactionType.EXPENSE
            else:
                console.print("[red]❌ Tipo debe ser 'income' or 'expense'[/red]")
                raise typer.Exit(1)

        # Obtener transacciones
        transactions = service.get_transactions(
            limit=limit,
            transaction_type=transaction_type,
            category_name=category,
            account_name=account,
            search_text=search
        )

        if not transactions:
            console.print("[yellow]ℹ️ No se encontraron transacciones[/yellow]")
            return

        # Crear tabla
        table = Table(title=f"📋 Últimas {len(transactions)} Transacciones")
        table.add_column("ID", style="dim")
        table.add_column("Fecha", style="cyan")
        table.add_column("Descripción", style="white")
        table.add_column("Categoría", style="blue")
        table.add_column("Tipo", justify="center")
        table.add_column("Monto", justify="right", style="bold")

        for transaction in transactions:
            # Formatear tipo con colores
            if transaction.transaction_type == TransactionType.INCOME:
                type_str = "[green]📈 Ingreso[/green]"
                amount_str = f"[green]+${transaction.amount:,.2f}[/green]"
            else:
                type_str = "[red]📉 Gasto[/red]"
                amount_str = f"[red]-${transaction.amount:,.2f}[/red]"

            table.add_row(
                transaction.id[:8] + "...",
                transaction.transaction_date.strftime("%Y-%m-%d"),
                transaction.description[:30] + ("..." if len(transaction.description) > 30 else ""),
                transaction.category.name if transaction.category else "Sin categoría",
                type_str,
                amount_str
            )

        console.print(table)

        # Mostrar resumen rápido
        income_total = sum(
            t.amount for t in transactions
            if t.transaction_type == TransactionType.INCOME
        )
        expense_total = sum(
            t.amount for t in transactions
            if t.transaction_type == TransactionType.EXPENSE
        )

        console.print()
        console.print(f"💰 [green]Total Ingresos:[/green] ${income_total:,.2f}")
        console.print(f"💸 [red]Total Gastos:[/red] ${expense_total:,.2f}")
        console.print(f"📊 [blue]Balance:[/blue] ${income_total - expense_total:,.2f}")

    except Exception as e:
        console.print(f"[red]❌ Error al listar transacciones: {e}[/red]")
        logger.error(f"Error en list_transactions: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@transactions_app.command("summary")
def transaction_summary(
    days: int = typer.Option(30, "-d", "--days", help="Días hacia atrás para el resumen"),
    account: Optional[str] = typer.Option(None, "-a", "--account", help="Filtrar por cuenta")
) -> None:
    """📊 Mostrar resumen de transacciones."""
    try:
        service = TransactionService()

        # Calcular fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Obtener resumen
        summary = service.get_summary(
            start_date=start_date,
            end_date=end_date,
            account_name=account
        )

        # Mostrar resumen principal
        panel_content = f"""
[bold blue]📊 Resumen de Transacciones[/bold blue]
[dim]Período: {start_date} a {end_date} ({days} días)[/dim]

💰 [green]Ingresos:[/green] ${summary['income_total']:,.2f}
💸 [red]Gastos:[/red] ${summary['expense_total']:,.2f}
📈 [blue]Balance:[/blue] ${summary['balance']:,.2f}
📋 [white]Total Transacciones:[/white] {summary['total_transactions']}
"""

        if account:
            panel_content += f"🏦 [dim]Cuenta: {account}[/dim]\n"

        console.print(Panel(panel_content, border_style="blue"))

        # Mostrar top categorías si hay datos
        if summary['top_categories']:
            console.print("\n[bold]🏷️ Top Categorías de Gastos:[/bold]")
            for i, category in enumerate(summary['top_categories'], 1):
                console.print(f"  {i}. {category['name']}: ${category['amount']:,.2f}")

    except Exception as e:
        console.print(f"[red]❌ Error al generar resumen: {e}[/red]")
        logger.error(f"Error en transaction_summary: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@transactions_app.command("delete")
def delete_transaction(
    transaction_id: str = typer.Argument(..., help="ID de la transacción a eliminar"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirmar eliminación sin preguntar")
) -> None:
    """🗑️ Eliminar transacción."""
    try:
        service = TransactionService()

        # Buscar transacción
        transaction = service.get_transaction_by_id(transaction_id)
        if not transaction:
            console.print(f"[red]❌ Transacción no encontrada: {transaction_id}[/red]")
            raise typer.Exit(1)

        # Mostrar detalles de la transacción
        console.print(f"\n[bold]Transacción a eliminar:[/bold]")
        console.print(f"ID: {transaction.id}")
        console.print(f"Fecha: {transaction.transaction_date.strftime('%Y-%m-%d %H:%M')}")
        console.print(f"Descripción: {transaction.description}")
        console.print(f"Monto: ${transaction.amount:,.2f}")
        console.print(f"Tipo: {transaction.transaction_type.value}")

        # Confirmar eliminación
        if not confirm:
            confirm = typer.confirm("\n¿Está seguro que desea eliminar esta transacción?")

        if confirm:
            if service.delete_transaction(transaction_id):
                console.print("[green]✅ Transacción eliminada exitosamente[/green]")
            else:
                console.print("[red]❌ Error al eliminar la transacción[/red]")
                raise typer.Exit(1)
        else:
            console.print("[yellow]ℹ️ Eliminación cancelada[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Error al eliminar transacción: {e}[/red]")
        logger.error(f"Error en delete_transaction: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


if __name__ == "__main__":
    transactions_app()
