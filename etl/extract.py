import os
import pandas as pd
import logging

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Expected file names in the workspace root
FILE_NAMES = {
    'companies': 'companies.xlsx',
    'balance_sheet': 'balancesheet.xlsx',
    'profit_and_loss': 'profitandloss.xlsx',
    'cash_flow': 'cashflow.xlsx',
    'analysis': 'analysis.xlsx',
    'pros_cons': 'prosandcons.xlsx',
    'documents': 'documents.xlsx',
}

def extract_file(file_path, sheet_name=None):
    """
    Extracts a single Excel file using pandas.
    Uses skiprows=1 because the source spreadsheets contain a title/branding row in row 0.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")
    
    logger.info(f"Extracting {os.path.basename(file_path)}...")
    try:
        # Load the sheet using pandas
        # skiprows=1 skips the title banner row so headers are parsed correctly from row 1
        df = pd.read_excel(file_path, skiprows=1)
        
        # Strip whitespaces from column headers
        df.columns = [str(col).strip() for col in df.columns]
        
        logger.info(f"Successfully extracted {os.path.basename(file_path)}: Shape = {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error extracting {os.path.basename(file_path)}: {str(e)}")
        raise e

def extract_all(data_dir=None):
    """
    Extracts all 7 required Excel files from the data directory.
    Returns a dictionary of raw pandas DataFrames.
    """
    if data_dir is None:
        # Default to the workspace directory which is the parent of this etl folder
        data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    logger.info(f"Starting data extraction from directory: {data_dir}")
    raw_data = {}
    
    for key, file_name in FILE_NAMES.items():
        file_path = os.path.join(data_dir, file_name)
        try:
            raw_data[key] = extract_file(file_path)
        except Exception as e:
            logger.error(f"Failed extraction sequence on: {file_name}. Error: {str(e)}")
            raise e
            
    logger.info("Extraction phase completed successfully.")
    return raw_data

if __name__ == '__main__':
    # Local standalone extraction check
    try:
        data = extract_all()
        for k, v in data.items():
            print(f"File key: {k:<15s} | Row Count: {len(v):<5d} | Columns: {v.columns.tolist()[:3]}...")
    except Exception as ex:
        print(f"Extraction failed: {ex}")
