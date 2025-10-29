import React from 'react';
import { useNavigate } from 'react-router-dom';
import './SignPage.css';

const API_URL = 'http://localhost:8000';

export default function LoginPage() {
  const nav = useNavigate();
  const handleSubmit = async e => {
    e.preventDefault();
    const form = new FormData(e.target);
    const data = {
      email: form.get('username'),
      password: form.get('password'),
    };
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    const { access_token } = await res.json();
    localStorage.setItem('token', access_token);
    nav('/chat');
  };

  return (
    <div className="signpage">
      <div className="card">
        <div className="cardHeader">
          <h3 className="title">Login</h3>
          <p className="subtitle">Welcome back, enter your credentials.</p>
        </div>
        <form className="cardBody" onSubmit={handleSubmit}>
          <div className="inputGroup">
            <label className="inputLabel">Email</label>
            <input className="input" type="email" name="username" placeholder="Email" required />
          </div>
          <div className="inputGroup">
            <label className="inputLabel">Password</label>
            <input className="input" type="password" name="password" placeholder="Password" required />
          </div>
          <div className="actions">
            <a className="link" href="/frontend/src/pages/RegisterPage">Register</a>
            <button type="submit" className="button">Log in</button>
          </div>
        </form>
      </div>
    </div>
  );
}