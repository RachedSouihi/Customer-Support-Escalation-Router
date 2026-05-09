import { useState } from "react";
import "./App.css";
import Header from "./components/Header";
import TicketForm from "./components/TicketInputs";
import ResultsPanel from "./components/ResultsPanel";
import { processTicket } from "./services/api";
import AgentTrace from "./components/AgentTrace"



function App() {
  const [ticket, setTicket] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (!ticket.body.trim()) {
      setError("Please enter a customer message.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
     
        const data = await processTicket(ticket);
        setResult(data);
      
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };
  const handleLoadExample = () => {
    setTicket(DEFAULT_TICKET);
    setResult(DEFAULT_RESPONSE);
    setError("");
  };

  return (
    <div className="app-shell">
      <Header />

      <main className="app-container">
        <section className="grid-layout">
          <div className="panel">
            <TicketForm
              ticket={ticket}
              setTicket={setTicket}
              onAnalyze={handleAnalyze}
              onLoadExample={handleLoadExample}
              loading={loading}
            />

            {error && <div className="error-box">{error}</div>}
          </div>

          <div className="panel">
            <ResultsPanel result={result} loading={loading} />
          </div>
        </section>

        <section className="trace-panel">
          <AgentTrace result={result} loading={loading} />
        </section>
      </main>
    </div>
  );
}


export default App