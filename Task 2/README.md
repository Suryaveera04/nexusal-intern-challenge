# Call Records Management System

Production-quality PostgreSQL schema and Python repository layer for storing customer interaction records.

## 📋 Project Overview

This project implements a complete database solution for managing customer call records with:
- Production-ready PostgreSQL schema with proper constraints and indexes
- Async Python repository layer using psycopg3
- Analytics queries for business insights
- Full CRUD operations with connection pooling

## 📁 Project Structure

```
.
├── sql/
│   ├── schema.sql          # Database schema with tables and indexes
│   └── analytics.sql       # Analytics query for low resolution intents
├── src/
│   ├── __init__.py         # Package initialization
│   ├── database.py         # Database connection management
│   ├── repository.py       # CallRecordRepository class
│   └── analytics.py        # Analytics functions
├── tests/
│   └── test_repository.py  # Unit tests
├── main.py                 # Demo script
├── setup.py                # Database setup script
├── demo_no_db.py           # Demo without database connection
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🎯 Features

### PostgreSQL Schema Features
- **ENUMs** for channel_type ('phone', 'chat', 'email', 'sms') and outcome_type ('resolved', 'escalated', 'failed')
- **CHECK constraints** for CSAT score (1-5) and confidence_score (0-1)
- **Three strategic indexes** for query optimization with detailed comments
- **TIMESTAMPTZ** for timezone-aware timestamps
- **BIGSERIAL** primary key for high-volume data support

### Python Repository Features
- Async PostgreSQL access with **psycopg3**
- Connection pooling for production scalability
- Parameterized queries (SQL injection prevention)
- Type hints for maintainability
- Windows async event loop compatibility

### Analytics
- Query returns top 5 intent types with lowest resolution rate in the last 7 days
- Includes average CSAT scores for each intent type
- Resolution rate calculation: (resolved calls) / (total calls)

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+ (tested with Python 3.13)
- PostgreSQL 16+ installed and running

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `psycopg[binary]>=3.2.2` - PostgreSQL adapter for Python
- `psycopg-pool` - Connection pooling
- `python-dotenv==1.0.0` - Environment variable management

### Step 2: Install PostgreSQL

**Windows:**
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer and select "Database Server"
3. Remember the password you set for 'postgres' user
4. Keep default port: 5432

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 3: Configure Database Connection

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_NAME=call_records_db
```

### Step 4: Create Database and Schema

Run the setup script:
```bash
python setup.py
```

This will:
1. Connect to PostgreSQL
2. Create the `call_records_db` database
3. Run the schema to create tables, ENUMs, and indexes

### Step 5: Run the Demo

```bash
python main.py
```

Expected output:
```
=== Saving Call Records ===
Saved record with ID: 1
Saved record with ID: 2
Saved record with ID: 3

=== Recent Calls for +1234567890 ===
ID: 2, Channel: chat, Outcome: escalated
ID: 1, Channel: phone, Outcome: resolved

=== Low Resolution Intents (Last 7 Days) ===
Intent: technical_support, Resolution Rate: 0.000, Avg CSAT: 3.00
Intent: billing, Resolution Rate: 1.000, Avg CSAT: 5.00
Intent: product_inquiry, Resolution Rate: 1.000, Avg CSAT: 4.00

=== Demo Complete ===
```

## 📖 Usage Examples

### Basic Usage

```python
import asyncio
from src.database import Database
from src.repository import CallRecordRepository
from src.analytics import get_low_resolution_intents

async def main():
    # Initialize database connection
    db = Database()
    await db.connect()
    
    # Create repository
    repo = CallRecordRepository(db.pool)
    
    # Save a call record
    call_data = {
        'customer_phone': '+1234567890',
        'channel': 'phone',
        'transcript': 'Customer inquiry about billing',
        'ai_response': 'I can help you with that',
        'outcome': 'resolved',
        'confidence_score': 0.95,
        'csat_score': 5,
        'duration': 180,
        'intent_type': 'billing'
    }
    record_id = await repo.save(call_data)
    print(f"Saved record: {record_id}")
    
    # Get recent calls
    recent = await repo.get_recent('+1234567890', limit=5)
    for call in recent:
        print(f"Call ID: {call['id']}, Outcome: {call['outcome']}")
    
    # Get analytics
    async with db.pool.connection() as conn:
        analytics = await get_low_resolution_intents(conn)
        for item in analytics:
            print(f"{item['intent_type']}: {item['resolution_rate']}")
    
    # Cleanup
    await db.disconnect()

asyncio.run(main())
```

### Repository Methods

#### `save(call_data: dict) -> int`
Inserts a call record and returns the generated ID.

**Parameters:**
- `customer_phone` (str): Phone number
- `channel` (str): 'phone', 'chat', 'email', or 'sms'
- `transcript` (str): Call transcript
- `ai_response` (str): AI response text
- `outcome` (str): 'resolved', 'escalated', or 'failed'
- `confidence_score` (float): 0.0 to 1.0
- `csat_score` (int, optional): 1 to 5
- `duration` (int): Duration in seconds
- `intent_type` (str): Intent classification
- `timestamp` (datetime, optional): Defaults to current UTC time

#### `get_recent(phone: str, limit: int = 5) -> list`
Returns the most recent calls for a given phone number.

**Parameters:**
- `phone` (str): Customer phone number
- `limit` (int): Maximum number of records to return

**Returns:** List of dictionaries with all call record fields

### Analytics Function

#### `get_low_resolution_intents(conn) -> list[dict]`
Returns top 5 intent types with lowest resolution rate in last 7 days.

**Returns:** List of dictionaries with:
- `intent_type` (str): Intent classification
- `resolution_rate` (Decimal): Ratio of resolved to total calls
- `avg_csat` (Decimal): Average CSAT score

## 🧪 Running Tests

```bash
pytest tests/
```

Or with coverage:
```bash
pytest --cov=src tests/
```

## 🔧 Troubleshooting

### Issue: "password authentication failed for user 'postgres'"

**Solution:** Update `.env` with correct PostgreSQL password.

To reset PostgreSQL password:
```bash
# Open SQL Shell (psql)
psql -U postgres
# Run this command
ALTER USER postgres PASSWORD 'newpassword';
\q
```

### Issue: "Psycopg cannot use the 'ProactorEventLoop'"

**Solution:** Already fixed in code with:
```python
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

### Issue: "ModuleNotFoundError: No module named 'psycopg_pool'"

**Solution:**
```bash
pip install psycopg-pool
```

### Issue: Can't connect to PostgreSQL

**Check if PostgreSQL is running:**

Windows:
```bash
net start postgresql-x64-18
```

macOS:
```bash
brew services list
```

Linux:
```bash
sudo systemctl status postgresql
```

## 📊 Database Schema Details

### Table: call_records

| Column | Type | Constraints |
|--------|------|-------------|
| id | BIGSERIAL | PRIMARY KEY |
| customer_phone | VARCHAR(20) | NOT NULL |
| channel | channel_type | NOT NULL |
| transcript | TEXT | NOT NULL |
| ai_response | TEXT | NOT NULL |
| outcome | outcome_type | NOT NULL |
| confidence_score | NUMERIC(3,2) | NOT NULL, CHECK (0-1) |
| csat_score | SMALLINT | CHECK (1-5), NULLABLE |
| timestamp | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| duration | INTEGER | NOT NULL |
| intent_type | VARCHAR(50) | NOT NULL |

### Indexes

1. **idx_call_records_phone_timestamp** - Optimizes queries by phone number and time
2. **idx_call_records_timestamp** - Supports time-range filtering
3. **idx_call_records_intent_outcome** - Accelerates analytics queries

## 🎓 Academic Requirements Met

✅ **PART 1 - PostgreSQL Table**
- Proper data types (not all VARCHAR)
- Primary key (BIGSERIAL)
- ENUMs for channel and outcome
- CHECK constraints for CSAT (1-5) and confidence_score (0-1)
- Three indexes with SQL comments explaining purpose
- Production-ready schema

✅ **PART 2 - Python Repository Class**
- Async PostgreSQL access with psycopg3
- Parameterized queries (no SQL injection)
- `save()` method for inserting records
- `get_recent()` method returning list of dicts

✅ **PART 3 - Analytics Query**
- Top 5 intent types with lowest resolution rate
- Last 7 days filter
- Average CSAT score included
- Proper resolution rate calculation

✅ **PART 4 - Python Function**
- `get_low_resolution_intents()` async function
- Returns list of dictionaries
- Executes analytics SQL query

## 🚫 Alternative: Demo Without Database

If you can't set up PostgreSQL, run:

```bash
python demo_no_db.py
```

This displays all the code without requiring a database connection.

## 📝 License

This project is for academic purposes.

## 👤 Author

Created as a production-quality solution for database management system coursework.

---

**Note:** This is a complete, production-ready implementation following PostgreSQL and Python async best practices.
