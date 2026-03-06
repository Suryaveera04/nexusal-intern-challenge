"""Test suite for Escalation Decision Engine"""

import pytest
from escalation import should_escalate, CustomerContext


def test_rule1_low_confidence():
    """
    Tests Rule 1: Confidence below 0.65 triggers escalation.
    This matters because low AI confidence indicates uncertainty that requires human judgment.
    """
    context = CustomerContext(
        is_vip=False,
        billing_overdue=False,
        data_complete=True,
        ticket_history=[]
    )
    result, reason = should_escalate(context, 0.64, 0.5, "general_inquiry")
    assert result is True
    assert reason == "low_confidence"


def test_rule2_angry_customer():
    """
    Tests Rule 2: Sentiment below -0.6 triggers escalation.
    This matters because angry customers need empathetic human intervention to prevent churn.
    """
    context = CustomerContext(
        is_vip=False,
        billing_overdue=False,
        data_complete=True,
        ticket_history=[]
    )
    result, reason = should_escalate(context, 0.90, -0.61, "complaint")
    assert result is True
    assert reason == "angry_customer"


def test_rule3_repeat_complaint():
    """
    Tests Rule 3: Same intent appearing 3+ times in history triggers escalation.
    This matters because repeated issues indicate unresolved problems requiring human attention.
    """
    context = CustomerContext(
        is_vip=False,
        billing_overdue=False,
        data_complete=True,
        ticket_history=["billing_issue", "billing_issue", "billing_issue"]
    )
    result, reason = should_escalate(context, 0.90, 0.5, "billing_issue")
    assert result is True
    assert reason == "repeat_complaint"


def test_rule4_service_cancellation():
    """
    Tests Rule 4: service_cancellation intent always escalates.
    This matters because cancellations are critical business events requiring human retention efforts.
    """
    context = CustomerContext(
        is_vip=False,
        billing_overdue=False,
        data_complete=True,
        ticket_history=[]
    )
    result, reason = should_escalate(context, 0.95, 0.8, "service_cancellation")
    assert result is True
    assert reason == "service_cancellation"


def test_rule5_vip_overdue_billing():
    """
    Tests Rule 5: VIP customer with overdue billing triggers escalation.
    This matters because VIP customers are high-value and billing issues need immediate resolution.
    """
    context = CustomerContext(
        is_vip=True,
        billing_overdue=True,
        data_complete=True,
        ticket_history=[]
    )
    result, reason = should_escalate(context, 0.90, 0.5, "general_inquiry")
    assert result is True
    assert reason == "vip_overdue_billing"


def test_rule6_incomplete_data_low_confidence():
    """
    Tests Rule 6: Incomplete data with confidence below 0.80 triggers escalation.
    This matters because missing information combined with uncertainty creates high error risk.
    """
    context = CustomerContext(
        is_vip=False,
        billing_overdue=False,
        data_complete=False,
        ticket_history=[]
    )
    result, reason = should_escalate(context, 0.79, 0.5, "general_inquiry")
    assert result is True
    assert reason == "incomplete_data"


def test_edge_case_no_escalation_perfect_conditions():
    """
    Tests edge case: All conditions are optimal, no escalation should occur.
    This matters to verify the system allows AI to handle straightforward cases efficiently.
    """
    context = CustomerContext(
        is_vip=False,
        billing_overdue=False,
        data_complete=True,
        ticket_history=[]
    )
    result, reason = should_escalate(context, 0.95, 0.8, "general_inquiry")
    assert result is False
    assert reason == "no_escalation"


def test_edge_case_boundary_values():
    """
    Tests edge case: Values exactly at thresholds should not escalate.
    This matters to ensure boundary conditions are handled correctly and consistently.
    """
    context = CustomerContext(
        is_vip=False,
        billing_overdue=False,
        data_complete=True,
        ticket_history=["issue", "issue"]  # Only 2 occurrences
    )
    # Confidence exactly at 0.65, sentiment exactly at -0.6
    result, reason = should_escalate(context, 0.65, -0.6, "issue")
    assert result is False
    assert reason == "no_escalation"
