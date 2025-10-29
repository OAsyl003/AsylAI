import React, { useState, useRef, useEffect } from 'react';
import './Chat.css';

const API_URL = 'http://localhost:8000';
function getToken() { return localStorage.getItem('token'); }

export default function Chat() {
  const [messages, setMessages] = useState([]);   // здесь и хранится история
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const endRef = useRef(null);

  // 1) Подгружаем историю
  useEffect(() => {
    (async () => {
      const token = getToken();
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;
      try {
        const res = await fetch(`${API_URL}/chat/history`, { headers });
        if (res.ok) {
          const history = await res.json();
          setMessages(history);
        }
      } catch (err) {
        console.error('Не удалось загрузить историю чата', err);
      }
    })();
  }, []);

  // 2) Автоскролл вниз
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const text = input.trim(); setInput('');
    // добавляем user+assistant placeholder
    setMessages(m => [...m, { sender: 'user', text }, { sender: 'assistant', text: '' }]);
    setIsLoading(true);

    try {
      const token = getToken();
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const res = await fetch(`${API_URL}/chat/stream`, {
        method: 'POST', headers, body: JSON.stringify({ message: text })
      });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantText = '';
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        assistantText += decoder.decode(value, { stream: true });
        setMessages(prev => {
          const msgs = [...prev];
          msgs[msgs.length-1] = { sender: 'assistant', text: assistantText };
          return msgs;
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((m,i) => (
          <div key={i} className={`message ${m.sender}`}>{m.text}</div>
        ))}
        <div ref={endRef}/>
      </div>
      <div className="input-area">
        <textarea
          value={input}
          onChange={e=>setInput(e.target.value)}
          rows={2}
        />
        <button onClick={handleSend} disabled={isLoading}>
          {isLoading ? 'Загружаю…' : 'Отправить'}
        </button>
      </div>
    </div>
  );
}
