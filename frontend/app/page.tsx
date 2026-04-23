//instructs Next.js and treats as Client Component (needed for hooks)
"use client";
//hook for functional state management 
import { useState } from "react";
//hook for programmatic navigation 
import { useRouter } from "next/navigation";

export default function ClientChat() {
  // 1. Hooks MUST be at the top level + state initialization 
  //DS: Router objects, handles app's URL syaye and navigation stack 
  const router = useRouter();
  //DS: Array of objects, stores chat conversation
  const [messages, setMessages] = useState([{ role: "ai", text: "Hello! How can I help with your visa?" }]);
  //DS: String, buffer for user's current keystrokes 
  const [input, setInput] = useState("");
  //DS: Boolean, toggle flag for UI visibility 
  const [showLogin, setShowLogin] = useState(false);
  //DS: String, stores sensitive input before verification 
  const [password, setPassword] = useState("");

  //2. ---Login Logic---

  // 2. Separate the Login Logic
  //O(1) String comparison 
  const handleLogin = () => {
    if (password === "issacompassadmin") {
      //pushes '/admin/ onto navigation stack 
      router.push("/admin");
    } else {
      //simple alert blocking UI
      alert("Wrong password!");
    }
  };

  // 3. ---Separate the Chat Logic---
  
  const sendMessage = async () => {
    //checks if string is just whitespace O(1)
    if (!input.trim()) return; // Don't send empty messages

    //DS: Object (snapshot), captures user's message 
    const userMsg = { role: "user", text: input };

    //state update 
    //ALGO: creates shallow copy of the 'prev' array O(N) 
    //React requires NEW memory reference to trigger UI re-render
    //Mutating existing array (prev/push) would fail to update screen 
    setMessages((prev) => [...prev, userMsg]);
    //O(1) sate reset, clears textbox asap for a real chat feel 
    setInput(""); // Clear input immediately for better UX

    try {
      //DS: JSON Body, converting JS Obj --> String for HTTP transport 
      // Call your Flask API
      const response = await fetch("http://localhost:5000/generate-reply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        //History is handled by Flask's global state in thbis version btw 
        body: JSON.stringify({ clientSequence: input, chatHistory: [] })
      });

      //parsing incoming JSON String --> JS Object 
      const data = await response.json();
      console.log("AI Data received: ", data);

      //update UI with AI result 
      setMessages((prev) => [
        ...prev, 
        //object property lookup O(1), fallback string if key missing 
        { role: "ai", text: data.aiReply || "Error: Data has no reply key" }
      ]);
    } catch (error) {
      console.error("Fetch error:", error);
      //error handling, appends system message so user not left hanging 
      setMessages((prev) => [...prev, { role: "ai", text: "Server error. Is Flask running?" }]);
    }
  };

  //---4. RENDER Logig---

  return (
    <div className="flex flex-col h-screen p-4 bg-gray-100">
      <header className="flex items-center justify-between pb-4 border-b mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">🤖</span>
          <h1 className="text-xl font-bold text-gray-800">Issa Compass AI Assistant</h1>
        </div>
        <button 
          onClick={() => setShowLogin(true)} 
          className="text-gray-400 hover:text-blue-600 transition text-sm"
        >
          ⚙️ Admin
        </button>
      </header>

      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={`p-3 rounded-lg max-w-xs ${m.role === "user" ? "ml-auto bg-blue-500 text-white" : "bg-white text-black border shadow-sm"}`}>
            {m.text}
          </div>
        ))}
      </div>

      <div className="flex mt-4">
        <input 
          className="flex-1 p-2 border border-gray-300 rounded-l-md text-black" 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder="Type here..." 
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()} // Optional: Send on Enter key
        />
        <button className="bg-blue-600 text-white px-4 rounded-r-md" onClick={sendMessage}>Send</button>
      </div>

      {showLogin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white p-6 rounded-2xl shadow-xl w-full max-w-sm">
            <h2 className="text-xl font-bold mb-4 text-black">Admin Access</h2>
            <input 
              type="password" 
              className="w-full p-2 border rounded mb-4 text-black" 
              placeholder="Enter Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <div className="flex gap-2">
              <button onClick={handleLogin} className="flex-1 bg-blue-600 text-white p-2 rounded">Login</button>
              <button onClick={() => setShowLogin(false)} className="flex-1 text-black bg-gray-200 p-2 rounded">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
