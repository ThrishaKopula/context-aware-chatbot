import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";

export default function Chatbot() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const chatEndRef = useRef(null); // Ref for auto-scrolling

  // Scroll to the latest message whenever messages update
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    localStorage.removeItem("session_id");
    const newSessionId = uuidv4();
    localStorage.setItem("session_id", newSessionId);
    setSessionId(newSessionId);
  }, []);

  const sendMessage = async () => {
    if (sessionId && input.trim() !== "") {
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        session_id: sessionId,
        message: input,
      });

      setMessages([...messages, { user: input, bot: res.data.response }]);
      setInput("");
    }
  };

  if (!sessionId) return <div>Loading...</div>;

  return (
    <div className="chat-container">
      <h1>Welcome to Supportly</h1>
      <div className="chat-card">
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className="message">
              {/* User Label */}
              <div className="user-label">User</div>
              <div className="user-message">{msg.user}</div>

              {/* Bot Label */}
              <div className="bot-label">Bot</div>
              <div className="bot-message">{msg.bot}</div>
            </div>
          ))}
          {/* Invisible div to ensure auto-scroll */}
          <div ref={chatEndRef} />
        </div>

        <div className="chat-input-container">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage();
            }}
            className="chat-input"
            placeholder="Type a message..."
          />
          <button onClick={sendMessage} className="send-button">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
