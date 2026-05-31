"""
api/views.py
DRF API Views for the Nifty 100 Financial platform.

Endpoints:
    GET /api/companies/                      - paginated list of all companies
    GET /api/company/<symbol>/               - full company profile
    GET /api/company/<symbol>/metrics/       - per-year financial metrics
    GET /api/company/<symbol>/score/         - health score history
    GET /api/top-companies/                  - top 10 by latest net profit
    GET /api/sectors/                        - placeholder; extend when sector field added
    GET /api/search/?q=<query>              - search by ticker or company name
"""

from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from companies.models import Company, ProfitAndLoss
from .serializers import (
    CompanyListSerializer,
    CompanyDetailSerializer,
    ProfitAndLossSerializer,
    HealthScoreSerializer,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


def _get_company_or_404(symbol: str):
    """Return Company by ticker (case-insensitive) or None."""
    try:
        return Company.objects.get(ticker__iexact=symbol)
    except Company.DoesNotExist:
        return None


def _company_prefetch():
    """Standard prefetch queryset for company detail."""
    return Company.objects.prefetch_related(
        "balance_sheets",
        "profit_and_losses",
        "cash_flows",
        "documents",
        "analysis",
        "pros_cons",
    )


from analytics.utils import compute_health_score, compute_debt_equity, compute_health_label, compute_fallback_health


# ---------------------------------------------------------------------------
# GET /api/companies/
# ---------------------------------------------------------------------------

@api_view(["GET"])
@cache_page(60 * 5)
def companies_list(request):
    """
    Return a paginated list of all companies with latest revenue, profit,
    and health score.
    """
    qs = Company.objects.prefetch_related("profit_and_losses").order_by("company_name")
    paginator = StandardPagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = CompanyListSerializer(page, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


# ---------------------------------------------------------------------------
# GET /api/company/<symbol>/
# ---------------------------------------------------------------------------

@api_view(["GET"])
@cache_page(60 * 5)
def company_detail(request, symbol):
    """
    Return the full profile of a single company identified by its ticker symbol.
    """
    company = _get_company_or_404(symbol)
    if not company:
        return Response(
            {"error": f"Company with ticker '{symbol}' not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    # Fetch with all related data to minimise queries
    company = _company_prefetch().get(pk=company.pk)
    serializer = CompanyDetailSerializer(company, context={"request": request})
    return Response(serializer.data)


# ---------------------------------------------------------------------------
# GET /api/company/<symbol>/metrics/
# ---------------------------------------------------------------------------

@api_view(["GET"])
def company_metrics(request, symbol):
    """
    Return per-year financial metrics (D/E, ROE, ROA, margins, growth, FCF)
    for the requested company.
    """
    company = _get_company_or_404(symbol)
    if not company:
        return Response(
            {"error": f"Company with ticker '{symbol}' not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    metrics_qs = (
        ProfitAndLoss.objects
        .filter(company=company)
        .order_by("-year")
    )
    serializer = ProfitAndLossSerializer(metrics_qs, many=True, context={"request": request})
    return Response({
        "company": company.ticker,
        "company_name": company.company_name,
        "metrics": serializer.data,
    })


# ---------------------------------------------------------------------------
# GET /api/company/<symbol>/score/
# ---------------------------------------------------------------------------

@api_view(["GET"])
@cache_page(60 * 3)
def company_score(request, symbol):
    """
    Return the financial health score history for the requested company.
    Scores are stored in the raw financial_health_score table.
    """
    company = _get_company_or_404(symbol)
    if not company:
        return Response(
            {"error": f"Company with ticker '{symbol}' not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    # Prefer ORM-based lookup for portability and safety
    from analytics.models import FinancialHealthScore
    try:
        rows_qs = FinancialHealthScore.objects.filter(company=company).select_related('company').order_by('-year')
        rows = list(rows_qs.values_list('company__company_id', 'company__ticker', 'company__company_name', 'year', 'score', 'label'))
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = []
    if rows:
        data = [
            {
                "company_id": r[0],
                "ticker": r[1],
                "company_name": r[2],
                "year": r[3],
                "score": r[4],
                "label": r[5],
            }
            for r in rows
        ]
    else:
        company = _company_prefetch().get(pk=company.pk)
        latest_pl = company.profit_and_losses.order_by('-year').first()
        computed_score = _compute_health_score(company, list(company.profit_and_losses.all()))
        year = latest_pl.year if latest_pl else 0
        data = [
            {
                "company_id": company.pk,
                "ticker": company.ticker,
                "company_name": company.company_name,
                "year": year,
                "score": int(computed_score),
                "label": (
                    "Excellent" if computed_score >= 80 else
                    "Good" if computed_score >= 60 else
                    "Average" if computed_score >= 40 else
                    "Weak"
                ),
            }
        ]
    serializer = HealthScoreSerializer(data, many=True)
    return Response({"company": symbol.upper(), "scores": serializer.data})


# ---------------------------------------------------------------------------
# GET /api/top-companies/
# ---------------------------------------------------------------------------

@api_view(["GET"])
@cache_page(60 * 5)
def top_companies(request):
    """
    Return the top N companies ranked by latest year net profit.
    Query param: ?n=10 (default 10, max 50)
    """
    try:
        n = min(int(request.query_params.get("n", 10)), 50)
    except (ValueError, TypeError):
        n = 10

    from django.db.models import Subquery, OuterRef
    from analytics.models import FinancialHealthScore

    try:
        latest_pl = ProfitAndLoss.objects.filter(company=OuterRef('pk')).order_by('-year')
        qs = (
            Company.objects
            .annotate(latest_year=Subquery(latest_pl.values('year')[:1]))
            .annotate(latest_revenue=Subquery(latest_pl.values('sales')[:1]))
            .annotate(latest_net_profit=Subquery(latest_pl.values('net_profit')[:1]))
            .order_by('-latest_net_profit')
        )
        companies = list(qs.values(
            'company_id', 'ticker', 'company_name', 'company_logo', 'website', 'roce_percentage', 'roe_percentage',
            'latest_year', 'latest_revenue', 'latest_net_profit'
        )[:n])

        # Fetch health scores for these company/year pairs in bulk
        pairs = [(c['company_id'], c['latest_year']) for c in companies if c.get('latest_year') is not None]
        health_map = {}
        if pairs:
            fhs_qs = FinancialHealthScore.objects.filter(
                company_id__in=[p[0] for p in pairs],
                year__in=[p[1] for p in pairs]
            ).values_list('company_id', 'year', 'score', 'label')
            for cid, yr, sc, lb in fhs_qs:
                health_map[(cid, yr)] = (sc, lb)

        result = []
        for c in companies:
            key = (c['company_id'], c.get('latest_year'))
            sc, lb = health_map.get(key, (None, None))
            result.append({
                "company_id": c['company_id'],
                "ticker": c['ticker'],
                "company_name": c['company_name'],
                "company_logo": c.get('company_logo'),
                "website": c.get('website'),
                "roce_percentage": c.get('roce_percentage'),
                "roe_percentage": c.get('roe_percentage'),
                "latest_year": c.get('latest_year'),
                "latest_revenue": c.get('latest_revenue'),
                "latest_net_profit": c.get('latest_net_profit'),
                "health_score": sc,
                "health_label": lb,
            })
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"count": len(result), "companies": result})


# ---------------------------------------------------------------------------
# GET /api/company/<symbol>/insights/
# ---------------------------------------------------------------------------

@api_view(["GET"])
def company_insights(request, symbol):
    """
    Return Pros & Cons insights for a company. If stored in DB return that,
    otherwise compute using the analytics insights engine (non-destructive).
    """
    company = _get_company_or_404(symbol)
    if not company:
        return Response({"error": f"Company with ticker '{symbol}' not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        pros_cons = company.pros_cons
        return Response({"company": company.ticker, "pros": pros_cons.pros, "cons": pros_cons.cons})
    except Exception:
        # compute fallback without persisting
        try:
            from analytics.insights import generate_pros_cons_from_metrics
            pros, cons = generate_pros_cons_from_metrics(company)
            return Response({"company": company.ticker, "pros": pros, "cons": cons})
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------------------------------------------------------------------
# GET /api/sectors/
# ---------------------------------------------------------------------------

@api_view(["GET"])
def sectors(request):
    """
    Return distinct sectors / industry groups.
    NOTE: The current schema does not store a 'sector' column.
    This endpoint returns a descriptive message and is ready to be extended
    once the sector field is added to the Company model.
    """
    return Response({
        "message": (
            "Sector data is not yet available in the current schema. "
            "Add a 'sector' CharField to the Company model and re-run migrations "
            "to activate this endpoint."
        ),
        "sectors": [],
    })


# ---------------------------------------------------------------------------
# GET /api/search/?q=<query>
# ---------------------------------------------------------------------------

@api_view(["GET"])
def search(request):
    """
    Full-text search across ticker and company_name.
    Query param: ?q=<search_term>
    """
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response(
            {"error": "Please provide a search term using the '?q=' query parameter."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    qs = Company.objects.filter(
        company_name__icontains=query
    ) | Company.objects.filter(
        ticker__icontains=query
    )
    qs = qs.distinct().prefetch_related("profit_and_losses").order_by("company_name")

    paginator = StandardPagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = CompanyListSerializer(page, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)
