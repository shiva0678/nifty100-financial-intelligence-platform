import pandas as pd
import re
import logging

logger = logging.getLogger(__name__)

def clean_string(val):
    """Strips whitespace and normalizes string values; maps empty strings/NaNs to None."""
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    return val_str if val_str != "" else None

def clean_decimal(val):
    """Converts a value to float for numeric storage; maps NaNs/invalids to None."""
    if pd.isna(val):
        return None
    try:
        # Strip currency symbols or commas if present
        clean_val = str(val).replace(',', '').replace('$', '').replace('₹', '').strip()
        return float(clean_val)
    except (ValueError, TypeError):
        return None

def clean_year(val):
    """Parses year formats into integer years (e.g. 'Dec 2012' -> 2012, 'Mar-13' -> 2013, 2024.0 -> 2024)."""
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    if not val_str:
        return None
    
    # 1. Try to extract a 4-digit year (1990-2099)
    match_4digit = re.search(r'\b(19\d{2}|20\d{2})\b', val_str)
    if match_4digit:
        return int(match_4digit.group(1))
        
    # 2. Try to extract a 2-digit year from formats like 'Mar-13', 'Mar/13'
    match_2digit = re.search(r'[-/ ](\d{2})$', val_str)
    if match_2digit:
        year_2d = int(match_2digit.group(1))
        # If year is < 50, assume 20xx, otherwise 19xx
        year_4d = 2000 + year_2d if year_2d < 50 else 1900 + year_2d
        return year_4d
        
    # 3. Fallback: direct numerical parse
    try:
        year_float = float(val_str)
        year_int = int(year_float)
        if 1990 <= year_int <= 2100:
            return year_int
    except (ValueError, TypeError):
        pass
        
    return None


def transform_companies(df):
    """Cleans and transforms companies dataframe."""
    logger.info("Transforming Companies data...")
    df_clean = df.copy()
    
    # Map headers correctly (skiprows handles this, but let's be explicitly defensive)
    # id in Excel represents the natural ticker key
    df_clean['ticker'] = df_clean['id'].apply(clean_string)
    df_clean['company_name'] = df_clean['company_name'].apply(clean_string)
    
    # Normalize company names (e.g., standardizing casing, collapsing double spaces)
    df_clean['company_name'] = df_clean['company_name'].apply(
        lambda name: " ".join(name.split()) if name else None
    )
    
    df_clean['company_logo'] = df_clean['company_logo'].apply(clean_string)
    df_clean['chart_link'] = df_clean['chart_link'].apply(clean_string)
    df_clean['about_company'] = df_clean['about_company'].apply(clean_string)
    df_clean['website'] = df_clean['website'].apply(clean_string)
    df_clean['nse_profile'] = df_clean['nse_profile'].apply(clean_string)
    df_clean['bse_profile'] = df_clean['bse_profile'].apply(clean_string)
    
    df_clean['face_value'] = df_clean['face_value'].apply(clean_decimal)
    df_clean['book_value'] = df_clean['book_value'].apply(clean_decimal)
    df_clean['roce_percentage'] = df_clean['roce_percentage'].apply(clean_decimal)
    df_clean['roe_percentage'] = df_clean['roe_percentage'].apply(clean_decimal)
    
    # Drop rows where ticker or company_name is missing
    df_clean = df_clean.dropna(subset=['ticker', 'company_name'])
    
    logger.info(f"Companies transformation complete. Rows preserved: {len(df_clean)}")
    return df_clean

def transform_balance_sheet(df):
    """Cleans, transforms, and calculates derived metrics for Balance Sheet."""
    logger.info("Transforming Balance Sheet data...")
    df_clean = df.copy()
    
    # Ticker links
    df_clean['company_ticker'] = df_clean['company_id'].apply(clean_string)
    df_clean['year'] = df_clean['year'].apply(clean_year)
    
    # Normalize header variants for the same logical field
    if 'other_asset' in df_clean.columns and 'other_assets' not in df_clean.columns:
        df_clean = df_clean.rename(columns={'other_asset': 'other_assets'})

    # Numeric fields
    fields = [
        'equity_capital', 'reserves', 'borrowings', 'other_liabilities',
        'total_liabilities', 'fixed_assets', 'cwip', 'investments',
        'other_assets', 'total_assets'
    ]
    for col in fields:
        df_clean[col] = df_clean[col].apply(clean_decimal)
    
    # Clean zeros and handle missing totals (Derived Metrics)
    for idx, row in df_clean.iterrows():
        # Ensure non-negative/None defaults for subcategories
        fixed = row['fixed_assets'] or 0.0
        cwip_val = row['cwip'] or 0.0
        inv = row['investments'] or 0.0
        oth_ast = row['other_assets'] or 0.0
        
        # Derived Metric 1: Recalculate total_assets if NaN/missing
        if pd.isna(row['total_assets']) or row['total_assets'] == 0.0:
            df_clean.at[idx, 'total_assets'] = fixed + cwip_val + inv + oth_ast
            
        eq = row['equity_capital'] or 0.0
        res = row['reserves'] or 0.0
        borrow = row['borrowings'] or 0.0
        oth_liab = row['other_liabilities'] or 0.0
        
        # Derived Metric 2: Recalculate total_liabilities if NaN/missing
        if pd.isna(row['total_liabilities']) or row['total_liabilities'] == 0.0:
            df_clean.at[idx, 'total_liabilities'] = eq + res + borrow + oth_liab

    # Filter out records missing vital join relationships
    df_clean = df_clean.dropna(subset=['company_ticker', 'year'])
    logger.info(f"Balance Sheet transformation complete. Rows preserved: {len(df_clean)}")
    return df_clean

def transform_profit_and_loss(df):
    """Cleans, transforms, and calculates derived metrics for Profit & Loss."""
    logger.info("Transforming Profit & Loss data...")
    df_clean = df.copy()
    
    df_clean['company_ticker'] = df_clean['company_id'].apply(clean_string)
    df_clean['year'] = df_clean['year'].apply(clean_year)
    
    numeric_fields = [
        'sales', 'expenses', 'operating_profit', 'opm_percentage',
        'other_income', 'interest', 'depreciation', 'profit_before_tax',
        'tax_percentage', 'net_profit', 'eps', 'dividend_payout'
    ]
    for col in numeric_fields:
        df_clean[col] = df_clean[col].apply(clean_decimal)
        
    # Derived Metrics for Profit and Loss
    for idx, row in df_clean.iterrows():
        sales_val = row['sales'] or 0.0
        expenses_val = row['expenses'] or 0.0
        
        # Derived Metric 1: Operating Profit = Sales - Expenses
        op_prof = row['operating_profit']
        if pd.isna(op_prof) or op_prof == 0.0:
            op_prof = sales_val - expenses_val
            df_clean.at[idx, 'operating_profit'] = op_prof
            
        # Derived Metric 2: Operating Profit Margin (OPM %) = (Operating Profit / Sales) * 100
        if pd.isna(row['opm_percentage']) or row['opm_percentage'] == 0.0:
            if sales_val > 0.0:
                df_clean.at[idx, 'opm_percentage'] = round((op_prof / sales_val) * 100, 2)
            else:
                df_clean.at[idx, 'opm_percentage'] = 0.0
                
        # Derived Metric 3: Net Profit Margin (NPM %)
        # Logged for analytical insight (not loaded to DB since NPM is not a DB column)
        
    df_clean = df_clean.dropna(subset=['company_ticker', 'year'])
    logger.info(f"Profit & Loss transformation complete. Rows preserved: {len(df_clean)}")
    return df_clean

def transform_cash_flow(df):
    """Cleans and transforms Cash Flow data."""
    logger.info("Transforming Cash Flow data...")
    df_clean = df.copy()
    
    df_clean['company_ticker'] = df_clean['company_id'].apply(clean_string)
    df_clean['year'] = df_clean['year'].apply(clean_year)
    
    fields = ['operating_activity', 'investing_activity', 'financing_activity', 'net_cash_flow']
    for col in fields:
        df_clean[col] = df_clean[col].apply(clean_decimal)
        
    # Derived Metric: Net Cash Flow = Ops + Inv + Fin
    for idx, row in df_clean.iterrows():
        if pd.isna(row['net_cash_flow']):
            ops = row['operating_activity'] or 0.0
            inv = row['investing_activity'] or 0.0
            fin = row['financing_activity'] or 0.0
            df_clean.at[idx, 'net_cash_flow'] = ops + inv + fin
            
    df_clean = df_clean.dropna(subset=['company_ticker', 'year'])
    logger.info(f"Cash Flow transformation complete. Rows preserved: {len(df_clean)}")
    return df_clean

def transform_analysis(df):
    """Cleans and transforms Analysis data."""
    logger.info("Transforming Analysis data...")
    df_clean = df.copy()
    
    df_clean['company_ticker'] = df_clean['company_id'].apply(clean_string)
    df_clean['compounded_sales_growth'] = df_clean['compounded_sales_growth'].apply(clean_decimal)
    df_clean['compounded_profit_growth'] = df_clean['compounded_profit_growth'].apply(clean_decimal)
    df_clean['stock_price_cagr'] = df_clean['stock_price_cagr'].apply(clean_decimal)
    
    # Rename column 'roe' to 'roe_percentage' to match normalized schema and model
    df_clean = df_clean.rename(columns={'roe': 'roe_percentage'})
    df_clean['roe_percentage'] = df_clean['roe_percentage'].apply(clean_decimal)
    
    df_clean = df_clean.dropna(subset=['company_ticker'])
    logger.info(f"Analysis transformation complete. Rows preserved: {len(df_clean)}")
    return df_clean

def transform_documents(df):
    """Cleans and transforms Documents data."""
    logger.info("Transforming Documents data...")
    df_clean = df.copy()
    
    df_clean['company_ticker'] = df_clean['company_id'].apply(clean_string)
    
    # In raw documents, year column has capitalized 'Year'
    # In some pandas loads, headers are case sensitive
    year_col = 'Year' if 'Year' in df_clean.columns else 'year'
    df_clean['year'] = df_clean[year_col].apply(clean_year)
    
    report_col = 'Annual_Report' if 'Annual_Report' in df_clean.columns else 'annual_report'
    df_clean['annual_report'] = df_clean[report_col].apply(clean_string)
    
    df_clean = df_clean.dropna(subset=['company_ticker'])
    logger.info(f"Documents transformation complete. Rows preserved: {len(df_clean)}")
    return df_clean

def transform_pros_cons(df):
    """Cleans and transforms Pros and Cons data."""
    logger.info("Transforming Pros and Cons data...")
    df_clean = df.copy()
    
    df_clean['company_ticker'] = df_clean['company_id'].apply(clean_string)
    df_clean['pros'] = df_clean['pros'].apply(clean_string)
    df_clean['cons'] = df_clean['cons'].apply(clean_string)
    
    df_clean = df_clean.dropna(subset=['company_ticker'])
    logger.info(f"Pros & Cons transformation complete. Rows preserved: {len(df_clean)}")
    return df_clean

def transform_all(raw_data):
    """
    Orchestrates the transformation of all 7 raw DataFrames.
    Returns a dictionary of cleaned DataFrames ready for loading.
    """
    logger.info("Starting data transformation pipeline...")
    transformed_data = {
        'companies': transform_companies(raw_data['companies']),
        'balance_sheet': transform_balance_sheet(raw_data['balance_sheet']),
        'profit_and_loss': transform_profit_and_loss(raw_data['profit_and_loss']),
        'cash_flow': transform_cash_flow(raw_data['cash_flow']),
        'analysis': transform_analysis(raw_data['analysis']),
        'documents': transform_documents(raw_data['documents']),
        'pros_cons': transform_pros_cons(raw_data['pros_cons']),
    }
    logger.info("Transformation pipeline completed successfully.")
    return transformed_data
