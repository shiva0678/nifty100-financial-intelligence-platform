from django.db import models

class Analysis(models.Model):
    # Primary Key is Foreign Key to Company, guaranteeing pure 1-to-1 relationship integrity
    company = models.OneToOneField(
        'companies.Company',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='analysis',
        verbose_name="Company"
    )
    compounded_sales_growth = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Compounded Sales Growth %"
    )
    compounded_profit_growth = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Compounded Profit Growth %"
    )
    stock_price_cagr = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Stock Price CAGR %"
    )
    roe_percentage = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Return on Equity %"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'analysis'
        verbose_name = 'Company Growth Analysis'
        verbose_name_plural = 'Company Growth Analyses'
        ordering = ['company']
        indexes = [
            models.Index(fields=['compounded_sales_growth'], name='idx_django_analysis_sales'),
            models.Index(fields=['roe_percentage'], name='idx_django_analysis_roe'),
        ]

    def __str__(self):
        return f"Analysis - {self.company.ticker}"


class ProsCons(models.Model):
    # Primary Key is Foreign Key to Company, guaranteeing pure 1-to-1 relationship integrity
    company = models.OneToOneField(
        'companies.Company',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='pros_cons',
        verbose_name="Company"
    )
    pros = models.TextField(null=True, blank=True, verbose_name="Key Strengths (Pros)")
    cons = models.TextField(null=True, blank=True, verbose_name="Key Weaknesses/Risks (Cons)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'pros_cons'
        verbose_name = 'Pros & Cons Profile'
        verbose_name_plural = 'Pros & Cons Profiles'
        ordering = ['company']

    def __str__(self):
        return f"Pros & Cons - {self.company.ticker}"

class FinancialMetric(models.Model):
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='financial_metrics')
    year = models.SmallIntegerField()
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Debt to Equity Ratio")
    roe = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Return on Equity")
    roa = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Return on Assets")
    net_profit_margin = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Net Profit Margin")
    revenue_growth = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Revenue Growth Rate")
    profit_growth = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Profit Growth Rate")
    cash_conversion_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Cash Conversion Ratio")
    free_cash_flow = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Free Cash Flow")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'financial_metric'
        unique_together = ('company', 'year')
        indexes = [
            models.Index(fields=['company', 'year'], name='idx_fin_metric_company_year'),
        ]
        ordering = ['company', '-year']

    def __str__(self):
        return f"Metrics {self.company.ticker} ({self.year})"


class FinancialHealthScore(models.Model):
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='health_scores',
        verbose_name='Company'
    )
    year = models.SmallIntegerField(verbose_name='Fiscal Year')
    score = models.IntegerField(null=True, blank=True, verbose_name='Health Score')
    label = models.CharField(max_length=64, null=True, blank=True, verbose_name='Score Label')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        db_table = 'financial_health_score'
        verbose_name = 'Financial Health Score'
        verbose_name_plural = 'Financial Health Scores'
        unique_together = ('company', 'year')
        indexes = [
            models.Index(fields=['company', 'year'], name='idx_health_score_company_year'),
            models.Index(fields=['year'], name='idx_health_score_year'),
        ]
        ordering = ['company', '-year']

    def __str__(self):
        return f"HealthScore {self.company.ticker} ({self.year})"
