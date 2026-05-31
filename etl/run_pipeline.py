import logging
import os
import sys

# Make project root available for top-level app imports when executed as a script.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    # Preferred package-style imports when etl is executed as a module
    from .extract import extract_all
    from .transform import transform_all
    from .load import load_all
except ImportError:
    # Fallback for direct script execution from the etl directory
    from extract import extract_all
    from transform import transform_all
    from load import load_all

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_etl():
    logger.info("==================================================")
    logger.info("STARTING NIFTY 100 FINANCIAL ETL PIPELINE")
    logger.info("==================================================")
    try:
        # 1. Extract raw Excel structures
        raw_data = extract_all()
        
        # 2. Perform transformations, cleanings, and derived metrics calculations
        cleaned_data = transform_all(raw_data)
        
        # 3. Load cleanly mapped records into PostgreSQL via Django ORM transactions
        load_all(cleaned_data)
        
        logger.info("==================================================")
        logger.info("ETL PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        logger.info("==================================================")
    except Exception as e:
        logger.error(f"ETL Pipeline execution crashed: {e}", exc_info=True)

if __name__ == '__main__':
    run_etl()
