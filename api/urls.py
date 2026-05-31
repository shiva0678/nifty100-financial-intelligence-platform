"""
api/urls.py
URL configuration for the Nifty 100 Financial REST API.

All routes are prefixed with /api/ via the root urls.py include.
"""
from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    # List all companies (paginated)
    path("companies/", views.companies_list, name="companies-list"),

    # Full profile for a single company
    path("company/<str:symbol>/", views.company_detail, name="company-detail"),

    # Per-year financial metrics (D/E, ROE, ROA, margins, FCF …)
    path("company/<str:symbol>/metrics/", views.company_metrics, name="company-metrics"),

    # Health score history (0-100 + label)
    path("company/<str:symbol>/score/", views.company_score, name="company-score"),

    # Insights (pros/cons) — stored or computed on-demand
    path("company/<str:symbol>/insights/", views.company_insights, name="company-insights"),

    # Top N companies by net profit
    path("top-companies/", views.top_companies, name="top-companies"),

    # Sector groupings (placeholder – extend when sector field added)
    path("sectors/", views.sectors, name="sectors"),

    # Fuzzy search by ticker or company name
    path("search/", views.search, name="search"),
]
