import logging
import pandas as pd
from django.db import transaction
from analytics.models import FinancialMetric


def compute_and_save_metrics(transformed_data, company_cache):
    """Compute financial metrics and persist them to PostgreSQL.

    Parameters
    ----------
    transformed_data: dict
        Dictionary containing transformed pandas DataFrames keyed by table name.
    company_cache: dict
        Mapping from ticker symbol to Company model instance.
    """
    logger = None  # optional placeholder for external logger if needed

    # Extract relevant dataframes
    df_pl = transformed_data.get('profit_and_loss')
    df_bs = transformed_data.get('balance_sheet')
    df_cf = transformed_data.get('cash_flow')

    if df_pl is None or df_bs is None or df_cf is None:
        return

    # Ensure year is integer
    df_pl['year'] = df_pl['year'].astype(int)
    df_bs['year'] = df_bs['year'].astype(int)
    df_cf['year'] = df_cf['year'].astype(int)

    # Compute year‑over‑year growth metrics using pandas groupby
    # Revenue Growth and Profit Growth require previous year values
    df_pl_sorted = df_pl.sort_values(['company_ticker', 'year'])
    df_pl_sorted['prev_sales'] = df_pl_sorted.groupby('company_ticker')['sales'].shift(1)
    df_pl_sorted['prev_net_profit'] = df_pl_sorted.groupby('company_ticker')['net_profit'].shift(1)

    # Merge all needed tables on company_ticker and year
    merged = pd.merge(df_pl_sorted, df_bs, how='left', left_on=['company_ticker', 'year'], right_on=['company_ticker', 'year'])
    merged = pd.merge(merged, df_cf, how='left', left_on=['company_ticker', 'year'], right_on=['company_ticker', 'year'])

    # Iterate over rows and persist metrics
    with transaction.atomic():
        for _, row in merged.iterrows():
            ticker = row['company_ticker']
            company = company_cache.get(ticker)
            if not company:
                continue
            year = int(row['year'])

            # Defensive: treat missing values as None
            equity = row.get('equity_capital')
            total_assets = row.get('total_assets')
            total_liabilities = row.get('total_liabilities')
            net_profit = row.get('net_profit')
            sales = row.get('sales')
            operating_activity = row.get('operating_activity')
            net_cash_flow = row.get('net_cash_flow')
            interest = row.get('interest')

            # Compute ratios, guarding division by zero
            def safe_div(num, denom):
                try:
                    if pd.isna(num) or pd.isna(denom) or denom == 0:
                        return None
                    return float(num) / float(denom)
                except Exception:
                    return None

            debt_to_equity = safe_div(total_liabilities, equity)
            roe = safe_div(net_profit, equity)
            roa = safe_div(net_profit, total_assets)
            net_profit_margin = safe_div(net_profit, sales)
            revenue_growth = safe_div(sales - row.get('prev_sales'), row.get('prev_sales'))
            profit_growth = safe_div(net_profit - row.get('prev_net_profit'), row.get('prev_net_profit'))
            cash_conversion_ratio = safe_div(operating_activity, net_profit)
            free_cash_flow = None if pd.isna(net_cash_flow) else net_cash_flow  # simple definition; can be adjusted

            defaults = {
                'debt_to_equity': debt_to_equity,
                'roe': roe,
                'roa': roa,
                'net_profit_margin': net_profit_margin,
                'revenue_growth': revenue_growth,
                'profit_growth': profit_growth,
                'cash_conversion_ratio': cash_conversion_ratio,
                'free_cash_flow': free_cash_flow,
            }

            FinancialMetric.objects.update_or_create(
                company=company,
                year=year,
                defaults=defaults,
            )
