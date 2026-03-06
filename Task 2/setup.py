import psycopg
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Fix for Windows psycopg3 async
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Database connection parameters
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'call_records_db')

def setup_database():
    """Create database and run schema."""
    
    # Connect to default postgres database
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}...")
    conn = psycopg.connect(
        f"host={DB_HOST} port={DB_PORT} dbname=postgres user={DB_USER} password={DB_PASSWORD}",
        autocommit=True
    )
    
    # Create database
    print(f"Creating database '{DB_NAME}'...")
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cur.execute(f"CREATE DATABASE {DB_NAME}")
    conn.close()
    print(f"Database '{DB_NAME}' created successfully!")
    
    # Connect to new database and run schema
    print("Running schema...")
    conn = psycopg.connect(
        f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    )
    
    with open('sql/schema.sql', 'r') as f:
        schema_sql = f.read()
    
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()
    conn.close()
    
    print("Schema created successfully!")
    print("\nSetup complete! You can now run: python main.py")

if __name__ == '__main__':
    try:
        setup_database()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure PostgreSQL is installed and running.")
        print("Download from: https://www.postgresql.org/download/windows/")
