import psycopg_pool
from typing import Optional
from datetime import datetime


class CallRecordRepository:
    def __init__(self, pool: psycopg_pool.AsyncConnectionPool):
        self.pool = pool
    
    async def save(self, call_data: dict) -> int:
        """Insert a call record and return the generated ID."""
        query = """
            INSERT INTO call_records (
                customer_phone, channel, transcript, ai_response, 
                outcome, confidence_score, csat_score, timestamp, 
                duration, intent_type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    query,
                    (
                        call_data['customer_phone'],
                        call_data['channel'],
                        call_data['transcript'],
                        call_data['ai_response'],
                        call_data['outcome'],
                        call_data['confidence_score'],
                        call_data.get('csat_score'),
                        call_data.get('timestamp', datetime.utcnow()),
                        call_data['duration'],
                        call_data['intent_type']
                    )
                )
                result = await cur.fetchone()
                return result[0]
    
    async def get_recent(self, phone: str, limit: int = 5) -> list:
        """Return the most recent calls for a given phone number."""
        query = """
            SELECT 
                id, customer_phone, channel, transcript, ai_response,
                outcome, confidence_score, csat_score, timestamp, 
                duration, intent_type
            FROM call_records
            WHERE customer_phone = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (phone, limit))
                rows = await cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in rows]
