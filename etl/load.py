import os
import sys
import django
import logging
import pandas as pd

# Make project root available for top-level Django app imports before importing analytics modules.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Initialize Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nifty_finance.settings")

# Setup Django (initializes models, apps, and database routing configurations)
django.setup()

# Import financial metrics and AI insight engines after Django is configured
try:
    from .metrics_engine import compute_and_save_metrics
    from .health_score import compute_and_save_health_scores
except ImportError:
    from metrics_engine import compute_and_save_metrics
    from health_score import compute_and_save_health_scores
from analytics.insights import compute_and_save_insights

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Django Models after django.setup()
from companies.models import Company, BalanceSheet, ProfitAndLoss, CashFlow, Document
from analytics.models import Analysis, ProsCons
from django.db import transaction

def load_companies(df_companies):
    """Loads transformed companies into the PostgreSQL database using Django's ORM."""
    logger.info("Loading Companies data (Dimension table)...")
    company_cache = {}
    
    # Define numeric fields that may contain NaN and should be stored as NULL
    numeric_fields = ['face_value', 'book_value', 'roce_percentage', 'roe_percentage']
    
    with transaction.atomic():
        for _, row in df_companies.iterrows():
            ticker = row['ticker']
            
            # Clean numeric fields: convert NaN to None
            cleaned_data = {
                field: (None if pd.isna(row[field]) else row[field])
                for field in numeric_fields
            }
            
            defaults = {
                'company_name': row['company_name'],
                'company_logo': row['company_logo'],
                'chart_link': row['chart_link'],
                'about_company': row['about_company'],
                'website': row['website'],
                'nse_profile': row['nse_profile'],
                'bse_profile': row['bse_profile'],
                **cleaned_data
            }
            
            company_obj, created = Company.objects.update_or_create(
                ticker=ticker,
                defaults=defaults
            )
            company_cache[ticker] = company_obj
    
    logger.info(f"Loaded {len(company_cache)} companies successfully.")
    return company_cache

def load_balance_sheets(df_bs, company_cache):
    """Loads Balance Sheet facts using company cache for relational joins."""
    logger.info("Loading Balance Sheet records (Fact table)...")
    records_loaded = 0
    skipped_records = 0
    
    with transaction.atomic():
        for _, row in df_bs.iterrows():
            ticker = row['company_ticker']
            company_obj = company_cache.get(ticker)
            
            if not company_obj:
                # Defensive check: if the company ticker is missing from dimension table, skip it
                skipped_records += 1
                continue
                
            numeric_fields = ['equity_capital', 'reserves', 'borrowings', 'other_liabilities', 'total_liabilities', 'fixed_assets', 'cwip', 'investments', 'other_assets', 'total_assets']
            cleaned_data = {}
            for field in numeric_fields:
                value = row[field]
                if pd.isna(value) or value < 0:
                    cleaned_data[field] = None
                else:
                    cleaned_data[field] = value
            defaults = {
                **cleaned_data,
                'company': company_obj,
                'year': row['year']
            }
            BalanceSheet.objects.update_or_create(
                company=company_obj,
                year=row['year'],
                defaults=defaults
            )
            records_loaded += 1
            
    logger.info(f"Balance Sheets loaded: {records_loaded}. Skipped: {skipped_records}")

def load_profit_and_losses(df_pl, company_cache):
    """Loads Profit & Loss statements using company cache."""
    logger.info("Loading Profit & Loss records (Fact table)...")
    records_loaded = 0
    skipped_records = 0
    
    with transaction.atomic():
        for _, row in df_pl.iterrows():
            ticker = row['company_ticker']
            company_obj = company_cache.get(ticker)
            
            if not company_obj:
                skipped_records += 1
                continue
                
            numeric_fields = ['sales', 'expenses', 'operating_profit', 'opm_percentage', 'other_income', 'interest', 'depreciation', 'profit_before_tax', 'tax_percentage', 'net_profit', 'eps', 'dividend_payout']
            cleaned_data = {}
            for field in numeric_fields:
                value = row[field]
                if pd.isna(value):
                    cleaned_data[field] = None
                elif field in ['sales', 'expenses', 'interest', 'depreciation', 'dividend_payout'] and value < 0:
                    cleaned_data[field] = abs(value)
                else:
                    cleaned_data[field] = value
            defaults = {
                **cleaned_data,
                'company': company_obj,
                'year': row['year']
            }
            ProfitAndLoss.objects.update_or_create(
                company=company_obj,
                year=row['year'],
                defaults=defaults
            )
            records_loaded += 1
            
    logger.info(f"Profit & Losses loaded: {records_loaded}. Skipped: {skipped_records}")

def load_cash_flows(df_cf, company_cache):
    """Loads Cash Flow facts using company cache."""
    logger.info("Loading Cash Flow records (Fact table)...")
    records_loaded = 0
    skipped_records = 0
    
    with transaction.atomic():
        for _, row in df_cf.iterrows():
            ticker = row['company_ticker']
            company_obj = company_cache.get(ticker)
            
            if not company_obj:
                skipped_records += 1
                continue
                
            numeric_fields = ['operating_activity', 'investing_activity', 'financing_activity', 'net_cash_flow']
            cleaned_data = {}
            for field in numeric_fields:
                value = row[field]
                cleaned_data[field] = None if pd.isna(value) else value
            defaults = {
                **cleaned_data,
                'company': company_obj,
                'year': row['year']
            }
            CashFlow.objects.update_or_create(
                company=company_obj,
                year=row['year'],
                defaults=defaults
            )
            records_loaded += 1
            
    logger.info(f"Cash Flows loaded: {records_loaded}. Skipped: {skipped_records}")

def load_analyses(df_analysis, company_cache):
    """Loads Growth Analyses (OneToOne model) using company cache."""
    logger.info("Loading Analysis records (1-to-1 extension table)...")
    records_loaded = 0
    skipped_records = 0
    
    with transaction.atomic():
        for _, row in df_analysis.iterrows():
            ticker = row['company_ticker']
            company_obj = company_cache.get(ticker)
            
            if not company_obj:
                skipped_records += 1
                continue
                
            Analysis.objects.update_or_create(
                company=company_obj,
                defaults={
                    'compounded_sales_growth': row['compounded_sales_growth'],
                    'compounded_profit_growth': row['compounded_profit_growth'],
                    'stock_price_cagr': row['stock_price_cagr'],
                    'roe_percentage': row['roe_percentage'],
                }
            )
            records_loaded += 1
            
    logger.info(f"Analyses loaded: {records_loaded}. Skipped: {skipped_records}")

def load_documents(df_docs, company_cache):
    """Loads Supporting Documents using company cache."""
    logger.info("Loading Documents (Reference table)...")
    records_loaded = 0
    skipped_records = 0
    
    with transaction.atomic():
        for _, row in df_docs.iterrows():
            ticker = row['company_ticker']
            company_obj = company_cache.get(ticker)
            
            if not company_obj:
                skipped_records += 1
                continue
                
            # Documents do not have a unique constraint, but we update or create based on unique 
            # combination to prevent double loading the exact same document link.
            Document.objects.update_or_create(
                company=company_obj,
                year=row['year'],
                annual_report=row['annual_report'],
                defaults={} # Insert only if it doesn't exist
            )
            records_loaded += 1
            
    logger.info(f"Documents loaded: {records_loaded}. Skipped: {skipped_records}")

def load_pros_cons(df_pc, company_cache):
    """Loads Pros & Cons Profiles (OneToOne model) using company cache."""
    logger.info("Loading Pros & Cons (1-to-1 extension table)...")
    records_loaded = 0
    skipped_records = 0
    
    with transaction.atomic():
        for _, row in df_pc.iterrows():
            ticker = row['company_ticker']
            company_obj = company_cache.get(ticker)
            
            if not company_obj:
                skipped_records += 1
                continue
                
            ProsCons.objects.update_or_create(
                company=company_obj,
                defaults={
                    'pros': row['pros'],
                    'cons': row['cons'],
                }
            )
            records_loaded += 1
            
    logger.info(f"Pros & Cons loaded: {records_loaded}. Skipped: {skipped_records}")

def load_all(transformed_data):
    """
    Executes the load phase of the ETL pipeline.
    Ensures dimension entities (Company) load first, caching them
    to resolve relational integrity joins for fact/detail records.
    """
    logger.info("Starting database load process inside atomic transactions...")
    
    # 1. Load Dimension table first and retrieve the ticker-to-Company DB object cache
    company_cache = load_companies(transformed_data['companies'])
    
    if not company_cache:
        logger.error("No companies loaded. Aborting load pipeline to prevent database crashes.")
        return
        
    # 2. Load Fact tables
    load_balance_sheets(transformed_data['balance_sheet'], company_cache)
    load_profit_and_losses(transformed_data['profit_and_loss'], company_cache)
    load_cash_flows(transformed_data['cash_flow'], company_cache)
    
    # 3. Load One-to-One and Reference tables
    load_analyses(transformed_data['analysis'], company_cache)
    load_documents(transformed_data['documents'], company_cache)
    load_pros_cons(transformed_data['pros_cons'], company_cache)

    # 4. Compute financial metrics and save to DB
    compute_and_save_metrics(transformed_data, company_cache)

    # 5. Generate financial health scores based on computed metrics
    compute_and_save_health_scores()

    # 6. Generate and store AI-driven pros/cons insights if no manual profile exists
    compute_and_save_insights()

    logger.info("Database load pipeline completed successfully.")
