import psycopg


async def get_low_resolution_intents(conn: psycopg.AsyncConnection) -> list[dict]:
    """
    Get top 5 intent types with lowest resolution rate in last 7 days.
    Returns list of dicts with intent_type, resolution_rate, and avg_csat.
    """
    query = """
        SELECT 
            intent_type,
            ROUND(
                SUM(CASE WHEN outcome = 'resolved' THEN 1 ELSE 0 END)::NUMERIC / 
                COUNT(*)::NUMERIC, 
                3
            ) AS resolution_rate,
            ROUND(AVG(csat_score), 2) AS avg_csat
        FROM call_records
        WHERE timestamp >= NOW() - INTERVAL '7 days'
        GROUP BY intent_type
        HAVING COUNT(*) > 0
        ORDER BY resolution_rate ASC
        LIMIT 5
    """
    async with conn.cursor() as cur:
        await cur.execute(query)
        rows = await cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in rows]
