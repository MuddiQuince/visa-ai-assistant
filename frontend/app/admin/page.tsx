//THE ADMIN PAGE - https://localhost:3000/admin

"use client"; //Client Component to allow hooks like useState and useEffect
import { useState, useEffect } from "react";

interface ChatLog {
  role: string;
  text: string;
}

export default function AdminDashboard() {
  //state for text area input
  const [feedback, setFeedback] = useState("");
  //state for visual status message (ex: 'Improving AI logic.."")
  const [status, setStatus] = useState("AI is currently using standard rules.");
  //state to store array of msgs fetched from Flask backend
  const [logs, setLogs] = useState<ChatLog[]>([]); // State to hold chat history

  //1. Fetch latest live logs from Flask backend
  const fetchLogs = async () => {
    try {
      const response = await fetch("http://localhost:5000/get-logs"); // Ensure this endpoint exists in Flask
      const data = await response.json();
      //update state with history from backend, default to empty array if NULL
      setLogs(data.history || []);
    } catch (err) {
      console.error("Failed to fetch logs:", err);
    }
  };

  //Runs once when page loads 
  useEffect(() => {
    fetchLogs();
    //request fresh logs every 5 secs to simulate 'live; feed
    const interval = setInterval(fetchLogs, 5000); // Auto-refresh every 5 seconds
    //cleanup function: stops timer when user leaves
    return () => clearInterval(interval);
  }, []);

  //Handles "Push Update" button
  const handleImprove = async () => {
    if (!feedback.trim()) return alert("Please enter an instruction.");
    
    setStatus("Improving AI logic...");
    try {
      //POST the manual instructions to the backend
      const response = await fetch("http://localhost:5000/improve-ai-manually", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ instructions: feedback })
      });
      const data = await response.json();
      if(response.ok){
        //Show success message and a snippet of the new prompt
        setStatus("Success! New Prompt: " + (data.updatedPrompt?.substring(0, 50) || "Updated") + "...");
        setFeedback(""); // Clear input after success
      }
    } catch (err) {
      setStatus("Error updating AI logic.");
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* LEFT: Live Conversation Monitor */}
      <div className="w-1/2 bg-white border-r flex flex-col">
        <div className="p-6 border-b flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-800">Live Monitor</h2>
          <span className="flex items-center text-xs text-green-500 font-mono">
            <span className="animate-ping inline-block w-2 h-2 rounded-full bg-green-400 mr-2"></span>
            LIVE
          </span>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {logs.length === 0 ? (
            <p className="text-gray-400 italic">Waiting for incoming messages...</p>
          ) : (
            logs.map((log, i) => (
              <div key={i} className={`p-3 rounded-lg border ${log.role === 'user' ? 'bg-blue-50 border-blue-100' : 'bg-gray-50'}`}>
                <span className="text-[10px] uppercase font-bold text-gray-400">{log.role}</span>
                <p className="text-sm text-gray-800">{log.text}</p>
              </div>
            ))
          )}
        </div>
      </div>

      {/* RIGHT: Training & Prompt Control (where user trains the AI) */}
      <div className="w-1/2 bg-slate-900 text-white p-8 flex flex-col">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-green-400 mb-2 underline decoration-green-500/30">
            AI Response Training
          </h2>
          <p className="text-slate-400 text-sm">Update the system instructions in real-time.</p>
        </div>

          {/* Dynamic Status Box */}
        <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 mb-6">
          <p className="text-xs font-mono text-slate-500 mb-2">SYSTEM STATUS</p>
          <p className="text-sm font-medium text-blue-300 italic">"{status}"</p>
        </div>
        
        <label className="text-xs font-bold text-slate-500 mb-2 uppercase tracking-widest">
          Manual Instruction Injector
        </label>
        <textarea 
          className="w-full h-48 p-4 bg-slate-950 text-green-50 border border-slate-700 rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition-all font-mono text-sm" 
          placeholder="Example: 'If the user asks about the O-A visa, tell them they need 800,000 THB in a Thai bank account.'"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
        />
        
        <button 
          className="mt-6 w-full bg-green-600 hover:bg-green-500 active:scale-[0.98] transition-all text-white p-4 rounded-xl font-bold shadow-lg shadow-green-900/20"
          onClick={handleImprove}
        >
          Push Update to AI Node
        </button>

        <div className="mt-auto pt-6 border-t border-slate-800">
          <p className="text-[10px] text-slate-600 text-center uppercase tracking-tighter">
            Visa Assistant Admin Console v1.2
          </p>
        </div>
      </div>
    </div>
  );
}