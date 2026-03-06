"""Escalation Decision Engine - Core Logic"""

from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class CustomerContext:
    """Customer context information for escalation decisions"""
    is_vip: bool
    billing_overdue: bool
    data_complete: bool
    ticket_history: List[str]


def should_escalate(
    context: CustomerContext,
    confidence_score: float,
    sentiment_score: float,
    intent: str
) -> Tuple[bool, str]:
    """
    Determines if a customer interaction should be escalated to a human agent.
    
    Args:
        context: CustomerContext object with customer information
        confidence_score: AI confidence score (0.0 to 1.0)
        sentiment_score: Sentiment score (-1.0 to 1.0)
        intent: Detected customer intent
    
    Returns:
        Tuple of (should_escalate: bool, reason: str)
    """
    # Rule 4: service_cancellation always escalates (highest priority)
    if intent == "service_cancellation":
        return (True, "service_cancellation")
    
    # Rule 1: Low confidence
    if confidence_score < 0.65:
        return (True, "low_confidence")
    
    # Rule 2: Angry customer
    if sentiment_score < -0.6:
        return (True, "angry_customer")
    
    # Rule 3: Repeat complaint
    if context.ticket_history.count(intent) >= 3:
        return (True, "repeat_complaint")
    
    # Rule 5: VIP with overdue billing
    if context.is_vip and context.billing_overdue:
        return (True, "vip_overdue_billing")
    
    # Rule 6: Incomplete data with low-medium confidence
    if not context.data_complete and confidence_score < 0.80:
        return (True, "incomplete_data")
    
    return (False, "no_escalation")
