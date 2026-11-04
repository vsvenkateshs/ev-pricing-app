import React, { useState, useEffect } from 'react';
import API from '../api';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

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

  const handleDelete = async (stationId) => {
    if (!window.confirm("Are you sure you want to delete this station?")) return;
    try {
      await API.delete(`/stations/${stationId}`);
      fetchStations(); // Refresh list after deletion
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete station');
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
    <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '0 20px' }}>
      <div className="glass-card">
        <h2 style={{ margin: '0 0 8px 0', color: 'var(--accent-blue)' }}>🏬 Station Owner Game Theory Portal</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
          Manage charging infrastructure and compute Nash Equilibrium pricing across competitor locations.
        </p>

        <h3>Add New Station</h3>
        <form onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
          <input className="input-field" placeholder="Station Name" onChange={e => setForm({...form, name: e.target.value})} required />
          <input className="input-field" placeholder="Location (km)" type="number" onChange={e => setForm({...form, location_km: +e.target.value})} required />
          <input className="input-field" placeholder="Energy Cost (eta)" type="number" step="0.01" onChange={e => setForm({...form, energy_cost_eta: +e.target.value})} required />
          <input className="input-field" placeholder="Wait Time (hr)" type="number" step="0.01" onChange={e => setForm({...form, expected_wait_hr: +e.target.value})} required />
          <input className="input-field" placeholder="Terminal Cost" type="number" onChange={e => setForm({...form, terminal_cost: +e.target.value})} required />
          <button type="submit" className="btn-success" style={{ gridColumn: '1 / -1' }}>
            Add Charging Station
          </button>
        </form>
      </div>

      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ margin: 0 }}>Registered Network Stations</h3>
          <button onClick={runPricingGame} className="btn-primary">
            Run Nash Equilibrium Solver (Algorithm 2)
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
          {stations.map(s => (
            <div key={s.id} style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', position: 'relative' }}>
              <h4 style={{ margin: '0 0 8px 0' }}>{s.name}</h4>
              <p style={{ margin: '4px 0', fontSize: '14px', color: 'var(--text-muted)' }}>Location: {s.location_km} km</p>
              <p style={{ margin: '4px 0', fontSize: '18px', fontWeight: 'bold', color: 'var(--accent-green)' }}>
                Published: ${s.published_price} / kWh
              </p>

              {/* Delete Button */}
              <button 
                onClick={() => handleDelete(s.id)}
                style={{
                  marginTop: '12px',
                  width: '100%',
                  background: 'rgba(239, 68, 68, 0.2)',
                  color: '#ef4444',
                  border: '1px solid #ef4444',
                  padding: '8px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                Delete Station
              </button>
            </div>
          ))}
        </div>
      </div>

      {results.length > 0 && (
        <div className="glass-card">
          <h3>Nash Equilibrium Price vs. Station Location</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <LineChart data={results}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="location_km" stroke="#94a3b8" label={{ value: 'Highway Location (km)', position: 'insideBottom', offset: -5 }} />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                <Line type="monotone" dataKey="ne_price" name="Equilibrium Price ($)" stroke="#38bdf8" strokeWidth={3} />
                <Line type="monotone" dataKey="ne_profit" name="Predicted Profit ($)" stroke="#22c55e" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}