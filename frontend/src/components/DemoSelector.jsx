import React, { useState, useEffect } from 'react';
import { getDemoTickets, getDemoTicket } from '../services/api';

const DemoSelector = ({ onSelect }) => {
  const [tickets, setTickets] = useState([]);
  const [selectedId, setSelectedId] = useState('');

  useEffect(() => {
    getDemoTickets().then(data => setTickets(data.tickets));
  }, []);

  const handleSelect = async (ticketId) => {
    setSelectedId(ticketId);
    const ticket = await getDemoTicket(ticketId);
    onSelect(ticket);
  };

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h3 className="font-semibold text-blue-900 mb-2">🎯 Quick Demo</h3>
      <select
        value={selectedId}
        onChange={(e) => handleSelect(e.target.value)}
        className="w-full border border-blue-300 rounded-md px-3 py-2 bg-white"
      >
        <option value="">Select a demo ticket...</option>
        {tickets.map(t => (
          <option key={t.id} value={t.id}>{t.subject}</option>
        ))}
      </select>
    </div>
  );
};

export default DemoSelector;