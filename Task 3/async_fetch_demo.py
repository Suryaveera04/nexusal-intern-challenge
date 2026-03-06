"""
Async parallelism demonstration for fetching data from multiple external systems.
Shows performance improvement when using asyncio.gather() vs sequential execution.
"""

import asyncio
import random
import time
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# PART 1 — Mock Async Data Sources

async def fetch_crm(phone: str) -> dict:
    """Simulate CRM system with 200-400ms latency."""
    await asyncio.sleep(random.uniform(0.2, 0.4))
    return {
        "customer_id": random.randint(10000, 99999),
        "name": random.choice(["Alice Johnson", "Bob Smith", "Carol White", "David Brown"]),
        "account_status": random.choice(["active", "suspended", "pending"]),
        "plan_type": random.choice(["premium", "standard", "basic"]),
        "phone": phone
    }


async def fetch_billing(phone: str) -> dict:
    """Simulate billing system with 150-350ms latency and 10% failure rate."""
    await asyncio.sleep(random.uniform(0.15, 0.35))
    
    # 10% probability of timeout
    if random.random() < 0.1:
        raise TimeoutError("Billing service timeout")
    
    return {
        "payment_status": random.choice(["paid", "pending", "overdue"]),
        "last_payment_date": random.choice(["2024-01-15", "2024-02-10", "2024-03-05"]),
        "outstanding_balance": round(random.uniform(0, 500), 2)
    }


async def fetch_ticket_history(phone: str) -> dict:
    """Simulate ticket system with 100-300ms latency."""
    await asyncio.sleep(random.uniform(0.1, 0.3))
    
    complaints = [
        "Internet connection slow",
        "Billing discrepancy",
        "Service outage",
        "Router not working",
        "Cannot access email"
    ]
    
    return {
        "last_5_complaints": random.sample(complaints, k=random.randint(0, 5)),
        "open_ticket_count": random.randint(0, 3)
    }


# PART 2 — CustomerContext Dataclass

@dataclass
class CustomerContext:
    """Container for aggregated customer data from multiple sources."""
    crm_data: dict | None
    billing_data: dict | None
    ticket_history: dict | None
    data_complete: bool
    fetch_time_ms: float


# PART 3 — Sequential Fetch

async def fetch_sequential(phone: str) -> CustomerContext:
    """
    Fetch data sequentially (one after another).
    Total time = sum of all individual fetch times.
    """
    start = time.perf_counter()
    
    crm_data = await fetch_crm(phone)
    
    billing_data = None
    try:
        billing_data = await fetch_billing(phone)
    except TimeoutError as e:
        logger.warning(f"Sequential fetch - {e}")
    
    ticket_history = await fetch_ticket_history(phone)
    
    elapsed = (time.perf_counter() - start) * 1000
    data_complete = all([crm_data, billing_data, ticket_history])
    
    return CustomerContext(
        crm_data=crm_data,
        billing_data=billing_data,
        ticket_history=ticket_history,
        data_complete=data_complete,
        fetch_time_ms=elapsed
    )


# PART 4 — Parallel Fetch

async def fetch_parallel(phone: str) -> CustomerContext:
    """
    Fetch data in parallel using asyncio.gather().
    Total time ≈ max(individual fetch times) instead of sum.
    """
    start = time.perf_counter()
    
    # Execute all fetches concurrently, capturing exceptions
    results = await asyncio.gather(
        fetch_crm(phone),
        fetch_billing(phone),
        fetch_ticket_history(phone),
        return_exceptions=True
    )
    
    crm_data, billing_data, ticket_history = results
    
    # Handle billing timeout error
    if isinstance(billing_data, TimeoutError):
        logger.warning(f"Parallel fetch - {billing_data}")
        billing_data = None
    
    elapsed = (time.perf_counter() - start) * 1000
    data_complete = all([crm_data, billing_data, ticket_history])
    
    return CustomerContext(
        crm_data=crm_data,
        billing_data=billing_data,
        ticket_history=ticket_history,
        data_complete=data_complete,
        fetch_time_ms=elapsed
    )


# PART 5 — Benchmark Runner

async def run_benchmark(phone: str):
    """
    Compare sequential vs parallel fetch performance.
    Parallel should be ~2-3x faster due to concurrent I/O.
    """
    # Sequential execution
    seq_result = await fetch_sequential(phone)
    print(f"Sequential fetch time: {seq_result.fetch_time_ms:.0f} ms")
    
    # Parallel execution
    par_result = await fetch_parallel(phone)
    print(f"Parallel fetch time: {par_result.fetch_time_ms:.0f} ms")
    
    # Calculate improvement
    speedup = seq_result.fetch_time_ms / par_result.fetch_time_ms
    print(f"Speed improvement: {speedup:.1f}x faster")


# PART 6 — Main Runner

if __name__ == "__main__":
    asyncio.run(run_benchmark("9876543210"))
