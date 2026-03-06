# Task 4: Escalation Decision Engine

## Overview
This module implements an intelligent escalation decision engine that determines when customer interactions should be escalated from AI to human agents.

## Installation
```bash
pip install pytest
```

## How to Run

### Run Tests
```bash
pytest test_escalation.py -v
```

### Run Main Code (Example)
```bash
python escalation.py
```

### Run Individual Test
```bash
pytest test_escalation.py::test_rule1_low_confidence -v
```
### Run All Test
```bash
python -m pytest test_escalation.py -v  
```

## Rule Conflict Resolution

When multiple escalation rules are triggered simultaneously, the system follows a priority-based approach. Rule 4 (service_cancellation) takes absolute precedence because cancellations represent critical business events requiring immediate human intervention regardless of other factors. After that, rules are evaluated in order (1→2→3→5→6), with the first matching condition triggering escalation. For example, if confidence is 0.90 but intent is service_cancellation, Rule 4 wins because preventing customer churn is more valuable than leveraging high AI confidence. This design prioritizes business impact over technical metrics, ensuring critical situations always receive human attention while allowing AI to handle routine cases efficiently.

## Function Signature
```python
def should_escalate(
    context: CustomerContext,
    confidence_score: float,
    sentiment_score: float,
    intent: str
) -> Tuple[bool, str]
```

## Escalation Rules
1. **Low Confidence**: confidence < 0.65 → escalate
2. **Angry Customer**: sentiment < -0.6 → escalate
3. **Repeat Complaint**: intent appears 3+ times in history → escalate
4. **Service Cancellation**: intent == "service_cancellation" → always escalate
5. **VIP Overdue**: VIP customer with overdue billing → escalate
6. **Incomplete Data**: data_complete == False AND confidence < 0.80 → escalate

## Example Usage
```python
from escalation import should_escalate, CustomerContext

context = CustomerContext(
    is_vip=True,
    billing_overdue=False,
    data_complete=True,
    ticket_history=["billing_issue", "general_inquiry"]
)

should_escalate_flag, reason = should_escalate(
    context=context,
    confidence_score=0.85,
    sentiment_score=0.3,
    intent="general_inquiry"
)

print(f"Escalate: {should_escalate_flag}, Reason: {reason}")
```
