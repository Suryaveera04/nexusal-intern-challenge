-- Top 5 intent types with lowest resolution rate in last 7 days
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
LIMIT 5;
