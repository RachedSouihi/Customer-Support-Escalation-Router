const API_BASE = 'http://localhost:8000';

export async function processTicket(ticketData) {
  const response = await fetch(`${API_BASE}/analyze-ticket`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(ticketData)
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}
