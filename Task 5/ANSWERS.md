# TASK 5 — Written Design Questions

## Q1: Partial Transcripts vs. Waiting for Complete Speech

**Approach:** Use a hybrid strategy that queries on partial transcripts but only commits to actions on complete utterances.

Start querying the database immediately on partial results to pre-fetch potential solutions, but display them in a "preparing" state without committing to any action. Think of it like Google's search suggestions—as you type "how to reset my rou...", it's already fetching results for "how to reset my router" before you finish.

**Specific Tradeoffs:**

1. **Latency vs. Accuracy:** Querying partial transcripts reduces response time by 1-2 seconds (critical for customer satisfaction), but increases false positives. For example, if someone says "My internet is slow... actually it's completely down," early queries for "slow internet" waste resources.

2. **Database Load vs. User Experience:** Partial queries generate 5-10x more database hits per conversation. A customer speaking for 4 seconds creates ~20 queries instead of 1. This requires connection pooling and caching, but delivers near-instant responses when they finish speaking.

3. **Cost vs. Responsiveness:** More queries mean higher database costs (potentially 3-5x), but studies show each second of delay reduces customer satisfaction by 7%.

**Implementation:** Use debouncing—only query when speech pauses for 100ms+ and the partial transcript changes meaningfully (not just adding "um" or "uh"). Cache results for 5 seconds to avoid redundant queries.

---

## Q2: Auto-Adding High CSAT Resolutions to Knowledge Base

**Problem 1: Context-Specific Solutions Becoming Generic Advice**

A customer rates 5-stars after an agent manually credits their account $50 for a service outage. The system adds "issue a $50 credit" to the knowledge base for "internet outage" problems. Over 6 months, the AI starts suggesting credits for every outage, costing the company thousands in unnecessary refunds.

**Prevention:** Implement solution classification before adding to knowledge base. Flag resolutions containing financial actions (credits, refunds, discounts), account modifications, or agent escalations as "human-decision-required" and exclude them from auto-addition. Only add procedural solutions (restart router, check cables, update firmware) that are universally applicable.

**Problem 2: Outdated Solutions Persisting**

In January, customers love a workaround for a firmware bug: "disable IPv6 in router settings." It gets 5-star ratings and enters the knowledge base. In March, the company releases a firmware update that fixes the bug, but the workaround now causes connectivity issues. The AI keeps suggesting the outdated solution because it has high historical CSAT.

**Prevention:** Implement solution decay and validation. Track CSAT trends over time—if a solution's rating drops below 3.5 in the last 30 days despite historical 4+ average, flag it for review. Add a "solution freshness" check: automatically expire knowledge base entries after 90 days unless manually re-validated by a human expert. Include version tracking—link solutions to specific firmware/software versions and auto-deprecate when versions change.

---

## Q3: Handling an Angry, Escalated Customer

**Customer Statement:** "I've been without internet for 4 days, I called 3 times already, your company is useless and I want to cancel right now."

**AI Step-by-Step Actions:**

1. **Sentiment Analysis (0.5 seconds):** Detect high-anger sentiment (keywords: "useless," "cancel," tone analysis), repeat-caller status, and service duration (4 days).

2. **Immediate Acknowledgment (AI speaks):** "I understand you've been without internet for 4 days and this is your fourth contact with us. That's completely unacceptable, and I'm going to get you help immediately."

3. **Account Lookup (1 second):** Query customer history—verify 3 previous tickets, check if they're still open, identify the issue type, and retrieve account tenure and value.

4. **Critical Decision Point:** This customer meets escalation criteria (repeat contact + cancellation threat + extended outage). DO NOT attempt AI resolution.

5. **Human Handoff (AI speaks):** "I'm connecting you directly to a senior support specialist who can resolve this and discuss your account. They'll have your full history—no need to repeat yourself. Please stay on the line for 30 seconds."

6. **What AI Passes to Human Agent:**
   - **Priority Flag:** "HIGH PRIORITY - Cancellation Risk"
   - **Customer Emotion:** "High anger, frustrated by repeat contacts"
   - **Issue Summary:** "Internet outage - 4 days duration, 3 previous contacts (Ticket #12345, #12389, #12401)"
   - **Account Context:** Account age, monthly value, payment history
   - **Suggested Actions:** "Consider: immediate technician dispatch, service credit, retention offer"
   - **What NOT to Say:** "Don't ask them to repeat the issue or troubleshoot basic steps"

**Key Principle:** The AI recognizes it cannot de-escalate this situation. Attempting automated troubleshooting would further anger the customer. The goal is rapid, empathetic handoff with complete context so the human agent can immediately solve the problem.

---

## Q4: Most Important System Improvement

**Feature: Real-Time Agent Feedback Loop with Confidence Scoring**

**The Problem:** Current systems treat all AI suggestions equally. Agents can't quickly signal "this suggestion is wrong" or "this worked perfectly," so the AI keeps making the same mistakes and doesn't learn what actually works in production.

**How to Build It:**

1. **Add Inline Feedback Buttons:** When the AI suggests a solution, show agents three buttons: 👍 (Worked), 👎 (Wrong), ⚠️ (Partially Helpful). Takes 1 second to click.

2. **Confidence Scoring Engine:** Track success rates per solution type. If "restart router" gets 85% 👍 for "slow internet" but only 40% for "no connection," adjust confidence scores. Display confidence to agents: "Solution confidence: 87% - High" or "Solution confidence: 45% - Low, consider alternatives."

3. **Immediate Model Adjustment:** When a solution gets 3+ 👎 votes in 24 hours, automatically reduce its ranking. When it gets 10+ 👍 votes, boost it. This creates a continuous learning loop without waiting for monthly retraining.

4. **Agent Override Learning:** When agents ignore the AI's #1 suggestion and manually choose #3, log that decision. If this pattern repeats (agents consistently pick #3 over #1 for specific issue types), automatically re-rank suggestions.

**Real Example:** An AI suggests "check if router is plugged in" for every connectivity issue. Agents give it 👎 60% of the time because most customers already checked. Within 48 hours, the system learns to only suggest this for first-time callers or when other indicators suggest power issues.

**How to Measure Success:**

1. **Primary Metric:** Agent acceptance rate of AI suggestions. Target: increase from baseline 40% to 65% within 3 months.

2. **Secondary Metrics:**
   - Average resolution time (should decrease by 20%)
   - Number of agent overrides (should decrease by 30%)
   - Customer CSAT for AI-assisted resolutions (should increase by 0.5 points)

3. **A/B Test:** Run 50% of agents with feedback loop enabled, 50% without. Compare resolution times and CSAT scores weekly.

**Why This Matters Most:** Every other improvement (better NLP, more data, faster queries) is limited by not knowing what actually works in production. This creates a flywheel—better feedback → better suggestions → happier agents → more feedback → even better suggestions. It turns your agents into trainers, making the system smarter every single day without expensive retraining cycles.
