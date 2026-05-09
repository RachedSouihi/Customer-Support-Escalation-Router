from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.core.config import settings
from app.models.ticket import TicketAnalysisResponse, TicketInput


def _database_path() -> Path:
    return Path(settings.database_path)


def get_connection() -> sqlite3.Connection:
    # SQLite is enough for the MVP and keeps local setup very simple.
    db_path = _database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyzed_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                intent TEXT NOT NULL,
                priority TEXT NOT NULL,
                route_to TEXT NOT NULL,
                response TEXT NOT NULL,
                tags TEXT DEFAULT '["payment", "failed"]',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Add tags column if it doesn't exist (migration for existing databases)
        cursor = connection.execute("PRAGMA table_info(analyzed_tickets)")
        columns = {row[1] for row in cursor.fetchall()}
        if "tags" not in columns:
            connection.execute(
                "ALTER TABLE analyzed_tickets ADD COLUMN tags TEXT DEFAULT '[\"payment\", \"failed\"]'"
            )
        connection.commit()


def save_ticket_analysis(ticket: TicketInput, analysis: TicketAnalysisResponse) -> None:
    with get_connection() as connection:
        tags = json.dumps(analysis.tags) if analysis.tags else json.dumps([])
        connection.execute(
            """
            INSERT INTO analyzed_tickets (message, intent, priority, route_to, response, tags)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                ticket.ticket_id,
                analysis.intent,
                analysis.priority,
                analysis.route_to,
                analysis.response,
                tags,
            ),
        )
        connection.commit()


def get_ticket_by_id(ticket_id: str) -> dict | None:
    """Retrieve a single ticket analysis by ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT id, message, intent, priority, route_to, response, tags, created_at FROM analyzed_tickets WHERE message = ?",
            (ticket_id,),
        )
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result['tags'] = json.loads(result['tags']) if result['tags'] else []
            return result
        return None


def get_all_tickets(limit: int = 50, offset: int = 0) -> list[dict]:
    """Retrieve all ticket analyses with pagination."""
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT id, message, intent, priority, route_to, response, tags, created_at FROM analyzed_tickets ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            result['tags'] = json.loads(result['tags']) if result['tags'] else []
            results.append(result)
        return results
