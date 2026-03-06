import asyncio
import sys
from datetime import datetime, timedelta, UTC
from src.database import Database
from src.repository import CallRecordRepository
from src.analytics import get_low_resolution_intents

# Fix for Windows psycopg3 async
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    # Initialize database
    db = Database()
    await db.connect()
    
    # Create repository
    repo = CallRecordRepository(db.pool)
    
    # Example 1: Save call records
    print("=== Saving Call Records ===")
    sample_calls = [
        {
            'customer_phone': '+1234567890',
            'channel': 'phone',
            'transcript': 'Customer asked about billing issue',
            'ai_response': 'I can help you with that billing concern',
            'outcome': 'resolved',
            'confidence_score': 0.95,
            'csat_score': 5,
            'duration': 180,
            'intent_type': 'billing',
            'timestamp': datetime.now(UTC)
        },
        {
            'customer_phone': '+1234567890',
            'channel': 'chat',
            'transcript': 'Need technical support',
            'ai_response': 'Let me connect you with technical team',
            'outcome': 'escalated',
            'confidence_score': 0.75,
            'csat_score': 3,
            'duration': 240,
            'intent_type': 'technical_support',
            'timestamp': datetime.now(UTC) - timedelta(days=1)
        },
        {
            'customer_phone': '+9876543210',
            'channel': 'email',
            'transcript': 'Product inquiry',
            'ai_response': 'Here are the product details',
            'outcome': 'resolved',
            'confidence_score': 0.88,
            'csat_score': 4,
            'duration': 120,
            'intent_type': 'product_inquiry',
            'timestamp': datetime.now(UTC) - timedelta(days=2)
        }
    ]
    
    for call in sample_calls:
        record_id = await repo.save(call)
        print(f"Saved record with ID: {record_id}")
    
    # Example 2: Get recent calls
    print("\n=== Recent Calls for +1234567890 ===")
    recent_calls = await repo.get_recent('+1234567890', limit=5)
    for call in recent_calls:
        print(f"ID: {call['id']}, Channel: {call['channel']}, Outcome: {call['outcome']}")
    
    # Example 3: Get analytics
    print("\n=== Low Resolution Intents (Last 7 Days) ===")
    async with db.pool.connection() as conn:
        analytics = await get_low_resolution_intents(conn)
        for item in analytics:
            print(f"Intent: {item['intent_type']}, "
                  f"Resolution Rate: {item['resolution_rate']}, "
                  f"Avg CSAT: {item['avg_csat']}")
    
    # Cleanup
    await db.disconnect()
    print("\n=== Demo Complete ===")


if __name__ == '__main__':
    asyncio.run(main())
