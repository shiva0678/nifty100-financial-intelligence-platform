"""
api/serializers.py
Serializers for the Nifty 100 Financial REST API.
"""
from rest_framework import serializers
from companies.models import Company, BalanceSheet, ProfitAndLoss, CashFlow, Document
from analytics.models import Analysis, ProsCons, FinancialMetric


# ---------------------------------------------------------------------------
# Child / nested serializers
# ---------------------------------------------------------------------------

class BalanceSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceSheet
        fields = [
            "year", "equity_capital", "reserves", "borrowings",
            "other_liabilities", "total_liabilities",
            "fixed_assets", "cwip", "investments", "other_assets", "total_assets",
        ]


class ProfitAndLossSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfitAndLoss
        fields = [
            "year", "sales", "expenses", "operating_profit", "opm_percentage",
            "other_income", "interest", "depreciation", "profit_before_tax",
            "tax_percentage", "net_profit", "eps", "dividend_payout",
        ]


class CashFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashFlow
        fields = [
            "year", "operating_activity", "investing_activity",
            "financing_activity", "net_cash_flow",
        ]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["year", "annual_report"]


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = [
            "compounded_sales_growth", "compounded_profit_growth",
            "stock_price_cagr", "roe_percentage",
        ]


class ProsConsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProsCons
        fields = ["pros", "cons"]


class FinancialMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialMetric
        fields = [
            "year", "debt_to_equity", "roe", "roa", "net_profit_margin",
            "revenue_growth", "profit_growth", "cash_conversion_ratio", "free_cash_flow",
        ]


# ---------------------------------------------------------------------------
# Company list  (lightweight)
# ---------------------------------------------------------------------------

class CompanyListSerializer(serializers.ModelSerializer):
    """Compact card used in list / top-companies endpoints."""
    latest_revenue = serializers.SerializerMethodField()
    latest_net_profit = serializers.SerializerMethodField()
    health_score = serializers.SerializerMethodField()
    health_label = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            "company_id", "ticker", "company_name", "company_logo",
            "website", "face_value", "book_value",
            "roce_percentage", "roe_percentage",
            "latest_revenue", "latest_net_profit",
            "health_score", "health_label",
        ]

    # --- helpers that cache per request so we don't hit DB per row ---
    def _latest_pl(self, obj):
        cache = self.context.setdefault("_pl_cache", {})
        if obj.pk not in cache:
            cache[obj.pk] = obj.profit_and_losses.order_by("-year").first()
        return cache[obj.pk]

    def _latest_health(self, obj):
        cache = self.context.setdefault("_hs_cache", {})
        if obj.pk not in cache:
            try:
                from django.db import connection
                with connection.cursor() as cur:
                    cur.execute(
                        "SELECT score, label FROM financial_health_score "
                        "WHERE company_id = %s ORDER BY year DESC LIMIT 1",
                        [obj.pk],
                    )
                    row = cur.fetchone()
                    cache[obj.pk] = {"score": row[0], "label": row[1]} if row else {}
            except Exception:
                cache[obj.pk] = {}
        if not cache[obj.pk]:
            cache[obj.pk] = self._compute_fallback_health(obj)
        return cache[obj.pk]

    from analytics.utils import compute_fallback_health

    def _compute_fallback_health(self, company):
        return compute_fallback_health(company)

    def get_latest_revenue(self, obj):
        pl = self._latest_pl(obj)
        return pl.sales if pl else None

    def get_latest_net_profit(self, obj):
        pl = self._latest_pl(obj)
        return pl.net_profit if pl else None

    def get_health_score(self, obj):
        return self._latest_health(obj).get("score")

    def get_health_label(self, obj):
        return self._latest_health(obj).get("label")


# ---------------------------------------------------------------------------
# Company detail  (full nested)
# ---------------------------------------------------------------------------

class CompanyDetailSerializer(serializers.ModelSerializer):
    """Full company profile with all related financial statements."""
    balance_sheets = BalanceSheetSerializer(many=True, read_only=True)
    profit_and_losses = ProfitAndLossSerializer(many=True, read_only=True)
    cash_flows = CashFlowSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    analysis = AnalysisSerializer(read_only=True)
    pros_cons = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            "company_id", "ticker", "company_name", "company_logo",
            "chart_link", "about_company", "website",
            "nse_profile", "bse_profile",
            "face_value", "book_value", "roce_percentage", "roe_percentage",
            "balance_sheets", "profit_and_losses", "cash_flows",
            "documents", "analysis", "pros_cons",
            "created_at", "updated_at",
        ]

    def get_pros_cons(self, obj):
        try:
            existing = obj.pros_cons
        except ProsCons.DoesNotExist:
            existing = None

        if existing and (existing.pros or existing.cons):
            return ProsConsSerializer(existing).data

        from analytics.insights import generate_pros_cons_from_metrics

        pros, cons = generate_pros_cons_from_metrics(obj)
        return {
            "pros": pros,
            "cons": cons,
        }


# ---------------------------------------------------------------------------
# Health score
# ---------------------------------------------------------------------------

class HealthScoreSerializer(serializers.Serializer):
    """Serializes raw-SQL health score rows."""
    company_id = serializers.IntegerField()
    ticker = serializers.CharField()
    company_name = serializers.CharField()
    year = serializers.IntegerField()
    score = serializers.IntegerField()
    label = serializers.CharField()
