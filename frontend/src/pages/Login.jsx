import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api';

export default function Login({ setAuth }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('station_owner');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await API.post('/auth/register', { email, password, role });
        setIsRegister(false);
        alert('Registration successful! Please login.');
      } else {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        const res = await API.post('/auth/login', formData);
        
        localStorage.setItem('token', res.data.access_token);
        localStorage.setItem('role', res.data.role);
        setAuth({ token: res.data.access_token, role: res.data.role });

        if (res.data.role === 'station_owner') {
          navigate('/station-dashboard');
        } else {
          navigate('/ev-dashboard');
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2>{isRegister ? 'Register Account' : 'Login'}</h2>
        {error && <p style={styles.error}>{error}</p>}
        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={styles.input}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={styles.input}
          />
          {isRegister && (
            <select value={role} onChange={(e) => setRole(e.target.value)} style={styles.input}>
              <option value="station_owner">Station Owner</option>
              <option value="ev_owner">EV Owner</option>
            </select>
          )}
          <button type="submit" style={styles.button}>
            {isRegister ? 'Sign Up' : 'Log In'}
          </button>
        </form>
        <button onClick={() => setIsRegister(!isRegister)} style={styles.toggleBtn}>
          {isRegister ? 'Already have an account? Login' : "Don't have an account? Register"}
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' },
  card: { background: '#fff', padding: '30px', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '350px' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  input: { padding: '10px', fontSize: '14px', borderRadius: '4px', border: '1px solid #ccc' },
  button: { padding: '12px', background: '#0070f3', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  toggleBtn: { marginTop: '15px', background: 'none', border: 'none', color: '#0070f3', cursor: 'pointer' },
  error: { color: 'red', fontSize: '13px' }
};