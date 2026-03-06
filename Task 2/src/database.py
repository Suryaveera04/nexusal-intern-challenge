import psycopg
import psycopg_pool
import os


class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Create connection pool."""
        conninfo = f"host={os.getenv('DB_HOST', 'localhost')} port={os.getenv('DB_PORT', 5432)} dbname={os.getenv('DB_NAME', 'call_records_db')} user={os.getenv('DB_USER', 'postgres')} password={os.getenv('DB_PASSWORD', 'postgres')}"
        self.pool = psycopg_pool.AsyncConnectionPool(conninfo, min_size=5, max_size=20)
        await self.pool.open()
    
    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
    
    async def get_connection(self):
        """Get a connection from the pool."""
        return await self.pool.getconn()
    
    async def release_connection(self, conn):
        """Release a connection back to the pool."""
        await self.pool.putconn(conn)
