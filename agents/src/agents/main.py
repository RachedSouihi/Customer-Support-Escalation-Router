from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, start

from agents.crew import EscalationCrew

import logging

from dotenv import load_dotenv
load_dotenv(dotenv_path="C:/Users/souih/OneDrive/Bureau/router/.env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)


def extract_from_output(raw_output: str, json_key: str) -> str:
    """
    Extract structured data from agent output (JSON or text).
    
    Tries to parse JSON first (model-agnostic), then falls back to text extraction.
    Works with all models whether they return JSON, think tags, or plain text.
    
    Args:
        raw_output: The raw output from an agent task
        json_key: The JSON key to extract (e.g., "priority", "routing")
        
    Returns:
        The extracted value, stripped of whitespace
    """
    if not raw_output:
        return ""
    
    # Strategy 1: Try to parse as JSON
    try:
        import json
        output_stripped = raw_output.strip()
        
        # If it starts with {, try to parse it as JSON
        if output_stripped.startswith("{"):
            parsed = json.loads(output_stripped)
            if json_key in parsed:
                return str(parsed[json_key]).strip()
        else:
            # Try to find JSON within the text
            start_idx = output_stripped.find("{")
            if start_idx != -1:
                end_idx = output_stripped.rfind("}")
                if end_idx > start_idx:
                    json_str = output_stripped[start_idx:end_idx+1]
                    parsed = json.loads(json_str)
                    if json_key in parsed:
                        return str(parsed[json_key]).strip()
    except (json.JSONDecodeError, ValueError, KeyError):
        pass  # Fall through to text extraction
    
    # Strategy 2: Look for "The final answer is:" marker
    marker = "The final answer is:"
    if marker in raw_output:
        parts = raw_output.split(marker, 1)
        final_answer = parts[1].strip()
        final_answer = final_answer.lstrip("*\n").rstrip("*\n").strip()
        return final_answer
    
    # Strategy 3: Return the last non-empty line (fallback)
    lines = [line.strip() for line in raw_output.split("\n") if line.strip()]
    if lines:
        return lines[-1]
    
    return raw_output.strip()


class TicketState(BaseModel):
    # Include fields that mirror the external TicketInput so Flow.inputs map correctly
    ticket_id: str = ""
    subject: str = ""
    body: str = ""
    customer_name: str = ""
    customer_tier: str = ""

    # Results produced by the flow
    priority: str = ""
    intent: str = ""
    tags: list[str] = Field(default_factory=list)
    routing: str = ""
    response: str = ""
    # Keep a flexible trace field — crews often return raw text
    trace: str = ""
    trace_steps: list[dict[str, str]] = Field(default_factory=list)


def build_trace_steps(
    ticket_id: str,
    classify_raw: str,
    intent: str,
    tags: list[str],
    priority_raw: str,
    priority: str,
    routing_raw: str,
    routing: str,
    response: str,
) -> list[dict[str, str]]:
    steps: list[dict[str, str]] = [
        {
            "agent": "Input received",
            "decision": "completed",
            "details": f"Request accepted for ticket {ticket_id or 'unknown'}.",
            "status": "completed",
        }
    ]

    if classify_raw:
        steps.append(
            {
                "agent": "Classified",
                "decision": "completed",
                "details": f"Intent: {intent or 'unknown'} | Tags: {', '.join(tags) if tags else 'none'} | Raw: {classify_raw}",
                "status": "completed",
            }
        )

    if priority_raw or priority:
        steps.append(
            {
                "agent": "Prioritized",
                "decision": "completed",
                "details": f"Priority: {priority or 'unknown'} | Raw: {priority_raw or priority or 'n/a'}",
                "status": "completed",
            }
        )

    if routing_raw or routing:
        steps.append(
            {
                "agent": "Router",
                "decision": "completed",
                "details": f"Route: {routing or 'unknown'} | Raw: {routing_raw or routing or 'n/a'}",
                "status": "completed",
            }
        )

    if response:
        steps.append(
            {
                "agent": "Response generated",
                "decision": "completed",
                "details": response,
                "status": "completed",
            }
        )

    return steps


class EscalationFlow(Flow[TicketState]):

    @start()
    def run(self):
        crew = EscalationCrew().crew()
        # Pass individual fields that the YAML tasks expect (subject, body, customer_tier)
        logger.info(
            "Running crew with ticket data - subject: %s, body: %s, tier: %s",
            self.state.subject,
            self.state.body,
            self.state.customer_tier,
        )
        
        result = crew.kickoff(inputs={
            "subject": self.state.subject,
            "body": self.state.body,
            "customer_tier": self.state.customer_tier,
            "customer_name": self.state.customer_name,
        })
        
        task_outputs = getattr(result, "tasks_output", []) or []

        classify_raw = ""
        priority_raw = ""
        routing_raw = ""

        # defaults
        intent = ""
        tags: list[str] = []
        priority = ""
        routing = ""
        response = getattr(result, "raw", "") or ""

        if len(task_outputs) > 0:
            classify_raw = (getattr(task_outputs[0], "raw", "") or "").strip()
            # classify_task is expected to return JSON string with "intent"
            try:
                import json
                parsed = json.loads(classify_raw)
                intent = (parsed.get("intent", "") or "").strip()
                raw_tags = parsed.get("tags", [])
                if isinstance(raw_tags, list):
                    tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]
            except Exception:
                # fallback: keep raw if not valid JSON
                intent = classify_raw

        if len(task_outputs) > 1:
            priority_raw = (getattr(task_outputs[1], "raw", "") or "").strip()
            priority = extract_from_output(priority_raw, "priority")

        if len(task_outputs) > 2:
            routing_raw = (getattr(task_outputs[2], "raw", "") or "").strip()
            routing = extract_from_output(routing_raw, "routing")

        if len(task_outputs) > 3:
            response = (getattr(task_outputs[3], "raw", "") or "").strip()

        trace_steps = build_trace_steps(
            ticket_id=self.state.ticket_id,
            classify_raw=classify_raw,
            intent=intent,
            tags=tags,
            priority_raw=priority_raw,
            priority=priority,
            routing_raw=routing_raw,
            routing=routing,
            response=response,
        )

        self.state.intent = intent
        self.state.tags = tags
        self.state.priority = priority
        self.state.routing = routing
        self.state.response = response
        self.state.trace = response
        self.state.trace_steps = trace_steps
        self.state.trace = getattr(result, "raw", "") or response


def run_ticket_flow(inputs: dict) -> TicketState:
    """Helper adapter to run the EscalationFlow from external code.

    `inputs` should be a mapping with any of the TicketState fields (e.g. subject, body,
    ticket_id, customer_tier). Returns the populated `TicketState` after the flow runs.
    """
        
    
    if not is_valid_ticket_data(inputs):
        # Return empty state without running the workflow
        logger.warning("Invalid ticket data provided. Skipping workflow execution.")
        
        return TicketState(
            ticket_id=inputs.get("ticket_id", ""),
            trace="No ticket data provided. Please provide at least 'body' or 'subject'."
        )
        
    logger.info("Valid ticket data found. Executing workflow.")
    flow = EscalationFlow()
    #kickoff populates flow.state from inputs where keys match TicketState fields
    flow.kickoff(inputs=inputs)    
    logger.info(f"Flow completed. Final state: {flow}")
    return flow.state


def kickoff():
    flow = EscalationFlow()
    flow.kickoff(inputs={
        "ticket_text": "customer tier: VIP; subject: URGENT: Payment failed for premium subscription; body: I need help immediately! My payment failed and I can't access my account. This is critical for my business."
    })


def is_valid_ticket_data(inputs: dict) -> bool:
    """Check if ticket data has meaningful content before running the workflow."""
    if not inputs:
        return False
    
    # Check if body (main content) exists and is not empty
    body = inputs.get("body", "").strip()
    subject = inputs.get("subject", "").strip()
    
    # At least body or subject should have content
    return bool(body or subject)


if __name__ == "__main__":
    kickoff()
