"""Comandos CLI para generación de reportes."""

from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.services.report_service import ReportService
from src.utils.logging import get_logger

# Crear subcomando para reportes
reports_app = typer.Typer(
    name="reports",
    help="📊 Generación de reportes financieros",
    no_args_is_help=True
)

console = Console()
logger = get_logger(__name__)


@reports_app.command("monthly")
def monthly_report(
    year: Optional[int] = typer.Option(None, "-y", "--year", help="Año del reporte"),
    month: Optional[int] = typer.Option(None, "-m", "--month", help="Mes del reporte (1-12)")
) -> None:
    """📅 Generar reporte mensual completo."""
    try:
        service = ReportService()

        # Usar fecha actual si no se especifica
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month

        # Validar mes
        if month < 1 or month > 12:
            console.print("[red]❌ El mes debe estar entre 1 y 12[/red]")
            raise typer.Exit(1)

        # Generar reporte
        with console.status(f"[bold green]Generando reporte mensual para {year}-{month:02d}..."):
            report = service.generate_monthly_report(year, month)

        # Mostrar información del período
        period = report['period']
        transactions = report['transactions']
        budget = report['budget']
        investments = report['investments']
        trends = report['trends']

        # Panel principal
        console.print(f"\n[bold blue]📅 Reporte Mensual - {period['month_name']}[/bold blue]")
        console.print(f"[dim]Período: {period['start_date']} a {period['end_date']}[/dim]\n")

        # Resumen de transacciones
        net_amount = transactions['net_amount']
        net_color = "green" if net_amount >= 0 else "red"
        net_symbol = "+" if net_amount >= 0 else ""

        transactions_panel = f"""
[bold]💳 Resumen de Transacciones[/bold]

💰 [green]Ingresos:[/green] ${transactions['income_total']:,.2f}
💸 [red]Gastos:[/red] ${transactions['expense_total']:,.2f}
📊 [{net_color}]Balance Neto:[/{net_color}] [{net_color}]{net_symbol}${net_amount:,.2f}[/{net_color}]
📋 [white]Total Transacciones:[/white] {transactions['transactions_count']}
💵 [dim]Promedio por Transacción:[/dim] ${transactions['average_transaction']:,.2f}
"""

        console.print(Panel(transactions_panel, border_style="blue"))

        # Top categorías de gastos
        if transactions['top_expense_categories']:
            console.print("\n[bold]🏷️ Top Categorías de Gastos:[/bold]")

            categories_table = Table()
            categories_table.add_column("Posición", justify="center", style="dim")
            categories_table.add_column("Categoría", style="white")
            categories_table.add_column("Monto", justify="right", style="red")
            categories_table.add_column("% del Total", justify="right", style="yellow")

            total_expenses = transactions['expense_total']
            for i, category in enumerate(transactions['top_expense_categories'], 1):
                percentage = (category['amount'] / total_expenses * 100) if total_expenses > 0 else 0
                categories_table.add_row(
                    str(i),
                    category['name'],
                    f"${category['amount']:,.2f}",
                    f"{percentage:.1f}%"
                )

            console.print(categories_table)

        # Análisis de presupuesto si existe
        if budget:
            console.print("\n[bold]💰 Análisis de Presupuesto:[/bold]")

            budget_totals = budget['totals']
            budget_status = "Excedido" if budget['is_over_budget'] else "Dentro del límite"
            budget_color = "red" if budget['is_over_budget'] else "green"

            budget_panel = f"""
[bold]Presupuesto:[/bold] {budget['budget']['name']}
💰 [blue]Asignado:[/blue] ${budget_totals['allocated_amount']:,.2f}
💸 [red]Gastado:[/red] ${budget_totals['spent_amount']:,.2f}
💵 [green]Restante:[/green] ${budget_totals['remaining_amount']:,.2f}
📊 [yellow]Progreso:[/yellow] {budget_totals['percentage_used']:.1f}% usado
🎯 [{budget_color}]Estado:[/{budget_color}] [{budget_color}]{budget_status}[/{budget_color}]
"""

            console.print(Panel(budget_panel, border_style=budget_color))

        # Resumen de inversiones si hay datos
        if investments and investments.get('investments_count', 0) > 0:
            console.print("\n[bold]📈 Resumen de Inversiones:[/bold]")

            inv_return = investments['total_return']
            inv_return_pct = investments['return_percentage']
            inv_color = "green" if inv_return >= 0 else "red"
            inv_symbol = "+" if inv_return >= 0 else ""

            investments_panel = f"""
💰 [cyan]Total Invertido:[/cyan] ${investments['total_invested']:,.2f}
💵 [yellow]Valor Actual:[/yellow] ${investments['current_value']:,.2f}
📈 [{inv_color}]Rendimiento:[/{inv_color}] [{inv_color}]{inv_symbol}${inv_return:,.2f} ({inv_symbol}{inv_return_pct:.1f}%)[/{inv_color}]
🎯 [white]Número de Inversiones:[/white] {investments['investments_count']}
"""

            console.print(Panel(investments_panel, border_style="cyan"))

        # Análisis de tendencias
        if trends and 'changes' in trends:
            console.print("\n[bold]📈 Análisis de Tendencias:[/bold]")

            changes = trends['changes']
            income_change = changes['income_change_percentage']
            expense_change = changes['expense_change_percentage']

            # Formatear cambios con colores
            income_color = "green" if income_change >= 0 else "red"
            expense_color = "red" if expense_change >= 0 else "green"  # Más gastos = malo

            income_symbol = "+" if income_change >= 0 else ""
            expense_symbol = "+" if expense_change >= 0 else ""

            trends_content = f"""
Comparación con el mes anterior:

💰 [bold]Ingresos:[/bold] [{income_color}]{income_symbol}{income_change:.1f}%[/{income_color}] ({changes['income_trend']})
💸 [bold]Gastos:[/bold] [{expense_color}]{expense_symbol}{expense_change:.1f}%[/{expense_color}] ({changes['expense_trend']})
"""

            console.print(Panel(trends_content, title="📊 Tendencias", border_style="yellow"))

        console.print(f"\n[dim]Reporte generado el {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error al generar reporte mensual: {e}[/red]")
        logger.error(f"Error en monthly_report: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@reports_app.command("yearly")
def yearly_report(
    year: Optional[int] = typer.Option(None, "-y", "--year", help="Año del reporte")
) -> None:
    """📅 Generar reporte anual completo."""
    try:
        service = ReportService()

        # Usar año actual si no se especifica
        if year is None:
            year = datetime.now().year

        # Generar reporte
        with console.status(f"[bold green]Generando reporte anual para {year}..."):
            report = service.generate_yearly_report(year)

        period = report['period']
        annual_summary = report['annual_summary']
        monthly_breakdown = report['monthly_breakdown']
        investments = report['investments']
        growth_analysis = report['growth_analysis']

        # Panel principal
        console.print(f"\n[bold blue]📅 Reporte Anual - {year}[/bold blue]\n")

        # Resumen anual
        net_amount = annual_summary['net_amount']
        net_color = "green" if net_amount >= 0 else "red"
        net_symbol = "+" if net_amount >= 0 else ""

        annual_panel = f"""
[bold]📊 Resumen Anual {year}[/bold]

💰 [green]Ingresos Totales:[/green] ${annual_summary['income_total']:,.2f}
💸 [red]Gastos Totales:[/red] ${annual_summary['expense_total']:,.2f}
📊 [{net_color}]Balance Anual:[/{net_color}] [{net_color}]{net_symbol}${net_amount:,.2f}[/{net_color}]
📋 [white]Total Transacciones:[/white] {annual_summary['transactions_count']}
💵 [dim]Promedio Mensual de Ingresos:[/dim] ${annual_summary['income_total']/12:,.2f}
💸 [dim]Promedio Mensual de Gastos:[/dim] ${annual_summary['expense_total']/12:,.2f}
"""

        console.print(Panel(annual_panel, border_style="blue"))

        # Análisis mensual
        console.print("\n[bold]📊 Desglose Mensual:[/bold]")

        monthly_table = Table()
        monthly_table.add_column("Mes", style="cyan")
        monthly_table.add_column("Ingresos", justify="right", style="green")
        monthly_table.add_column("Gastos", justify="right", style="red")
        monthly_table.add_column("Balance", justify="right")
        monthly_table.add_column("Transacciones", justify="center", style="dim")

        for month_data in monthly_breakdown:
            month_net = month_data['net_amount']
            net_color = "green" if month_net >= 0 else "red"
            net_symbol = "+" if month_net >= 0 else ""

            monthly_table.add_row(
                month_data['month_name'],
                f"${month_data['income_total']:,.2f}",
                f"${month_data['expense_total']:,.2f}",
                f"[{net_color}]{net_symbol}${month_net:,.2f}[/{net_color}]",
                str(month_data['transactions_count'])
            )

        console.print(monthly_table)

        # Top categorías anuales
        if annual_summary['top_expense_categories']:
            console.print("\n[bold]🏷️ Top Categorías de Gastos del Año:[/bold]")

            for i, category in enumerate(annual_summary['top_expense_categories'], 1):
                percentage = (category['amount'] / annual_summary['expense_total'] * 100) if annual_summary['expense_total'] > 0 else 0
                console.print(f"  {i}. {category['name']}: ${category['amount']:,.2f} ({percentage:.1f}%)")

        # Análisis de crecimiento
        if growth_analysis and 'growth_rates' in growth_analysis:
            console.print("\n[bold]📈 Análisis de Crecimiento (vs. año anterior):[/bold]")

            growth_rates = growth_analysis['growth_rates']
            income_growth = growth_rates['income_growth']
            expense_growth = growth_rates['expense_growth']
            net_growth = growth_rates['net_growth']

            # Formatear con colores
            income_color = "green" if income_growth >= 0 else "red"
            expense_color = "red" if expense_growth >= 0 else "green"  # Más gastos = malo
            net_color = "green" if net_growth >= 0 else "red"

            income_symbol = "+" if income_growth >= 0 else ""
            expense_symbol = "+" if expense_growth >= 0 else ""
            net_symbol = "+" if net_growth >= 0 else ""

            growth_content = f"""
💰 [bold]Crecimiento de Ingresos:[/bold] [{income_color}]{income_symbol}{income_growth:.1f}%[/{income_color}]
💸 [bold]Crecimiento de Gastos:[/bold] [{expense_color}]{expense_symbol}{expense_growth:.1f}%[/{expense_color}]
📊 [bold]Crecimiento del Balance Neto:[/bold] [{net_color}]{net_symbol}{net_growth:.1f}%[/{net_color}]
"""

            console.print(Panel(growth_content, title="📈 Crecimiento Anual", border_style="yellow"))

        # Resumen de inversiones
        if investments and investments.get('investments_count', 0) > 0:
            console.print("\n[bold]📈 Portafolio de Inversiones:[/bold]")

            inv_return = investments['total_return']
            inv_return_pct = investments['return_percentage']
            inv_color = "green" if inv_return >= 0 else "red"
            inv_symbol = "+" if inv_return >= 0 else ""

            investments_panel = f"""
💰 [cyan]Total Invertido:[/cyan] ${investments['total_invested']:,.2f}
💵 [yellow]Valor Actual:[/yellow] ${investments['current_value']:,.2f}
📈 [{inv_color}]Rendimiento Total:[/{inv_color}] [{inv_color}]{inv_symbol}${inv_return:,.2f} ({inv_symbol}{inv_return_pct:.1f}%)[/{inv_color}]
🎯 [white]Número de Inversiones:[/white] {investments['investments_count']}
"""

            console.print(Panel(investments_panel, border_style="cyan"))

        console.print(f"\n[dim]Reporte generado el {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error al generar reporte anual: {e}[/red]")
        logger.error(f"Error en yearly_report: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@reports_app.command("categories")
def categories_report(
    days: int = typer.Option(30, "-d", "--days", help="Días hacia atrás para el análisis"),
    category: Optional[str] = typer.Option(None, "-c", "--category", help="Filtrar por categoría específica")
) -> None:
    """🏷️ Generar reporte por categorías."""
    try:
        service = ReportService()

        # Calcular fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Generar reporte
        with console.status(f"[bold green]Analizando categorías para los últimos {days} días..."):
            report = service.generate_category_report(start_date, end_date, category)

        # Mostrar información del período
        period = report['period']
        summary = report['summary']
        categories = report['categories']

        # Panel principal
        title = f"🏷️ Análisis por Categorías - {days} días"
        if category:
            title += f" (Filtro: {category})"

        console.print(f"\n[bold blue]{title}[/bold blue]")
        console.print(f"[dim]Período: {period['start_date']} a {period['end_date']}[/dim]\n")

        # Resumen general
        summary_panel = f"""
[bold]📊 Resumen General[/bold]

🏷️ [white]Total Categorías:[/white] {summary['total_categories']}
💰 [green]Ingresos Totales:[/green] ${summary['total_income']:,.2f}
💸 [red]Gastos Totales:[/red] ${summary['total_expense']:,.2f}
📋 [white]Total Transacciones:[/white] {summary['total_transactions']}
📊 [blue]Balance Neto:[/blue] ${summary['total_income'] - summary['total_expense']:,.2f}
"""

        console.print(Panel(summary_panel, border_style="blue"))

        # Tabla detallada por categorías
        if categories:
            console.print("\n[bold]📋 Desglose por Categorías:[/bold]")

            categories_table = Table()
            categories_table.add_column("Categoría", style="white")
            categories_table.add_column("Ingresos", justify="right", style="green")
            categories_table.add_column("Gastos", justify="right", style="red")
            categories_table.add_column("Balance", justify="right")
            categories_table.add_column("Transacciones", justify="center", style="dim")
            categories_table.add_column("Promedio", justify="right", style="yellow")

            for cat in categories:
                net_amount = cat['net_amount']
                net_color = "green" if net_amount >= 0 else "red"
                net_symbol = "+" if net_amount >= 0 else ""

                categories_table.add_row(
                    cat['name'],
                    f"${cat['income']:,.2f}" if cat['income'] > 0 else "-",
                    f"${cat['expense']:,.2f}" if cat['expense'] > 0 else "-",
                    f"[{net_color}]{net_symbol}${net_amount:,.2f}[/{net_color}]",
                    str(cat['transactions_count']),
                    f"${cat['average_transaction']:,.2f}"
                )

            console.print(categories_table)

            # Destacar categorías principales
            if not category:  # Solo si no estamos filtrando
                console.print("\n[bold]🎯 Categorías Destacadas:[/bold]")

                # Categoría con más gastos
                top_expense_cat = max(categories, key=lambda x: x['expense'])
                console.print(f"💸 [red]Mayor gasto:[/red] {top_expense_cat['name']} - ${top_expense_cat['expense']:,.2f}")

                # Categoría con más ingresos (si hay)
                income_categories = [cat for cat in categories if cat['income'] > 0]
                if income_categories:
                    top_income_cat = max(income_categories, key=lambda x: x['income'])
                    console.print(f"💰 [green]Mayor ingreso:[/green] {top_income_cat['name']} - ${top_income_cat['income']:,.2f}")

                # Categoría con más transacciones
                most_active_cat = max(categories, key=lambda x: x['transactions_count'])
                console.print(f"📋 [blue]Más activa:[/blue] {most_active_cat['name']} - {most_active_cat['transactions_count']} transacciones")

        else:
            console.print("[yellow]ℹ️ No se encontraron datos para el período especificado[/yellow]")

        console.print(f"\n[dim]Reporte generado el {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error al generar reporte de categorías: {e}[/red]")
        logger.error(f"Error en categories_report: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


@reports_app.command("cash-flow")
def cash_flow_report(
    days: int = typer.Option(30, "-d", "--days", help="Días hacia atrás para el análisis"),
    granularity: str = typer.Option("daily", "-g", "--granularity", help="Granularidad: daily, weekly, monthly")
) -> None:
    """💰 Generar reporte de flujo de efectivo."""
    try:
        service = ReportService()

        # Validar granularidad
        if granularity not in ["daily", "weekly", "monthly"]:
            console.print("[red]❌ Granularidad debe ser: daily, weekly, monthly[/red]")
            raise typer.Exit(1)

        # Calcular fechas
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Generar reporte
        with console.status(f"[bold green]Analizando flujo de efectivo ({granularity})..."):
            report = service.generate_cash_flow_report(start_date, end_date, granularity)

        period = report['period']
        cash_flow = report['cash_flow']
        summary = report['summary']

        # Panel principal
        console.print(f"\n[bold blue]💰 Flujo de Efectivo - {granularity.title()}[/bold blue]")
        console.print(f"[dim]Período: {period['start_date']} a {period['end_date']} ({days} días)[/dim]\n")

        # Resumen del flujo
        final_balance = summary['final_balance']
        balance_color = "green" if final_balance >= 0 else "red"
        balance_symbol = "+" if final_balance >= 0 else ""

        summary_panel = f"""
[bold]📊 Resumen del Flujo de Efectivo[/bold]

💰 [green]Total Ingresos:[/green] ${summary['total_income']:,.2f}
💸 [red]Total Gastos:[/red] ${summary['total_expense']:,.2f}
📊 [blue]Flujo Neto:[/blue] ${summary['net_flow']:,.2f}
💵 [{balance_color}]Balance Final:[/{balance_color}] [{balance_color}]{balance_symbol}${final_balance:,.2f}[/{balance_color}]
📋 [white]Períodos Analizados:[/white] {summary['periods_count']}
"""

        console.print(Panel(summary_panel, border_style="blue"))

        # Tabla de flujo de efectivo
        if cash_flow:
            console.print(f"\n[bold]📋 Detalle del Flujo ({granularity.title()}):[/bold]")

            # Limitar número de filas mostradas
            max_rows = 15
            display_cash_flow = cash_flow[-max_rows:] if len(cash_flow) > max_rows else cash_flow

            flow_table = Table()
            flow_table.add_column("Período", style="cyan")
            flow_table.add_column("Ingresos", justify="right", style="green")
            flow_table.add_column("Gastos", justify="right", style="red")
            flow_table.add_column("Flujo Neto", justify="right")
            flow_table.add_column("Balance Acum.", justify="right", style="yellow")
            flow_table.add_column("Trans.", justify="center", style="dim")

            for flow in display_cash_flow:
                # Formatear período
                if granularity == "daily":
                    period_str = flow['period_start'].strftime("%m-%d")
                elif granularity == "weekly":
                    period_str = f"{flow['period_start'].strftime('%m-%d')} - {flow['period_end'].strftime('%m-%d')}"
                else:  # monthly
                    period_str = flow['period_start'].strftime("%Y-%m")

                # Formatear flujo neto
                net_flow = flow['net_flow']
                net_color = "green" if net_flow >= 0 else "red"
                net_symbol = "+" if net_flow >= 0 else ""

                # Formatear balance acumulado
                running_balance = flow['running_balance']
                balance_color = "green" if running_balance >= 0 else "red"
                balance_symbol = "+" if running_balance >= 0 else ""

                flow_table.add_row(
                    period_str,
                    f"${flow['income']:,.2f}" if flow['income'] > 0 else "-",
                    f"${flow['expense']:,.2f}" if flow['expense'] > 0 else "-",
                    f"[{net_color}]{net_symbol}${net_flow:,.2f}[/{net_color}]",
                    f"[{balance_color}]{balance_symbol}${running_balance:,.2f}[/{balance_color}]",
                    str(flow['transactions_count'])
                )

            console.print(flow_table)

            if len(cash_flow) > max_rows:
                console.print(f"[dim]... mostrando últimos {max_rows} de {len(cash_flow)} períodos[/dim]")

        # Análisis de tendencias
        if len(cash_flow) >= 3:
            console.print("\n[bold]📈 Análisis de Tendencias:[/bold]")

            # Comparar primeros vs últimos 3 períodos
            first_periods = cash_flow[:3]
            last_periods = cash_flow[-3:]

            avg_income_first = sum(p['income'] for p in first_periods) / len(first_periods)
            avg_income_last = sum(p['income'] for p in last_periods) / len(last_periods)

            avg_expense_first = sum(p['expense'] for p in first_periods) / len(first_periods)
            avg_expense_last = sum(p['expense'] for p in last_periods) / len(last_periods)

            income_trend = ((avg_income_last - avg_income_first) / avg_income_first * 100) if avg_income_first > 0 else 0
            expense_trend = ((avg_expense_last - avg_expense_first) / avg_expense_first * 100) if avg_expense_first > 0 else 0

            # Mostrar tendencias
            income_color = "green" if income_trend >= 0 else "red"
            expense_color = "red" if expense_trend >= 0 else "green"

            income_symbol = "+" if income_trend >= 0 else ""
            expense_symbol = "+" if expense_trend >= 0 else ""

            console.print(f"💰 [bold]Tendencia de Ingresos:[/bold] [{income_color}]{income_symbol}{income_trend:.1f}%[/{income_color}]")
            console.print(f"💸 [bold]Tendencia de Gastos:[/bold] [{expense_color}]{expense_symbol}{expense_trend:.1f}%[/{expense_color}]")

        console.print(f"\n[dim]Reporte generado el {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error al generar reporte de flujo de efectivo: {e}[/red]")
        logger.error(f"Error en cash_flow_report: {e}")
        raise typer.Exit(1)
    finally:
        if 'service' in locals():
            service.close()


if __name__ == "__main__":
    reports_app()
