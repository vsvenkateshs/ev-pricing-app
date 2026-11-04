import React, { useState } from 'react';
import API from '../api';

export default function EVDashboard() {
  const [form, setForm] = useState({
    location_km: 25, energy_kwh: 40, travel_cost_per_km: 0.15, waiting_cost_per_hr: 5.0
  });
  const [rankings, setRankings] = useState([]);

  const handleRecommend = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post('/ev/recommend', form);
      setRankings(res.data.rankings);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to fetch recommendation');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>EV Owner - Find Best Charging Station</h2>
      <form onSubmit={handleRecommend} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' }}>
        <div>
          <label>Location on Highway (km):</label>
          <input type="number" value={form.location_km} onChange={e => setForm({...form, location_km: +e.target.value})} />
        </div>
        <div>
          <label>Energy Needed (kWh):</label>
          <input type="number" value={form.energy_kwh} onChange={e => setForm({...form, energy_kwh: +e.target.value})} />
        </div>
        <div>
          <label>Travel Cost ($/km):</label>
          <input type="number" step="0.01" value={form.travel_cost_per_km} onChange={e => setForm({...form, travel_cost_per_km: +e.target.value})} />
        </div>
        <div>
          <label>Waiting Cost ($/hr):</label>
          <input type="number" step="0.1" value={form.waiting_cost_per_hr} onChange={e => setForm({...form, waiting_cost_per_hr: +e.target.value})} />
        </div>
        <button type="submit" style={{ gridColumn: 'span 2', padding: '12px', background: '#0070f3', color: '#fff', border: 'none', borderRadius: '4px' }}>
          Find Cheapest Station (Algorithm 1)
        </button>
      </form>

      {rankings.length > 0 && (
        <div>
          <h3>Ranked Recommendations</h3>
          {rankings.map((r, index) => (
            <div key={r.station_id} style={{
              background: index === 0 ? '#e6ffed' : '#fff',
              border: index === 0 ? '2px solid #28a745' : '1px solid #ccc',
              padding: '15px', borderRadius: '8px', marginBottom: '10px'
            }}>
              <h4>{index === 0 ? '🏆 Best Choice: ' : ''}{r.name}</h4>
              <p>Total Cost: <b>${r.total_cost}</b> (Distance: {r.distance_km} km)</p>
              <p style={{ fontSize: '12px', color: '#555' }}>
                Energy & Service: ${r.energy_service_cost} | Travel: ${r.travel_cost} | Waiting: ${r.waiting_cost}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}