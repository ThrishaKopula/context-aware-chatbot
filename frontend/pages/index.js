import { useState, useEffect } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import "../style/chatbot.css";

export default function Chatbot() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  // Run only on client-side after the component mounts
  useEffect(() => {
    // Clear localStorage on page refresh
    localStorage.removeItem("session_id");

    // Create a new session ID and store it in localStorage
    const newSessionId = uuidv4();
    localStorage.setItem("session_id", newSessionId);
    setSessionId(newSessionId);
  }, []); // Empty dependency array to run this once when the component mounts

  const sendMessage = async () => {
    if (sessionId) {
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        session_id: sessionId,
        text: input,
      });

      setMessages([...messages, { user: input, bot: res.data.response }]);
      setInput("");
    }
  };

  if (!sessionId) return <div>Loading...</div>; // Show loading state while sessionId is being set

  return (
    <div className="chat-container">
      {/* Chat Card */}
      <div className="chat-card">
        {/* Chat Messages */}
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className="message">
              {/* User Message */}
              <div className="user-message">{msg.user}</div>
              {/* Bot Message */}
              <div className="bot-message">{msg.bot}</div>
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div className="chat-input-container">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
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
