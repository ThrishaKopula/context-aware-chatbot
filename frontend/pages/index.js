import { useState } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";

export default function Chatbot() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const sessionId = uuidv4(); // Unique session ID

  const sendMessage = async () => {
    const res = await axios.post("http://127.0.0.1:8000/chat", {
      session_id: sessionId,
      text: input,
    });

    setMessages([...messages, { user: input, bot: res.data.response }]);
    setInput("");
  };

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
