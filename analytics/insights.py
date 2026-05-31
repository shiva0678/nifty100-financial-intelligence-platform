import logging
from typing import List, Optional, Tuple

from companies.models import Company
from analytics.models import FinancialMetric, ProsCons
from django.db import transaction

logger = logging.getLogger(__name__)


def _safe_float(value: Optional[float]) -> float:
    if value is None:
        return float('nan')
    try:
        return float(value)
    except (TypeError, ValueError):
        return float('nan')


def _format_ratio(value: Optional[float], precision: int = 2) -> str:
    if value is None or value != value:
        return 'N/A'
    return f"{value:.{precision}f}"


def _format_percent(value: Optional[float], precision: int = 1) -> str:
    if value is None or value != value:
        return 'N/A'
    return f"{value * 100:.{precision}f}%"


def _append_line(lines: List[str], text: str) -> None:
    if text:
        lines.append(text)


def generate_pros_cons_from_metrics(company: Company, metrics: Optional[List[FinancialMetric]] = None) -> Tuple[str, str]:
    """Generate pro/con narratives from a company's computed financial metrics."""
    if metrics is None:
        metrics = list(FinancialMetric.objects.filter(company=company).order_by('-year'))

    if not metrics:
        return (
            "No financial metric history is available to generate insights at this time.",
            ""
        )

    latest = metrics[0]
    previous = metrics[1] if len(metrics) > 1 else None

    revenue_growth = _safe_float(latest.revenue_growth)
    profit_growth = _safe_float(latest.profit_growth)
    roe = _safe_float(latest.roe)
    debt_equity = _safe_float(latest.debt_to_equity)
    margin = _safe_float(latest.net_profit_margin)
    cash_conversion = _safe_float(latest.cash_conversion_ratio)
    free_cash_flow = latest.free_cash_flow

    pros: List[str] = []
    cons: List[str] = []

    if revenue_growth >= 0.20:
        _append_line(pros, f"Strong revenue momentum with year-over-year growth of {_format_percent(revenue_growth)}.")
    elif revenue_growth >= 0.10:
        _append_line(pros, f"Healthy top-line expansion at {_format_percent(revenue_growth)} year-over-year.")
    elif revenue_growth < 0:
        _append_line(cons, f"Revenue has declined by {_format_percent(abs(revenue_growth))}, indicating pressure on top-line growth.")
    else:
        _append_line(cons, f"Revenue growth is modest at {_format_percent(revenue_growth)}, leaving room to accelerate expansion.")

    if profit_growth >= 0.20:
        _append_line(pros, f"Strong profit growth of {_format_percent(profit_growth)} highlights improving earnings quality.")
    elif profit_growth >= 0.10:
        _append_line(pros, f"Good profit growth of {_format_percent(profit_growth)} supports margin expansion.")
    elif profit_growth < 0:
        _append_line(cons, f"Profit has contracted by {_format_percent(abs(profit_growth))}, which may reduce cash available for reinvestment.")
    else:
        _append_line(cons, f"Profit growth is moderate at {_format_percent(profit_growth)} and could be improved.")

    if roe >= 0.15:
        _append_line(pros, f"ROE is solid at {_format_percent(roe)}, demonstrating efficient use of shareholder capital.")
    elif roe >= 0.10:
        _append_line(pros, f"ROE of {_format_percent(roe)} is acceptable, but there is potential to do better.")
    else:
        _append_line(cons, f"ROE is low at {_format_percent(roe)}, signaling weak equity returns.")

    if margin >= 0.15:
        _append_line(pros, f"Net profit margin of {_format_percent(margin)} is strong and supports resilient earnings.")
    elif margin >= 0.08:
        _append_line(pros, f"Net profit margin of {_format_percent(margin)} is healthy for the current business profile.")
    elif margin >= 0:
        _append_line(cons, f"Net profit margin is modest at {_format_percent(margin)}, leaving limited buffer for downturns.")
    else:
        _append_line(cons, f"Net profit margin is negative at {_format_percent(margin)}, pointing to operating losses.")

    if debt_equity <= 0.5:
        _append_line(pros, f"Low leverage with a debt-to-equity ratio of {_format_ratio(debt_equity)} supports financial flexibility.")
    elif debt_equity <= 1.0:
        _append_line(pros, f"Moderate leverage at {_format_ratio(debt_equity)} is manageable, but should be monitored.")
    elif debt_equity > 2.0:
        _append_line(cons, f"High leverage with a debt-to-equity ratio above 2.0 may increase refinancing risk.")
    else:
        _append_line(cons, f"Debt-to-equity is {_format_ratio(debt_equity)}, so leverage should be watched closely.")

    if cash_conversion >= 0.70:
        _append_line(pros, f"Strong cash conversion ratio of {_format_percent(cash_conversion)} indicates efficient translation of profit into cash.")
    elif cash_conversion >= 0.50:
        _append_line(pros, f"Cash conversion is adequate at {_format_percent(cash_conversion)}, but further improvement would be beneficial.")
    else:
        _append_line(cons, f"Cash conversion is weak at {_format_percent(cash_conversion)}, which could strain liquidity.")

    if free_cash_flow is not None:
        if free_cash_flow >= 0:
            _append_line(pros, f"Positive free cash flow of {free_cash_flow:,.0f} supports reinvestment and capital return.")
        else:
            _append_line(cons, f"Negative free cash flow of {abs(free_cash_flow):,.0f} may limit funding for growth and shareholder distributions.")

    if previous is not None:
        prev_rg = _safe_float(previous.revenue_growth)
        prev_pg = _safe_float(previous.profit_growth)
        if revenue_growth > prev_rg and revenue_growth >= 0:
            _append_line(pros, "Revenue growth is improving compared to the prior year.")
        elif revenue_growth < prev_rg:
            _append_line(cons, "Revenue momentum has cooled relative to the prior year.")

        if profit_growth > prev_pg and profit_growth >= 0:
            _append_line(pros, "Profit growth is trending in the right direction year-over-year.")
        elif profit_growth < prev_pg:
            _append_line(cons, "Profit expansion is weakening compared to the previous year.")

    if not pros:
        _append_line(pros, "The company shows a stable financial profile with no major strength flags in the latest available metrics.")
    if not cons:
        _append_line(cons, "No major downside risks were detected in the latest computed financial metrics.")

    return ("\n".join(pros), "\n".join(cons))


def compute_and_save_insights(replace_existing: bool = False) -> None:
    """Persist generated AI-style insights into the ProsCons table."""
    logger.info("Computing and saving AI-generated pros/cons insights...")
    companies = Company.objects.prefetch_related('financial_metrics').all()
    updated_count = 0
    with transaction.atomic():
        for company in companies:
            try:
                existing = company.pros_cons
            except ProsCons.DoesNotExist:
                existing = None

            if existing and not replace_existing and (existing.pros or existing.cons):
                continue

            metrics = list(company.financial_metrics.all().order_by('-year'))
            pros, cons = generate_pros_cons_from_metrics(company, metrics=metrics)
            if not pros and not cons:
                continue

            ProsCons.objects.update_or_create(
                company=company,
                defaults={
                    'pros': pros,
                    'cons': cons,
                }
            )
            updated_count += 1

    logger.info("AI-generated insights stored for %d companies.", updated_count)
