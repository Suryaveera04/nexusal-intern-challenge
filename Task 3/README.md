# Async Parallelism Performance Demo

A Python module demonstrating the performance benefits of async parallelism when fetching data from multiple external systems using `asyncio`.

## Overview

This project compares **sequential** vs **parallel** execution of async I/O operations, showing how `asyncio.gather()` can significantly improve performance by running multiple network calls concurrently.

## Features

- **Mock External Systems**: Simulates CRM, Billing, and Ticket History services with realistic latency
- **Error Handling**: Demonstrates graceful handling of service timeouts (10% failure rate in billing)
- **Performance Benchmarking**: Measures and compares execution times
- **Production-Ready**: Clean architecture with proper logging and type hints

## Requirements

- **Python 3.10+** (uses `dict | None` union syntax)
- No external dependencies (uses only standard library)

## Installation

1. Clone or download this project
2. Ensure Python 3.10+ is installed:
   ```bash
   python --version
   ```

## How to Run

### Basic Execution

```bash
python async_fetch_demo.py
```

### Expected Behavior

The program will:
1. Fetch customer data **sequentially** (one service at a time)
2. Fetch customer data **in parallel** (all services simultaneously)
3. Display timing comparison and speedup factor

## Sample Output

```
Sequential fetch time: 782 ms
Parallel fetch time: 312 ms
Speed improvement: 2.5x faster
```

### With Billing Timeout (10% chance)

```
WARNING: Parallel fetch - Billing service timeout
Sequential fetch time: 695 ms
Parallel fetch time: 289 ms
Speed improvement: 2.4x faster
```

## Architecture

### Mock Data Sources

| Service | Latency | Failure Rate |
|---------|---------|--------------|
| CRM | 200-400ms | 0% |
| Billing | 150-350ms | 10% (TimeoutError) |
| Ticket History | 100-300ms | 0% |

### Key Components

- **fetch_crm()**: Returns customer profile data
- **fetch_billing()**: Returns payment information (may timeout)
- **fetch_ticket_history()**: Returns support ticket data
- **CustomerContext**: Dataclass aggregating all fetched data
- **fetch_sequential()**: Executes requests one-by-one
- **fetch_parallel()**: Executes requests concurrently using `asyncio.gather()`

## Performance Analysis

### Sequential Execution
- Total time = CRM + Billing + Tickets
- Range: ~450-1050ms
- Waits for each service before starting the next

### Parallel Execution
- Total time ≈ max(CRM, Billing, Tickets)
- Range: ~200-400ms
- All services called simultaneously
- **Typical speedup: 2-3x faster**

## Why Parallel is Faster

During I/O operations (network calls, database queries), the CPU is idle. Async parallelism allows the event loop to:
1. Start all three requests immediately
2. Switch between tasks during their wait periods
3. Process results as they arrive
4. Complete in roughly the time of the slowest request

## Use Cases

This pattern is ideal for:
- Aggregating data from multiple microservices
- Fetching from multiple databases
- Calling multiple external APIs
- Any scenario with independent I/O-bound operations

## Code Quality

- Type hints throughout
- Proper error handling with `return_exceptions=True`
- Logging for debugging
- Clean separation of concerns
- Production-ready structure

## License

MIT
