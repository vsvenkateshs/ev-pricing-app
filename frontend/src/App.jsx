import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import StationDashboard from './pages/StationDashboard';
import EVDashboard from './pages/EVDashboard';

export default function App() {
  const [auth, setAuth] = useState({
    token: localStorage.getItem('token'),
    role: localStorage.getItem('role')
  });

  const handleLogout = () => {
    localStorage.clear();
    setAuth({ token: null, role: null });
  };

  return (
    <BrowserRouter>
      {auth.token && (
        <div style={{ background: '#333', color: '#fff', padding: '10px 20px', display: 'flex', justifyContent: 'space-between' }}>
          <span>Logged in as <b>{auth.role}</b></span>
          <button onClick={handleLogout} style={{ background: '#ff4d4f', color: '#fff', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}>
            Logout
          </button>
        </div>
      )}
      <Routes>
        <Route path="/" element={<Login setAuth={setAuth} />} />
        <Route path="/station-dashboard" element={auth.token ? <StationDashboard /> : <Navigate to="/" />} />
        <Route path="/ev-dashboard" element={auth.token ? <EVDashboard /> : <Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}