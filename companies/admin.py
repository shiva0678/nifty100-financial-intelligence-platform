from django.contrib import admin
from .models import Company, BalanceSheet, ProfitAndLoss, CashFlow, Document

class BalanceSheetInline(admin.TabularInline):
    model = BalanceSheet
    extra = 0
    ordering = ('-year',)

class ProfitAndLossInline(admin.TabularInline):
    model = ProfitAndLoss
    extra = 0
    ordering = ('-year',)

class CashFlowInline(admin.TabularInline):
    model = CashFlow
    extra = 0
    ordering = ('-year',)

class DocumentInline(admin.StackedInline):
    model = Document
    extra = 0
    ordering = ('-year',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'company_name', 'website', 'face_value', 'roce_percentage', 'roe_percentage', 'created_at')
    search_fields = ('ticker', 'company_name', 'about_company')
    list_filter = ('created_at', 'face_value')
    inlines = [BalanceSheetInline, ProfitAndLossInline, CashFlowInline, DocumentInline]
    fieldsets = (
        ('Master Metadata', {
            'fields': ('ticker', 'company_name', 'company_logo', 'chart_link')
        }),
        ('Company Profile & Operations', {
            'fields': ('about_company', 'website', 'nse_profile', 'bse_profile')
        }),
        ('Core Valuations & Ratios', {
            'fields': ('face_value', 'book_value', 'roce_percentage', 'roe_percentage')
        }),
    )

@admin.register(BalanceSheet)
class BalanceSheetAdmin(admin.ModelAdmin):
    list_display = ('company', 'year', 'total_assets', 'total_liabilities', 'equity_capital', 'reserves', 'created_at')
    search_fields = ('company__company_name', 'company__ticker', 'year')
    list_filter = ('year', 'company')
    ordering = ('company', '-year')

@admin.register(ProfitAndLoss)
class ProfitAndLossAdmin(admin.ModelAdmin):
    list_display = ('company', 'year', 'sales', 'operating_profit', 'net_profit', 'eps', 'opm_percentage', 'created_at')
    search_fields = ('company__company_name', 'company__ticker', 'year')
    list_filter = ('year', 'company')
    ordering = ('company', '-year')

@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ('company', 'year', 'operating_activity', 'investing_activity', 'financing_activity', 'net_cash_flow', 'created_at')
    search_fields = ('company__company_name', 'company__ticker', 'year')
    list_filter = ('year', 'company')
    ordering = ('company', '-year')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('company', 'year', 'created_at')
    search_fields = ('company__company_name', 'company__ticker', 'year', 'annual_report')
    list_filter = ('year', 'company')
    ordering = ('company', '-year')
