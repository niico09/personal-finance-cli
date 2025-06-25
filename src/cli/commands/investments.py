"""Comandos CLI para gestión de inversiones."""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.services.investment_service import InvestmentService
from src.database.models import InvestmentType
from src.utils.logging import get_logger

# Crear subcomando para inversiones
investments_app = typer.Typer(
    name="investments",
    help="📈 Gestión de inversiones y portafolio",
    no_args_is_help=True
)

console = Console()
logger = get_logger(__name__)


@investments_app.command("add")
def add_investment(
    name: str = typer.Argument(..., help="Nombre de la inversión"),
    investment_type: str = typer.Argument(..., help="Tipo de inversión"),
    amount: float = typer.Argument(..., help="Monto inicial invertido"),
    shares: Optional[float] = typer.Option(None, "-s", "--shares", help="Número de acciones/unidades"),
    price: Optional[float] = typer.Option(None, "-p", "--price", help="Precio de compra por unidad"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="Descripción de la inversión"),
    date_str: Optional[str] = typer.Option(None, "--date", help="Fecha de compra (YYYY-MM-DD)")
) -> None:
    """➕ Agregar nueva inversión."""
    try:
        service = InvestmentService()

        # Validar tipo de inversión
        valid_types = [t.value for t in InvestmentType]
        if investment_type.lower() not in valid_types:
            console.print(f"[red]❌ Tipo de inversión inválido. Opciones: {', '.join(valid_types)}[/red]")
            raise typer.Exit(1)

        inv_type = InvestmentType(investment_type.lower())

        # Procesar fecha si se proporciona
        purchase_date = None
        if date_str:
            try:
                purchase_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                console.print("[red]❌ Formato de fecha inválido. Use YYYY-MM-DD[/red]")
                raise typer.Exit(1)

        # Crear inversión
        investment = service.create_investment(
            name=name,
            investment_type=inv_type,
            initial_amount=Decimal(str(amount)),
            shares=Decimal(str(shares)) if shares else None,
            purchase_price=Decimal(str(price)) if price else None,
            description=description,
            purchase_date=purchase_date
        )

        # Mostrar confirmación
        panel_content = f"""
[green]✅ Inversión agregada exitosamente[/green]

[bold]ID:[/bold] {investment.id[:8]}...
[bold]📝 Nombre:[/bold] {investment.name}
[bold]📊 Tipo:[/bold] {investment.investment_type.value.title()}
[bold]💰 Monto Inicial:[/bold] ${investment.initial_amount:,.2f}
[bold]💵 Valor Actual:[/bold] ${investment.current_value:,.2f}
[bold]📅 Fecha de Compra:[/bold] {investment.purchase_date.strftime('%Y-%m-%d')}
"""

        if investment.shares:
            panel_content += f"[bold]📦 Acciones/Unidades:[/bold] {investment.shares:,.2f}\n"

        if investment.purchase_price:
            panel_content += f"[bold]💲 Precio de Compra:[/bold] ${investment.purchase_price:,.2f}\n"

        if investment.description:
            panel_content += f"[bold]📋 Descripción:[/bold] {investment.description}\n"

        console.print(Panel(panel_content, title="📈 Nueva Inversión", border_style="green"))

    except ValueError as e:
        console.print(f"[red]❌ Error de validación: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error al agregar inversión: {e}[/red]")
        logger.error(f"Error en add_investment: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@investments_app.command("list")
def list_investments(
    investment_type: Optional[str] = typer.Option(None, "-t", "--type", help="Filtrar por tipo de inversión"),
    all_investments: bool = typer.Option(False, "--all", "-a", help="Mostrar todas las inversiones (incluidas inactivas)")
) -> None:
    """📋 Listar inversiones."""
    try:
        service = InvestmentService()

        # Validar tipo si se proporciona
        inv_type = None
        if investment_type:
            valid_types = [t.value for t in InvestmentType]
            if investment_type.lower() not in valid_types:
                console.print(f"[red]❌ Tipo de inversión inválido. Opciones: {', '.join(valid_types)}[/red]")
                raise typer.Exit(1)
            inv_type = InvestmentType(investment_type.lower())

        # Obtener inversiones
        investments = service.get_investments(
            active_only=not all_investments,
            investment_type=inv_type
        )

        if not investments:
            console.print("[yellow]ℹ️ No se encontraron inversiones[/yellow]")
            return

        # Crear tabla
        title = "📈 Inversiones"
        if investment_type:
            title += f" - Tipo: {investment_type.title()}"
        if all_investments:
            title += " (Todas)"

        table = Table(title=title)
        table.add_column("ID", style="dim")
        table.add_column("Nombre", style="white")
        table.add_column("Tipo", style="blue")
        table.add_column("Inversión", justify="right", style="cyan")
        table.add_column("Valor Actual", justify="right", style="yellow")
        table.add_column("Rendimiento", justify="right")
        table.add_column("Estado", justify="center")

        for investment in investments:
            # Calcular rendimiento
            total_return = investment.current_value - investment.initial_amount
            return_percentage = (total_return / investment.initial_amount * 100) if investment.initial_amount > 0 else 0

            # Formatear rendimiento con colores
            if return_percentage > 0:
                return_str = f"[green]+{return_percentage:.1f}%[/green]"
            elif return_percentage < 0:
                return_str = f"[red]{return_percentage:.1f}%[/red]"
            else:
                return_str = "[dim]0.0%[/dim]"

            # Estado
            status_str = "[green]✅ Activa[/green]" if investment.is_active else "[red]❌ Inactiva[/red]"

            table.add_row(
                investment.id[:8] + "...",
                investment.name[:25] + ("..." if len(investment.name) > 25 else ""),
                investment.investment_type.value.title(),
                f"${investment.initial_amount:,.2f}",
                f"${investment.current_value:,.2f}",
                return_str,
                status_str
            )

        console.print(table)

        # Mostrar resumen rápido
        total_invested = sum(inv.initial_amount for inv in investments)
        total_current = sum(inv.current_value for inv in investments)
        total_return = total_current - total_invested
        overall_return_pct = (total_return / total_invested * 100) if total_invested > 0 else 0

        console.print()
        console.print(f"💰 [cyan]Total Invertido:[/cyan] ${total_invested:,.2f}")
        console.print(f"💵 [yellow]Valor Actual:[/yellow] ${total_current:,.2f}")

        if overall_return_pct > 0:
            console.print(f"📈 [green]Rendimiento Total:[/green] +${total_return:,.2f} (+{overall_return_pct:.1f}%)")
        elif overall_return_pct < 0:
            console.print(f"📉 [red]Pérdida Total:[/red] ${total_return:,.2f} ({overall_return_pct:.1f}%)")
        else:
            console.print(f"📊 [dim]Sin cambios:[/dim] ${total_return:,.2f} (0.0%)")

    except Exception as e:
        console.print(f"[red]❌ Error al listar inversiones: {e}[/red]")
        logger.error(f"Error en list_investments: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@investments_app.command("update-value")
def update_investment_value(
    investment_id: str = typer.Argument(..., help="ID de la inversión"),
    new_value: float = typer.Argument(..., help="Nuevo valor actual"),
    date_str: Optional[str] = typer.Option(None, "--date", help="Fecha de actualización (YYYY-MM-DD)")
) -> None:
    """💰 Actualizar valor actual de inversión."""
    try:
        service = InvestmentService()

        # Procesar fecha si se proporciona
        update_date = None
        if date_str:
            try:
                update_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                console.print("[red]❌ Formato de fecha inválido. Use YYYY-MM-DD[/red]")
                raise typer.Exit(1)

        # Actualizar valor
        investment = service.update_investment_value(
            investment_id=investment_id,
            current_value=Decimal(str(new_value)),
            update_date=update_date
        )

        if not investment:
            console.print(f"[red]❌ Inversión no encontrada: {investment_id}[/red]")
            raise typer.Exit(1)

        # Calcular cambio
        total_return = investment.current_value - investment.initial_amount
        return_percentage = (total_return / investment.initial_amount * 100) if investment.initial_amount > 0 else 0

        # Mostrar confirmación
        console.print(f"[green]✅ Valor actualizado para '{investment.name}'[/green]")
        console.print(f"💰 Valor anterior: ${investment.initial_amount:,.2f}")
        console.print(f"💵 Valor actual: ${investment.current_value:,.2f}")

        if return_percentage > 0:
            console.print(f"📈 [green]Rendimiento: +${total_return:,.2f} (+{return_percentage:.1f}%)[/green]")
        elif return_percentage < 0:
            console.print(f"📉 [red]Pérdida: ${total_return:,.2f} ({return_percentage:.1f}%)[/red]")
        else:
            console.print(f"📊 [dim]Sin cambios: ${total_return:,.2f} (0.0%)[/dim]")

    except ValueError as e:
        console.print(f"[red]❌ Error de validación: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error al actualizar valor: {e}[/red]")
        logger.error(f"Error en update_investment_value: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@investments_app.command("portfolio")
def show_portfolio() -> None:
    """📊 Mostrar resumen del portafolio de inversiones."""
    try:
        service = InvestmentService()

        # Obtener resumen del portafolio
        summary = service.get_portfolio_summary()

        if summary['investments_count'] == 0:
            console.print("[yellow]ℹ️ No tienes inversiones registradas[/yellow]")
            console.print("[dim]Use 'investments add' para agregar tu primera inversión[/dim]")
            return

        # Panel principal con resumen
        overall_return_pct = summary['return_percentage']
        return_color = "green" if overall_return_pct >= 0 else "red"
        return_symbol = "+" if overall_return_pct >= 0 else ""

        panel_content = f"""
[bold blue]📊 Resumen del Portafolio[/bold blue]

💰 [cyan]Total Invertido:[/cyan] ${summary['total_invested']:,.2f}
💵 [yellow]Valor Actual:[/yellow] ${summary['current_value']:,.2f}
📈 [{return_color}]Rendimiento Total:[/{return_color}] [{return_color}]{return_symbol}${summary['total_return']:,.2f} ({return_symbol}{overall_return_pct:.1f}%)[/{return_color}]
🎯 [white]Número de Inversiones:[/white] {summary['investments_count']}
"""

        console.print(Panel(panel_content, border_style="blue"))

        # Mostrar distribución por tipo
        if summary['by_type']:
            console.print("\n[bold]🏷️ Distribución por Tipo:[/bold]")

            type_table = Table()
            type_table.add_column("Tipo", style="blue")
            type_table.add_column("Cantidad", justify="center")
            type_table.add_column("Invertido", justify="right", style="cyan")
            type_table.add_column("Valor Actual", justify="right", style="yellow")
            type_table.add_column("Rendimiento", justify="right")
            type_table.add_column("% del Portafolio", justify="right", style="dim")

            for inv_type, data in summary['by_type'].items():
                type_return = data['return']
                type_return_pct = (type_return / data['invested'] * 100) if data['invested'] > 0 else 0
                portfolio_pct = (data['current_value'] / summary['current_value'] * 100) if summary['current_value'] > 0 else 0

                # Formatear rendimiento
                if type_return_pct > 0:
                    return_str = f"[green]+{type_return_pct:.1f}%[/green]"
                elif type_return_pct < 0:
                    return_str = f"[red]{type_return_pct:.1f}%[/red]"
                else:
                    return_str = "[dim]0.0%[/dim]"

                type_table.add_row(
                    inv_type.title(),
                    str(data['count']),
                    f"${data['invested']:,.2f}",
                    f"${data['current_value']:,.2f}",
                    return_str,
                    f"{portfolio_pct:.1f}%"
                )

            console.print(type_table)

        # Mostrar mejores y peores inversiones
        if summary['top_performers']:
            console.print("\n[bold]🏆 Mejores Inversiones:[/bold]")
            for i, inv in enumerate(summary['top_performers'], 1):
                return_pct = inv['return_percentage']
                color = "green" if return_pct >= 0 else "red"
                symbol = "+" if return_pct >= 0 else ""

                console.print(f"  {i}. {inv['name']} - [{color}]{symbol}{return_pct:.1f}%[/{color}] (${inv['current_value']:,.2f})")

        if summary['worst_performers'] and len(summary['worst_performers']) > 0:
            console.print("\n[bold]📉 Inversiones con Menor Rendimiento:[/bold]")
            for i, inv in enumerate(summary['worst_performers'], 1):
                return_pct = inv['return_percentage']
                color = "green" if return_pct >= 0 else "red"
                symbol = "+" if return_pct >= 0 else ""

                console.print(f"  {i}. {inv['name']} - [{color}]{symbol}{return_pct:.1f}%[/{color}] (${inv['current_value']:,.2f})")

    except Exception as e:
        console.print(f"[red]❌ Error al mostrar portafolio: {e}[/red]")
        logger.error(f"Error en show_portfolio: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@investments_app.command("performance")
def show_investment_performance(
    investment_id: str = typer.Argument(..., help="ID de la inversión")
) -> None:
    """📊 Mostrar rendimiento detallado de una inversión."""
    try:
        service = InvestmentService()

        # Obtener análisis de rendimiento
        performance = service.get_investment_performance(investment_id)

        investment_info = performance['investment']
        values = performance['values']
        perf_data = performance['performance']

        # Panel con información detallada
        return_amount = perf_data['total_return']
        return_pct = perf_data['return_percentage']
        annualized_return = perf_data['annualized_return']

        return_color = "green" if return_amount >= 0 else "red"
        return_symbol = "+" if return_amount >= 0 else ""

        panel_content = f"""
[bold blue]📊 Análisis de Rendimiento[/bold blue]

[bold]📝 Inversión:[/bold] {investment_info['name']}
[bold]📊 Tipo:[/bold] {investment_info['type'].title()}
[bold]📅 Fecha de Compra:[/bold] {investment_info['purchase_date']}
[bold]⏱️ Días de Tenencia:[/bold] {perf_data['holding_days']} días

[bold]💰 Valores:[/bold]
• Inversión Inicial: ${values['initial_amount']:,.2f}
• Valor Actual: ${values['current_value']:,.2f}
• Rendimiento Total: [{return_color}]{return_symbol}${return_amount:,.2f}[/{return_color}]

[bold]📈 Rendimiento:[/bold]
• Rendimiento Total: [{return_color}]{return_symbol}{return_pct:.2f}%[/{return_color}]
• Rendimiento Anualizado: [{return_color}]{return_symbol}{annualized_return:.2f}%[/{return_color}]
"""

        if values['shares']:
            panel_content += f"• Acciones/Unidades: {values['shares']:,.2f}\n"

        if values['purchase_price']:
            current_unit_price = values['current_value'] / values['shares'] if values['shares'] > 0 else 0
            panel_content += f"• Precio de Compra: ${values['purchase_price']:,.2f}\n"
            panel_content += f"• Precio Actual (est.): ${current_unit_price:,.2f}\n"

        console.print(Panel(panel_content, border_style="blue"))

        # Mostrar interpretación del rendimiento
        console.print("\n[bold]🎯 Interpretación:[/bold]")

        if return_pct > 20:
            console.print("[green]🎉 Excelente rendimiento![/green]")
        elif return_pct > 10:
            console.print("[green]👍 Buen rendimiento[/green]")
        elif return_pct > 0:
            console.print("[yellow]📊 Rendimiento positivo moderado[/yellow]")
        elif return_pct > -10:
            console.print("[yellow]⚠️ Pérdida menor[/yellow]")
        else:
            console.print("[red]📉 Pérdida significativa[/red]")

        # Comparación con rendimiento anualizado
        if annualized_return > 10:
            console.print("[green]💡 Rendimiento anualizado superior al mercado promedio (≈10%)[/green]")
        elif annualized_return > 5:
            console.print("[yellow]💡 Rendimiento anualizado moderado[/yellow]")
        else:
            console.print("[red]💡 Rendimiento anualizado por debajo del promedio del mercado[/red]")

    except Exception as e:
        console.print(f"[red]❌ Error al mostrar rendimiento: {e}[/red]")
        logger.error(f"Error en show_investment_performance: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@investments_app.command("delete")
def delete_investment(
    investment_id: str = typer.Argument(..., help="ID de la inversión a eliminar"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirmar eliminación sin preguntar")
) -> None:
    """🗑️ Eliminar inversión."""
    try:
        service = InvestmentService()

        # Buscar inversión
        investment = service.get_investment_by_id(investment_id)
        if not investment:
            console.print(f"[red]❌ Inversión no encontrada: {investment_id}[/red]")
            raise typer.Exit(1)

        # Mostrar detalles de la inversión
        console.print(f"\n[bold]Inversión a eliminar:[/bold]")
        console.print(f"ID: {investment.id}")
        console.print(f"Nombre: {investment.name}")
        console.print(f"Tipo: {investment.investment_type.value}")
        console.print(f"Valor inicial: ${investment.initial_amount:,.2f}")
        console.print(f"Valor actual: ${investment.current_value:,.2f}")

        # Confirmar eliminación
        if not confirm:
            confirm = typer.confirm("\n¿Está seguro que desea eliminar esta inversión?")

        if confirm:
            if service.delete_investment(investment_id):
                console.print("[green]✅ Inversión eliminada exitosamente[/green]")
            else:
                console.print("[red]❌ Error al eliminar la inversión[/red]")
                raise typer.Exit(1)
        else:
            console.print("[yellow]ℹ️ Eliminación cancelada[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Error al eliminar inversión: {e}[/red]")
        logger.error(f"Error en delete_investment: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


if __name__ == "__main__":
    investments_app()
