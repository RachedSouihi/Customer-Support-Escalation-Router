import json
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task


# ============================================================================
# Output Guardrails — Validate agent output format and quality
# ============================================================================

def validate_classify_output(output) -> tuple[bool, str]:
    """
    Validate classifier output is valid JSON with required keys.
    Returns (True, output) if valid, (False, error_msg) if invalid.
    """
    try:
        # Handle TaskOutput object from CrewAI
        output_str = str(output) if not isinstance(output, str) else output
        data = json.loads(output_str)
        required_keys = {"intent", "tags", "confidence"}
        if not all(key in data for key in required_keys):
            return False, f"Missing required keys. Expected {required_keys}, got {set(data.keys())}"
        if not isinstance(data["tags"], list):
            return False, "Field 'tags' must be a list"
        if not isinstance(data["confidence"], (int, float)) or not (0.0 <= data["confidence"] <= 1.0):
            return False, "Field 'confidence' must be a number between 0.0 and 1.0"
        return True, output_str
    except json.JSONDecodeError as e:
        return False, f"Output is not valid JSON: {e}"


def validate_priority_output(output) -> tuple[bool, str]:
    """
    Validate prioritizer output is valid JSON with priority in {Low, Medium, High}.
    """
    try:
        # Handle TaskOutput object from CrewAI
        output_str = str(output) if not isinstance(output, str) else output
        data = json.loads(output_str)
        if "priority" not in data:
            return False, "Missing required key 'priority'"
        priority = data["priority"]
        valid_priorities = {"Low", "Medium", "High"}
        if priority not in valid_priorities:
            return False, f"Priority must be one of {valid_priorities}, got '{priority}'"
        return True, output_str
    except json.JSONDecodeError as e:
        return False, f"Output is not valid JSON: {e}"


def validate_routing_output(output) -> tuple[bool, str]:
    """
    Validate router output is valid JSON with routing in {human, auto}.
    """
    try:
        # Handle TaskOutput object from CrewAI
        output_str = str(output) if not isinstance(output, str) else output
        data = json.loads(output_str)
        if "routing" not in data:
            return False, "Missing required key 'routing'"
        routing = data["routing"]
        valid_routings = {"human", "auto"}
        if routing not in valid_routings:
            return False, f"Routing must be one of {valid_routings}, got '{routing}'"
        return True, output_str
    except json.JSONDecodeError as e:
        return False, f"Output is not valid JSON: {e}"


def validate_response_output(output) -> tuple[bool, str]:
    """
    Validate responder output contains no internal metadata (JSON, confidence, routing tags).
    """
    # Handle TaskOutput object from CrewAI
    output_str = str(output) if not isinstance(output, str) else output
    
    try:
        # Reject if output is JSON (should be plain text)
        json.loads(output_str)
        return False, "Response must be plain text, not JSON"
    except json.JSONDecodeError:
        # Good — output is not JSON
        pass

    # Check for internal metadata leakage and any attempt to solicit PII/confidential data
    forbidden_terms = ["confidence", "routing", "intent:", "priority:", "internal", "json"]
    pii_terms = ["ssn", "social security", "social-security", "card number", "credit card", "cvv", "cvc", "security code", "pin", "password", "account number", "routing number"]
    output_lower = output_str.lower()
    found_terms = [term for term in forbidden_terms if term in output_lower]
    found_pii = [term for term in pii_terms if term in output_lower]
    if found_terms:
        return False, f"Response contains internal metadata: {found_terms}"
    if found_pii:
        return False, f"Response attempts to solicit confidential/PII data: {found_pii}"

    # Check for minimum length
    if len(output_str.strip()) < 10:
        return False, "Response is too short (minimum 10 characters)"

    return True, output_str


@CrewBase
class EscalationCrew:
    """Escalation crew wiring classifier → prioritizer → router → responder."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def classifier(self) -> Agent:
        return Agent(config=self.agents_config["classifier"])  # type: ignore[index]

    @agent
    def prioritizer(self) -> Agent:
        return Agent(config=self.agents_config["prioritizer"])  # type: ignore[index]

    @agent
    def router(self) -> Agent:
        return Agent(config=self.agents_config["router"])  # type: ignore[index]

    @agent
    def responder(self) -> Agent:
        return Agent(config=self.agents_config["responder"])  # type: ignore[index]

    @task
    def classify_task(self) -> Task:
        task = Task(config=self.tasks_config["classify_task"])  # type: ignore[index]
        #task.guardrails = [validate_classify_output]
        return task

    @task
    def priority_task(self) -> Task:
        task = Task(config=self.tasks_config["priority_task"])  # type: ignore[index]
        #task.guardrails = [validate_priority_output]
        return task

    @task
    def route_task(self) -> Task:
        task = Task(config=self.tasks_config["route_task"])  # type: ignore[index]
        #task.guardrails = [validate_routing_output]
        return task

    @task
    def respond_task(self) -> Task:
        task = Task(config=self.tasks_config["respond_task"])  # type: ignore[index]
        #task.guardrails = [validate_response_output]
        return task

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
