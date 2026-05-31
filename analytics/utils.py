from typing import Iterable, List, Tuple, Dict


def _safe_number(value):
    if value is None:
        return float('nan')
    try:
        return float(value)
    except (TypeError, ValueError):
        return float('nan')


def compute_debt_equity(balance_sheets: Iterable) -> float:
    bs = list(balance_sheets)
    if not bs:
        return float('nan')
    latest = sorted(bs, key=lambda item: getattr(item, 'year', 0), reverse=True)[0]
    total_liabilities = _safe_number(getattr(latest, 'total_liabilities', None))
    equity = _safe_number(getattr(latest, 'equity_capital', 0)) + _safe_number(getattr(latest, 'reserves', 0))
    if not (total_liabilities == total_liabilities and equity == equity) or equity == 0:
        return float('nan')
    return total_liabilities / equity


def compute_health_score(company, profit_and_losses: Iterable) -> int:
    """Compute a 0-100 health score from company and its ProfitAndLoss iterable."""
    metrics = sorted(list(profit_and_losses), key=lambda item: getattr(item, 'year', 0), reverse=True)
    latest = metrics[0] if metrics else None
    previous = metrics[1] if len(metrics) > 1 else None

    latest_sales = _safe_number(getattr(latest, 'sales', None))
    previous_sales = _safe_number(getattr(previous, 'sales', None))
    latest_profit = _safe_number(getattr(latest, 'net_profit', None) or getattr(latest, 'profit_before_tax', None))
    previous_profit = _safe_number(getattr(previous, 'net_profit', None) or getattr(previous, 'profit_before_tax', None))

    revenue_growth = (latest_sales - previous_sales) / previous_sales if previous_sales > 0 else 0
    profit_growth = (latest_profit - previous_profit) / previous_profit if previous_profit > 0 else 0
    roe = _safe_number(company.roe_percentage or company.roce_percentage or 0)
    debt_equity = compute_debt_equity(getattr(company, 'balance_sheets', [])) if hasattr(company, 'balance_sheets') else float('nan')

    score = 0
    if revenue_growth >= 0.20:
        score += 20
    elif revenue_growth >= 0.10:
        score += 10

    if profit_growth >= 0.20:
        score += 20
    elif profit_growth >= 0.10:
        score += 10

    if roe >= 15:
        score += 20
    elif roe >= 10:
        score += 10

    if debt_equity <= 0.5:
        score += 20
    elif debt_equity <= 1.0:
        score += 10

    if latest_profit > 0:
        score += 20

    return int(min(max(score, 0), 100))


def compute_health_label(score: int) -> str:
    if score >= 80:
        return 'Excellent'
    if score >= 60:
        return 'Good'
    if score >= 40:
        return 'Average'
    return 'Weak'


def compute_fallback_health(company) -> Dict[str, object]:
    pl = list(company.profit_and_losses.order_by('-year'))
    latest = pl[0] if pl else None
    score = compute_health_score(company, pl)
    label = compute_health_label(score)
    return {"score": score, "label": label}
