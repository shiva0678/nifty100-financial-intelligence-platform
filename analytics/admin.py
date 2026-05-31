from django.contrib import admin
from .models import Analysis, ProsCons

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'company',
        'compounded_sales_growth',
        'compounded_profit_growth',
        'stock_price_cagr',
        'roe_percentage',
        'created_at',
        'updated_at'
    )
    search_fields = ('company__company_name', 'company__ticker')
    list_filter = ('created_at', 'updated_at')
    ordering = ('company',)

@admin.register(ProsCons)
class ProsConsAdmin(admin.ModelAdmin):
    list_display = ('company', 'created_at', 'updated_at')
    search_fields = ('company__company_name', 'company__ticker', 'pros', 'cons')
    list_filter = ('created_at', 'updated_at')
    ordering = ('company',)
