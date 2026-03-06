import asyncio
import pytest
from datetime import datetime
from src.database import Database
from src.repository import CallRecordRepository


@pytest.fixture
async def db():
    """Database fixture."""
    database = Database()
    await database.connect()
    yield database
    await database.disconnect()


@pytest.fixture
async def repo(db):
    """Repository fixture."""
    return CallRecordRepository(db.pool)


@pytest.mark.asyncio
async def test_save_call_record(repo):
    """Test saving a call record."""
    call_data = {
        'customer_phone': '+1234567890',
        'channel': 'phone',
        'transcript': 'Test transcript',
        'ai_response': 'Test response',
        'outcome': 'resolved',
        'confidence_score': 0.95,
        'csat_score': 5,
        'duration': 180,
        'intent_type': 'test_intent',
        'timestamp': datetime.utcnow()
    }
    
    record_id = await repo.save(call_data)
    assert record_id is not None
    assert isinstance(record_id, int)


@pytest.mark.asyncio
async def test_get_recent_calls(repo):
    """Test retrieving recent calls."""
    phone = '+9876543210'
    
    # Save test records
    for i in range(3):
        call_data = {
            'customer_phone': phone,
            'channel': 'chat',
            'transcript': f'Test {i}',
            'ai_response': f'Response {i}',
            'outcome': 'resolved',
            'confidence_score': 0.85,
            'csat_score': 4,
            'duration': 120,
            'intent_type': 'test'
        }
        await repo.save(call_data)
    
    # Retrieve recent calls
    recent = await repo.get_recent(phone, limit=5)
    assert len(recent) >= 3
    assert recent[0]['customer_phone'] == phone
