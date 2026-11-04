import React, { useState, useEffect } from 'react';
import API from '../api';

export default function StationDashboard() {
  const [stations, setStations] = useState([]);
  const [results, setResults] = useState([]);
  const [form, setForm] = useState({
    name: '', location_km: 10, energy_cost_eta: 0.05, expected_wait_hr: 0.2, terminal_cost: 10
  });

  const fetchStations = async () => {
    try {
      const res = await API.get('/stations/my');
      setStations(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => { fetchStations(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await API.post('/stations', form);
      fetchStations();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to add station');
    }
  };

  const runPricingGame = async () => {
    try {
      const res = await API.post('/pricing/run');
      setResults(res.data.results);
      fetchStations();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to solve Nash equilibrium');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>Station Owner Dashboard</h2>
      
      <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
        <h3>Add New Charging Station</h3>
        <form onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <input placeholder="Name" onChange={e => setForm({...form, name: e.target.value})} required />
          <input placeholder="Location (km)" type="number" onChange={e => setForm({...form, location_km: +e.target.value})} required />
          <input placeholder="Energy Cost (eta)" type="number" step="0.01" onChange={e => setForm({...form, energy_cost_eta: +e.target.value})} required />
          <input placeholder="Wait Time (hr)" type="number" step="0.01" onChange={e => setForm({...form, expected_wait_hr: +e.target.value})} required />
          <input placeholder="Terminal Cost" type="number" onChange={e => setForm({...form, terminal_cost: +e.target.value})} required />
          <button type="submit" style={{ gridColumn: 'span 2', padding: '10px', background: '#28a745', color: '#fff', border: 'none', borderRadius: '4px' }}>
            Add Station
          </button>
        </form>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>My Stations</h3>
        <button onClick={runPricingGame} style={{ padding: '10px 20px', background: '#0070f3', color: '#fff', border: 'none', borderRadius: '4px', marginBottom: '10px' }}>
          Run Nash Pricing Game (Algorithm 2)
        </button>
        <ul>
          {stations.map(s => (
            <li key={s.id}>
              <b>{s.name}</b> @ {s.location_km} km | Published Price: <b>${s.published_price}/kWh</b>
            </li>
          ))}
        </ul>
      </div>

      {results.length > 0 && (
        <div style={{ background: '#e6f7ff', padding: '15px', borderRadius: '8px' }}>
          <h3>Equilibrium Results</h3>
          {results.map(r => (
            <p key={r.station_id}>
              <b>{r.name}:</b> NE Price = ${r.ne_price}/kWh | Profit = ${r.ne_profit}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}