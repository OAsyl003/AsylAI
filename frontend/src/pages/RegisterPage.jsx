import React from 'react';
import { useNavigate } from 'react-router-dom';
import './SignPage.css';

const API_URL = 'http://localhost:8000';

export default function RegisterPage() {
  const nav = useNavigate();
  const handleSubmit = async e => {
    e.preventDefault();
    const form = new FormData(e.target);
    const data = {
      email: form.get('email'),
      password: form.get('password'),
      first_name: form.get('firstName'),
      last_name: form.get('lastName'),
    };
    const res = await fetch(`${API_URL}/auth/register`, {
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
          <h3 className="title">Register</h3>
          <p className="subtitle">Create your account to get started.</p>
        </div>
        <form className="cardBody" onSubmit={handleSubmit}>
          <div className="inputGroup">
            <label className="inputLabel">First Name</label>
            <input className="input" name="firstName" placeholder="First Name" required />
          </div>
          <div className="inputGroup">
            <label className="inputLabel">Last Name</label>
            <input className="input" name="lastName" placeholder="Last Name" required />
          </div>
          <div className="inputGroup">
            <label className="inputLabel">Email</label>
            <input className="input" type="email" name="email" placeholder="Email" required />
          </div>
          <div className="inputGroup">
            <label className="inputLabel">Password</label>
            <input className="input" type="password" name="password" placeholder="Password" required />
          </div>
          <div className="actions">
            <a className="link" href="/login">Already have an account?</a>
            <button type="submit" className="button">Register</button>
          </div>
        </form>
      </div>
    </div>
  );
}