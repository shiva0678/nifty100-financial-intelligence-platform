import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Locate project files
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

def load_env_credentials():
    """Manually parse .env to get Postgres connection credentials, as django is not booted yet."""
    env_path = os.path.join(PROJECT_ROOT, '.env')
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Configuration file .env not found at {env_path}")
        
    creds = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            creds[key.strip()] = val.strip()
            
    return {
        'dbname': creds.get('DB_NAME', 'nifty_100_db'),
        'user': creds.get('DB_USER', 'postgres'),
        'password': creds.get('DB_PASSWORD', 'postgres'),
        'host': creds.get('DB_HOST', 'localhost'),
        'port': creds.get('DB_PORT', '5432')
    }

def ensure_database_exists(creds):
    """Connects to default 'postgres' database and creates DB if missing."""
    logger.info("Checking database existence...")
    
    # Establish connection to system 'postgres' DB
    conn = psycopg2.connect(
        dbname='postgres',
        user=creds['user'],
        password=creds['password'],
        host=creds['host'],
        port=creds['port']
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{creds['dbname']}'")
        exists = cur.fetchone()
        if not exists:
            logger.info(f"Database '{creds['dbname']}' not found. Creating database...")
            cur.execute(f'CREATE DATABASE "{creds["dbname"]}" WITH ENCODING="UTF8";')
            logger.info(f"Database '{creds['dbname']}' created successfully.")
        else:
            logger.info(f"Database '{creds['dbname']}' already exists.")
    except Exception as e:
        logger.error(f"Error checking/creating database: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

def ensure_schema_exists(creds):
    """Ensures the application schema exists before Django migrations run."""
    logger.info(f"Ensuring schema 'nifty_100' exists in database '{creds['dbname']}'...")
    conn = psycopg2.connect(
        dbname=creds['dbname'],
        user=creds['user'],
        password=creds['password'],
        host=creds['host'],
        port=creds['port']
    )
    cur = conn.cursor()
    try:
        cur.execute('CREATE SCHEMA IF NOT EXISTS nifty_100;')
        conn.commit()
        logger.info("Schema 'nifty_100' exists or was created successfully.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error ensuring schema exists: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

def run_django_migrations():
    """Runs Django migrate command to set up built-in auth, session, and admin tables."""
    logger.info("Running Django standard migrations to set up core framework tables...")
    manage_py = os.path.join(PROJECT_ROOT, 'manage.py')
    try:
        result = subprocess.run(
            [sys.executable, manage_py, 'migrate'],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Django migrations executed successfully.")
        logger.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Django migrations: {e.stderr}")
        raise e

def initialize():
    logger.info("==================================================")
    logger.info("INITIALIZING DATABASE AND SCHEMA SETUP")
    logger.info("==================================================")
    try:
        # 1. Load credentials
        creds = load_env_credentials()
        
        # 2. Ensure DB exists
        ensure_database_exists(creds)
        
        # 3. Ensure the application schema exists before applying migrations
        ensure_schema_exists(creds)
        
        # 4. Create Django system tables and app tables via migrate
        run_django_migrations()
        
        logger.info("==================================================")
        logger.info("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
        logger.info("==================================================")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    initialize()
