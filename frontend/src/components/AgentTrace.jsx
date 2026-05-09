import "./AgentTrace.css";

function AgentTrace({ result, loading }) {
  const steps = [
    "Input received",
    "Classified",
    "Prioritized",
    "Routed",
    "Response generated",
  ];
  const trace = Array.isArray(result?.trace) ? result.trace : [];
  const completedCount = trace.length;
  const progressValue =
    loading && completedCount === 0 ? 18 : (completedCount / steps.length) * 100;

  return (
    <div className="agent-trace card-shell">
      <div className="trace-header">
        <div>
          <h2>Agent Trace</h2>
          <p className="trace-subtitle">
            A step-by-step view of the workflow as the analysis completes.
          </p>
        </div>
        <div className="trace-pill">
          {completedCount}/{steps.length} complete
        </div>
      </div>

      <div className="progress-shell" aria-label="Workflow progress">
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{ width: `${Math.max(0, Math.min(100, progressValue))}%` }}
          />
        </div>
      </div>

      <div className="trace-flow">
        {steps.map((step, index) => {
          const traceItem = trace[index];
          const isComplete = index < completedCount;
          const isCurrent =
            loading && index === Math.min(completedCount, steps.length - 1) && completedCount < steps.length;

          return (
            <div
              key={step}
              className={`trace-step ${isComplete ? "complete" : ""} ${isCurrent ? "current" : ""}`}
            >
              <div className="step-row">
                <div className="step-dot">{index + 1}</div>
                <div>
                  <div className="step-label">{step}</div>
                  <div className="step-state">
                    {isComplete ? "Completed" : loading ? "Running" : "Waiting"}
                  </div>
                </div>
              </div>

              <div className="step-details">
                {(isComplete ? "Completed successfully." : "Waiting for the workflow to reach this stage.")}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default AgentTrace;