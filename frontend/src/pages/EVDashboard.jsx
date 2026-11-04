import React, { useState } from 'react';
import API from '../api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function EVDashboard() {
  const [form, setForm] = useState({
    location_km: 25,
    energy_kwh: 40,
    travel_cost_per_km: 0.15,
    waiting_cost_per_hr: 5.0,
    battery_soc: 0.18,
    battery_capacity_kwh: 60,
    energy_consumption_per_km: 0.18,
    anxiety_weight: 2.5
  });
  const [rankings, setRankings] = useState([]);

  const handleRecommend = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post('/ev/recommend', form);
      setRankings(res.data.rankings);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to fetch recommendations');
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '0 20px' }}>
      <div className="glass-card">
        <h2 style={{ margin: '0 0 8px 0', color: 'var(--accent-blue)' }}>⚡ EV Driver Smart Station Selector</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
          Find optimal charging stations balancing travel costs, queue times, and real-time range anxiety algorithms.
        </p>

        <form onSubmit={handleRecommend} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Location (Highway km)</label>
            <input className="input-field" type="number" value={form.location_km} onChange={e => setForm({...form, location_km: +e.target.value})} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Energy Needed (kWh)</label>
            <input className="input-field" type="number" value={form.energy_kwh} onChange={e => setForm({...form, energy_kwh: +e.target.value})} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Travel Cost ($/km)</label>
            <input className="input-field" type="number" step="0.01" value={form.travel_cost_per_km} onChange={e => setForm({...form, travel_cost_per_km: +e.target.value})} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Waiting Cost ($/hr)</label>
            <input className="input-field" type="number" step="0.1" value={form.waiting_cost_per_hr} onChange={e => setForm({...form, waiting_cost_per_hr: +e.target.value})} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Battery Charge (SoC %)</label>
            <input className="input-field" type="number" step="0.01" value={form.battery_soc} onChange={e => setForm({...form, battery_soc: +e.target.value})} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Anxiety Tolerance Factor</label>
            <input className="input-field" type="number" step="0.1" value={form.anxiety_weight} onChange={e => setForm({...form, anxiety_weight: +e.target.value})} />
          </div>
          
          <button type="submit" className="btn-primary" style={{ gridColumn: '1 / -1', marginTop: '10px' }}>
            Calculate Optimal Stations (Algorithm 1)
          </button>
        </form>
      </div>

      {rankings.length > 0 && (
        <>
          {/* Cost Comparison Visual Chart */}
          <div className="glass-card">
            <h3 style={{ marginBottom: '16px' }}>Cost Breakdown Visualizer</h3>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <BarChart data={rankings}>
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                  <Legend />
                  <Bar dataKey="energy_service_cost" name="Energy ($)" fill="#38bdf8" stackId="a" />
                  <Bar dataKey="travel_cost" name="Travel ($)" fill="#818cf8" stackId="a" />
                  <Bar dataKey="waiting_cost" name="Wait ($)" fill="#f59e0b" stackId="a" />
                  <Bar dataKey="anxiety_penalty" name="Anxiety ($)" fill="#ef4444" stackId="a" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Cards List */}
          <div>
            <h3>Ranked Stations</h3>
            {rankings.map((r, index) => (
              <div 
                key={r.station_id} 
                className="glass-card" 
                style={{ 
                  borderColor: index === 0 ? 'var(--accent-green)' : 'var(--border-color)',
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                {index === 0 && (
                  <span style={{
                    position: 'absolute', top: 0, right: 0,
                    background: 'var(--accent-green)', color: '#fff',
                    padding: '4px 16px', fontSize: '12px', fontWeight: 'bold',
                    borderBottomLeftRadius: '10px'
                  }}>
                    RECOMMENDED CHOICE
                  </span>
                )}

                <h3 style={{ margin: '0 0 10px 0' }}>{r.name}</h3>
                <p style={{ fontSize: '20px', fontWeight: 'bold', margin: '0 0 10px 0', color: 'var(--accent-blue)' }}>
                  Total Effective Cost: ${r.total_cost}
                </p>
                <p style={{ margin: '4px 0', fontSize: '14px', color: 'var(--text-muted)' }}>
                  Distance: <b>{r.distance_km} km</b> | Traffic Congestion: <b>{r.congestion_index}</b>
                </p>
                <div style={{ marginTop: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  <span style={{ background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', padding: '4px 8px', borderRadius: '6px', fontSize: '12px' }}>
                    Energy: ${r.energy_service_cost}
                  </span>
                  <span style={{ background: 'rgba(129, 140, 248, 0.1)', color: '#818cf8', padding: '4px 8px', borderRadius: '6px', fontSize: '12px' }}>
                    Travel: ${r.travel_cost}
                  </span>
                  <span style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', padding: '4px 8px', borderRadius: '6px', fontSize: '12px' }}>
                    Wait: ${r.waiting_cost}
                  </span>
                  <span style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '4px 8px', borderRadius: '6px', fontSize: '12px' }}>
                    Range Anxiety: +${r.anxiety_penalty}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}