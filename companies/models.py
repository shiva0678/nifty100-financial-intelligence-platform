from django.db import models

class Company(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    ticker = models.CharField(max_length=20, unique=True, verbose_name="Ticker Symbol")
    company_name = models.CharField(max_length=256, unique=True, verbose_name="Company Name")
    company_logo = models.CharField(max_length=512, null=True, blank=True, verbose_name="Logo URL")
    chart_link = models.CharField(max_length=512, null=True, blank=True, verbose_name="Chart Link")
    about_company = models.TextField(null=True, blank=True, verbose_name="About Company")
    website = models.CharField(max_length=256, null=True, blank=True, verbose_name="Website")
    nse_profile = models.CharField(max_length=512, null=True, blank=True, verbose_name="NSE Profile")
    bse_profile = models.CharField(max_length=512, null=True, blank=True, verbose_name="BSE Profile")
    face_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Face Value")
    book_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Book Value")
    roce_percentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="ROCE %")
    roe_percentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="ROE %")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'company'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['company_name']
        indexes = [
            models.Index(fields=['company_name'], name='idx_django_company_name'),
            models.Index(fields=['website'], name='idx_django_company_website'),
        ]

    def __str__(self):
        return f"{self.company_name} ({self.ticker})"


class BalanceSheet(models.Model):
    balance_sheet_id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='balance_sheets', verbose_name="Company")
    year = models.SmallIntegerField(verbose_name="Fiscal Year")
    equity_capital = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Equity Capital")
    reserves = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Reserves & Surplus")
    borrowings = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Borrowings")
    other_liabilities = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Other Liabilities")
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Total Liabilities")
    fixed_assets = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Fixed Assets")
    cwip = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Capital Work-In-Progress")
    investments = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Investments")
    other_assets = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Other Assets")
    total_assets = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Total Assets")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'balance_sheet'
        verbose_name = 'Balance Sheet'
        verbose_name_plural = 'Balance Sheets'
        unique_together = ('company', 'year')
        ordering = ['company', '-year']
        indexes = [
            models.Index(fields=['year'], name='idx_django_bs_year'),
            models.Index(fields=['total_assets'], name='idx_django_bs_total_assets'),
        ]

    def __str__(self):
        return f"{self.company.ticker} - FY{self.year} Balance Sheet"


class ProfitAndLoss(models.Model):
    profit_and_loss_id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='profit_and_losses', verbose_name="Company")
    year = models.SmallIntegerField(verbose_name="Fiscal Year")
    sales = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Sales/Revenue")
    expenses = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Operating Expenses")
    operating_profit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Operating Profit (EBIT)")
    opm_percentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="OPM %")
    other_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Other Income")
    interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Interest Expense")
    depreciation = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Depreciation")
    profit_before_tax = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Profit Before Tax (PBT)")
    tax_percentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Effective Tax %")
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Net Profit (PAT)")
    eps = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, verbose_name="Earnings Per Share (EPS)")
    dividend_payout = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Dividend Payout")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'profit_and_loss'
        verbose_name = 'Profit & Loss Statement'
        verbose_name_plural = 'Profit & Loss Statements'
        unique_together = ('company', 'year')
        ordering = ['company', '-year']
        indexes = [
            models.Index(fields=['year'], name='idx_django_pl_year'),
            models.Index(fields=['net_profit'], name='idx_django_pl_net_profit'),
            models.Index(fields=['eps'], name='idx_django_pl_eps'),
        ]

    def __str__(self):
        return f"{self.company.ticker} - FY{self.year} P&L"


class CashFlow(models.Model):
    cash_flow_id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cash_flows', verbose_name="Company")
    year = models.SmallIntegerField(verbose_name="Fiscal Year")
    operating_activity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Cash from Operations")
    investing_activity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Cash from Investing")
    financing_activity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Cash from Financing")
    net_cash_flow = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Net Cash Flow")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'cash_flow'
        verbose_name = 'Cash Flow Statement'
        verbose_name_plural = 'Cash Flow Statements'
        unique_together = ('company', 'year')
        ordering = ['company', '-year']
        indexes = [
            models.Index(fields=['year'], name='idx_django_cf_year'),
            models.Index(fields=['operating_activity'], name='idx_django_cf_ops_cash'),
        ]

    def __str__(self):
        return f"{self.company.ticker} - FY{self.year} Cash Flow"


class Document(models.Model):
    document_id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='documents', verbose_name="Company")
    year = models.SmallIntegerField(null=True, blank=True, verbose_name="Fiscal Year")
    annual_report = models.TextField(null=True, blank=True, verbose_name="Annual Report Text/URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'document'
        verbose_name = 'Supporting Document'
        verbose_name_plural = 'Supporting Documents'
        ordering = ['company', '-year']
        indexes = [
            models.Index(fields=['year'], name='idx_django_doc_year'),
            models.Index(fields=['company', 'year'], name='idx_django_doc_company_year'),
        ]

    def __str__(self):
        return f"{self.company.ticker} - {f'FY{self.year} ' if self.year else ''}Document ({self.document_id})"
