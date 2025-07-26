import React from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🛍️ E-Commerce Customer Support</h1>
        <p>Your AI-powered shopping assistant</p>
      </header>
      <main>
        <ChatInterface />
      </main>
    </div>
  );
}

export default App; 