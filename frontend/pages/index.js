import { useState, useEffect } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";

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
    <div className="p-4">
      <div className="border p-4 h-96 overflow-auto">
        {messages.map((msg, index) => (
          <p key={index}><b>You:</b> {msg.user}<br /><b>Bot:</b> {msg.bot}</p>
        ))}
      </div>
      <input 
        value={input} 
        onChange={(e) => setInput(e.target.value)} 
        className="border p-2"
      />
      <button onClick={sendMessage} className="bg-blue-500 text-white p-2 ml-2">Send</button>
    </div>
  );
}
