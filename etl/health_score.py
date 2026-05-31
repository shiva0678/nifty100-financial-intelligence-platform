import logging
from django.db import transaction
from companies.models import Company
from analytics.models import FinancialMetric, FinancialHealthScore

logger = logging.getLogger(__name__)

def _assign_label(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Average"
    return "Weak"

def compute_and_save_health_scores():
    """Calculate a 0-100 health score per company-year and save it through Django ORM."""
    logger.info("Computing financial health scores...")

    metrics_qs = FinancialMetric.objects.all().values(
        "company_id", "year", "revenue_growth", "profit_growth", "roe",
        "debt_to_equity", "cash_conversion_ratio"
    )

    company_ids = sorted({item["company_id"] for item in metrics_qs if item.get("company_id") is not None})
    companies = Company.objects.in_bulk(company_ids)

    with transaction.atomic():
        for metrics in metrics_qs:
            company = companies.get(metrics["company_id"])
            if not company:
                continue

            score = 0
            rg = metrics.get("revenue_growth")
            if rg is not None:
                if rg >= 0.20:
                    score += 20
                elif rg >= 0.10:
                    score += 10

            pg = metrics.get("profit_growth")
            if pg is not None:
                if pg >= 0.20:
                    score += 20
                elif pg >= 0.10:
                    score += 10

            roe = metrics.get("roe")
            if roe is not None:
                if roe >= 0.15:
                    score += 20
                elif roe >= 0.10:
                    score += 10

            dte = metrics.get("debt_to_equity")
            if dte is not None:
                if dte <= 0.5:
                    score += 20
                elif dte <= 1.0:
                    score += 10

            ccr = metrics.get("cash_conversion_ratio")
            if ccr is not None:
                if ccr >= 0.70:
                    score += 20
                elif ccr >= 0.50:
                    score += 10

            score = min(score, 100)

            FinancialHealthScore.objects.update_or_create(
                company=company,
                year=metrics["year"],
                defaults={
                    "score": score,
                    "label": _assign_label(score),
                }
            )

    logger.info("Financial health scores computed and stored.")
