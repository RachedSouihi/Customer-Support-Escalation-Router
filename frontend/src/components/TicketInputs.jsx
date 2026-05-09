import "./TicketForm.css";

function TicketForm({ ticket, setTicket, onAnalyze, onLoadExample, loading }) {
  const updateField = (field) => (event) => {
    const { value } = event.target;
    setTicket((currentTicket) => ({
      ...currentTicket,
      [field]: value,
    }));
  };

  return (
    <div className="ticket-form">
      <div className="section-title">
        <h2>Ticket Input</h2>
        <button className="ghost-btn" onClick={onLoadExample} type="button">
          Load example
        </button>
      </div>

      <div className="ticket-grid">
        <div className="ticket-field">
          <label htmlFor="subject" className="input-label">
            Subject
          </label>
          <input
            id="subject"
            value={ticket?.subject}
            onChange={updateField("subject")}
            placeholder="Ticket subject"
            className="ticket-input"
          />
        </div>

        <div className="ticket-field">
          <label htmlFor="customer_name" className="input-label">
            Customer name
          </label>
          <input
            id="customer_name"
            value={ticket?.customer_name}
            onChange={updateField("customer_name")}
            placeholder="Alice"
            className="ticket-input"
          />
        </div>

      </div>
      <div className="ticket-grid-1">

        <div className="ticket-field">
          <label htmlFor="customer_tier" className="input-label">
            Customer tier
          </label>
          <input
            id="customer_tier"
            value={ticket?.customer_tier}
            onChange={updateField("customer_tier")}
            placeholder="VIP"
            className="ticket-input"
          />
        </div>


      </div>

      <label htmlFor="body" className="input-label">
        Customer message
      </label>

      <textarea
        id="body"
        value={ticket?.body}
        onChange={updateField("body")}
        placeholder="Paste the customer support request here..."
        className="ticket-textarea"
        rows={10}
      />

      <button
        className="primary-btn"
        onClick={onAnalyze}
        type="button"
        disabled={loading}
      >
        {loading ? "Analyzing..." : "Analyze Ticket"}
      </button>
    </div>
  );
}

export default TicketForm;