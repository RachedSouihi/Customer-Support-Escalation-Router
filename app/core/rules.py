from __future__ import annotations


REFUND_KEYWORDS = {"refund", "chargeback", "money back"}
COMPLAINT_KEYWORDS = {"complaint", "angry", "bad service", "frustrated"}
CANCEL_KEYWORDS = {"cancel", "subscription", "unsubscribe"}
HIGH_PRIORITY_KEYWORDS = {"urgent", "asap", "immediately", "broken", "down"}


def classify_intent(message: str) -> str:
    text = message.lower()

    if any(keyword in text for keyword in REFUND_KEYWORDS):
        return "refund"
    if any(keyword in text for keyword in COMPLAINT_KEYWORDS):
        return "complaint"
    if any(keyword in text for keyword in CANCEL_KEYWORDS):
        return "cancellation"
    return "inquiry"


def assign_priority_from_rules(message: str, intent: str) -> str:
    text = message.lower()

    if any(keyword in text for keyword in HIGH_PRIORITY_KEYWORDS):
        return "high"
    if intent in {"refund", "complaint"}:
        return "high"
    if intent == "cancellation":
        return "medium"
    return "low"


def decide_route_from_rules(intent: str, priority: str) -> str:
    if priority == "high":
        return "human"
    if intent == "refund":
        return "human"
    return "auto-response"


def build_response_prompt(message: str, intent: str, priority: str, route_to: str) -> str:
    return (
        "Write a short customer support reply. "
        f"Intent: {intent}. Priority: {priority}. Route: {route_to}. "
        f"Customer message: {message}"
    )
