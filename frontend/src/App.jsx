import { useState, useRef, useEffect } from "react";
import ChatMessages from "./components/ChatMessages";
import ChatInput from "./components/ChatInput";

function generateId() {
  return crypto?.randomUUID?.() || Math.random().toString(36).substring(2, 10);
}

export default function App() {
  const [chatMessages, setChatMessages] = useState([
    { message: "Hello! Ask me about Nextflow.", sender: "bot", id: generateId() },
  ]);
  const [sessionId, setSessionId] = useState(null);

  const chatWindowRef = useRef(null);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [chatMessages]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    try {
      const userMessage = { message: text, sender: "user", id: generateId() };
      setChatMessages((prev) => [...prev, userMessage]);

      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (!response.ok) throw new Error("Server error");

      const data = await response.json();
      setSessionId(data.session_id);

      const botMessage = { message: data.reply || "No reply", sender: "bot", id: generateId() };
      setChatMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      const errorMsg = { message: "Oops! Something went wrong.", sender: "bot", id: generateId() };
      setChatMessages((prev) => [...prev, errorMsg]);
    }
  };

  return (
    <div className="app-container">
      <h1>Nextflow Chat Assistant</h1>
      <div className="chat-window" ref={chatWindowRef}>
        <ChatMessages chatMessages={chatMessages} />
      </div>
      <ChatInput onSend={sendMessage} />
    </div>
  );
}
