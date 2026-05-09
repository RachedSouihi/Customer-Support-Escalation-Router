import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.tickets import router as tickets_router
from app.core.database import init_db, get_ticket_by_id, get_all_tickets


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
app = FastAPI(
    title="Customer Support Escalation Router",
    version="0.1.0",
    description="Minimal FastAPI backend for ticket analysis and routing.",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # Create the SQLite table once when the app starts.
    init_db()


@app.get("/")
def health_check() -> dict[str, str]:
    logger.info("Health check endpoint called")
    # Small health endpoint for quick smoke tests.
    return {"status": "ok", "service": "customer-support-escalation-router"}


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str) -> dict:
    """Retrieve a specific ticket analysis by ID."""
    logger.info(f"Retrieving ticket: {ticket_id}")
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket


@app.get("/tickets")
def list_tickets(limit: int = 50, offset: int = 0) -> dict:
    """Retrieve all ticket analyses with pagination."""
    logger.info(f"Retrieving tickets with limit={limit}, offset={offset}")
    tickets = get_all_tickets(limit=limit, offset=offset)
    return {"tickets": tickets, "count": len(tickets)}


app.include_router(tickets_router)
