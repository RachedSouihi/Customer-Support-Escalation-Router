from fastapi import APIRouter, HTTPException

# Ensure the project's embedded `agents` package (under `agents/src`) is
# importable when running the app directly (e.g. `uvicorn app.main:app`).
# This inserts `<project_root>/agents/src` into `sys.path` so `import agents.*`
# works without requiring an editable install or setting PYTHONPATH externally.
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
agents_src = str(project_root / "agents" / "src")
if agents_src not in sys.path:
    sys.path.insert(0, agents_src)

from app.core.database import save_ticket_analysis
from uuid import uuid4
from app.models.ticket import TicketAnalysisResponse, TicketInput, AgentTraceStep

from agents.main import run_ticket_flow

router = APIRouter(tags=["tickets"])


@router.post("/analyze-ticket", response_model=TicketAnalysisResponse)
def analyze_ticket(ticket: TicketInput) -> TicketAnalysisResponse:
    # Generate ticket_id if not provided
    #if not ticket.ticket_id:
    ticket.ticket_id = str(uuid4())
    
    # Run the ticket through the agent workflow
    print("[analyze_ticket] Received ticket:", ticket)
    state = run_ticket_flow(ticket.dict())

    # Check if workflow actually ran (look for meaningful trace from agents)
    if isinstance(state.trace, str) and state.trace.startswith("No ticket data provided"):
        raise HTTPException(status_code=400, detail=state.trace)

    # Convert the flow state into the API response model.
    trace_list = [AgentTraceStep(**step) for step in getattr(state, "trace_steps", []) if step]
    if not trace_list and getattr(state, "trace", None):
        trace_list.append(
            AgentTraceStep(
                agent="Response generated",
                decision="completed",
                details=state.trace,
                status="completed",
            )
        )

    analysis = TicketAnalysisResponse(
        intent=getattr(state, "intent", "") or "",
        tags=getattr(state, "tags", []) or [],
        priority=getattr(state, "priority", "") or "",
        route_to=getattr(state, "routing", "") or "",
        response=getattr(state, "response", "") or "",
        trace=trace_list,
    )

    # Save the result in SQLite so the demo has a basic audit trail.
    save_ticket_analysis(ticket, analysis)

    return analysis
