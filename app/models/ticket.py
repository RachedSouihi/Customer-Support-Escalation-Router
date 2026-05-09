from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TicketInput(BaseModel):
    # Keep the input shape small so the API is easy to test in Postman or curl.
    subject: Optional[str] = None
    ticket_id: Optional[str] = None
    body: str = Field(..., min_length=1, description="Customer support ticket text")
    customer_name: Optional[str] = None
    customer_tier: Optional[str] = None
    


class AgentTraceStep(BaseModel):
    # Each step explains what the mini-agent decided.
    agent: str
    decision: str
    details: str
    status: str = "completed"


class TicketAnalysisResponse(BaseModel):
    # This response is intentionally compact and demo-friendly.
    intent: str
    tags: List[str] = Field(default_factory=list)
    priority: str
    route_to: str
    response: str
    trace: List[AgentTraceStep]
