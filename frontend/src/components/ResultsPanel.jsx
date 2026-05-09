import "./ResultsPanel.css";
import StatusBadge from "./StatusBagge";
import AgentTrace from "./AgentTrace";

function formatText(value) {
  return String(value || "")
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function ResultsPanel({ result, loading }) {
  const intent = result?.intent ?? result?.category ?? "";
  const tags = Array.isArray(result?.tags)
    ? result.tags
    : Array.isArray(result?.classification?.tags)
      ? result.classification.tags
      : [];
  const priority = result?.priority ?? "";
  const routeTo = result?.route_to ?? result?.routing_decision ?? "";
  const responseText = result?.response ?? result?.response_text ?? "";

  return (
    <div className="results-panel">

      <h2>Analysis Result</h2>

      {loading && (
        <>
          <div className="placeholder-card">
            Running the agent workflow...
          </div>
         
        </>
      )}

      {!loading && !result && (
        <div className="placeholder-card">
          Your ticket analysis will appear here.
        </div>
      )}

      {result && (
        <div className="result-content">
          <div className="summary-grid">
            <div className="summary-card summary-card-intent">
              <div className="label">Intent</div>
              <div className="value value-emphasis">{formatText(intent)}</div>
              {tags.length > 0 && (
                <div className="tag-wrap" aria-label="Classifier tags">
                  {tags.map((tag) => (
                    <span key={tag} className="tag-chip">
                      {formatText(tag)}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="summary-card summary-card-priority">
              <div className="label">Priority</div>
              <StatusBadge priority={priority} />
              <div className="summary-note">Escalation level determined by the workflow.</div>
            </div>
          </div>

          <div className="summary-card summary-card-route">
            <div className="label">Route To</div>
            <div className="value">{formatText(routeTo)}</div>
          </div>

          <div>
            <div className="label">Generated Response</div>
            <div className="response-box">{responseText}</div>
          </div>

        </div>
      )}
    </div>
  );
}

export default ResultsPanel;