<<<<<<< HEAD
import { useState } from 'react';
=======
import { useState,useEffect,useRef } from 'react';
import UploadForm from './components/UploadForm';
>>>>>>> dc859da567c64e28f84fe9440a8767500577c11e

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
<<<<<<< HEAD
  const [analysisData, setAnalysisData] = useState(null);
  
  // Quiz State
  const [activeQuestionIndex, setActiveQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState("");
  const [showTrace, setShowTrace] = useState(false);

  // Ask Engine State
  const [query, setQuery] = useState("");
  const [format, setFormat] = useState("paragraph");
  const [askResponse, setAskResponse] = useState("");

  // --- API CALLS ---
  const handleUploadAndAnalyze = async () => {
    if (!file) return alert("Please select a file first!");
=======
  const messagesEndRef = useRef(null);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };
  useEffect(() => {
  messagesEndRef.current?.scrollIntoView({
    behavior: "smooth",
  });
}, [chatHistory, loading]);

  const handleTransmit = async () => {
    if( query.trim() === '') return;
    
    const userMessage = query;
    setChatHistory((prev) => [...prev, { sender: 'user', text: userMessage }]);
    setQuery('');
>>>>>>> dc859da567c64e28f84fe9440a8767500577c11e
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // 1. Upload the File
      await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
<<<<<<< HEAD

      // 2. Fetch the Analysis (Summary + Quiz)
      const res = await fetch("http://localhost:8000/analyze");
      const data = await res.json();
      setAnalysisData(data);
=======
      
      const data = await response.json();
      
      setChatHistory((prev) => [
        ...prev,
        {
          sender: 'system',
          text: data.answer || 'Error interpreting return stream.',
          sources: data.sources || [],
          relationships: data.relationships || []
        }
      ]);
>>>>>>> dc859da567c64e28f84fe9440a8767500577c11e
    } catch (error) {
      console.error("Pipeline Error:", error);
      alert("Failed to connect to backend. Is FastAPI running?");
    }
    setLoading(false);
  };

  const handleAskEngine = async () => {
    if (!query) return;
    setAskResponse("Analyzing document...");
    
    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query, format_preference: format })
      });
      const data = await res.json();
      setAskResponse(data.answer || "No response generated.");
    } catch (error) {
      setAskResponse("Error reaching the Ask endpoint.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-8 font-sans">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* HEADER */}
        <header className="border-b border-gray-700 pb-4">
          <h1 className="text-4xl font-bold text-blue-400">Graph-RAG Multi-Modal Engine</h1>
          <p className="text-gray-400 mt-2">Dell AI Hackathon | Real-time vector analytics</p>
        </header>

<<<<<<< HEAD
        {/* SECTION 1: INGESTION */}
        <section className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h2 className="text-2xl font-semibold mb-4">1. Document Ingestion</h2>
          <div className="flex gap-4 items-center">
=======
      {/* Main Grid Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Upload & System Status */}
        <div className="lg:col-span-5 space-y-8">
          <div className={`p-6 border-l-4 rounded-r-lg shadow-2xl transition-all duration-500 hover:scale-[1.01] ${
            theme === 'dark' ? 'bg-zinc-900 border-cyan-500' : 'bg-white border-blue-600'
          }`}>
            <h2 className="text-3xl font-black mb-2 uppercase tracking-wide">Data Intake</h2>
            <p className={`text-sm mb-6 ${theme === 'dark' ? 'text-zinc-400' : 'text-slate-500'}`}>
              Initialize Graph-RAG by securely dropping enterprise .pdf or .docx files into the uplink bucket.
            </p>
            <UploadForm theme={theme} />
          </div>

          <div className={`p-6 border-l-4 rounded-r-lg shadow-2xl ${
            theme === 'dark' ? 'bg-zinc-900 border-purple-500' : 'bg-white border-purple-600'
          }`}>
            <h3 className="text-xl font-bold uppercase tracking-widest mb-4">System Telemetry</h3>
            <div className="space-y-4 font-mono text-sm">
              <div className="flex justify-between border-b border-dashed border-zinc-700 pb-2">
                <span>Vector Engine</span>
                <span className="text-emerald-500 animate-pulse">ONLINE</span>
              </div>
              <div className="flex justify-between border-b border-dashed border-zinc-700 pb-2">
                <span>Graph Traverser</span>
                <span className="text-emerald-500 animate-pulse">ONLINE</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Active Chat Interface */}
        <div className={`lg:col-span-7 p-6 border-l-4 rounded-r-lg shadow-2xl flex flex-col h-[600px] ${
          theme === 'dark' ? 'bg-zinc-900 border-emerald-500' : 'bg-white border-emerald-600'
        }`}>
          <h2 className="text-3xl font-black mb-2 uppercase tracking-wide">Document Terminal</h2>
          <p className={`text-sm mb-4 border-b pb-4 ${theme === 'dark' ? 'text-zinc-400 border-zinc-800' : 'text-slate-500 border-slate-200'}`}>
            Execute natural language queries against the ingested intelligence network.
          </p>

          {/* Chat Logs Window */}
          <div className={`flex-1 overflow-y-auto rounded p-4 space-y-4 border ${
            theme === 'dark' ? 'bg-zinc-950 border-zinc-800' : 'bg-slate-50 border-slate-200'
          }`}>
            {chatHistory.length === 0 ? (
              <div className="h-full flex items-center justify-center text-center">
                <p className={`font-mono text-sm animate-pulse ${theme === 'dark' ? 'text-zinc-600' : 'text-slate-400'}`}>
                  [ System idle. Upload a document and stream your first query. ]
                </p>
              </div>
            ) : (
              chatHistory.map((msg, index) => (
                <div key={index} className={`p-3 rounded font-mono text-sm border ${
                  msg.sender === 'user'
                    ? theme === 'dark' ? 'bg-zinc-900 border-cyan-900 text-cyan-400 self-end' : 'bg-blue-50 border-blue-200 text-blue-700'
                    : theme === 'dark' ? 'bg-zinc-950 border-zinc-800 text-zinc-100' : 'bg-white border-slate-200 text-slate-800'
                }`}>
                  <span className="font-black block text-xs uppercase mb-1 tracking-wider opacity-60">
                    {msg.sender === 'user' ? '// User_Query' : '// System_Response'}
                  </span>
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                  {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 border-t border-zinc-700 pt-3">
                    <div className="font-bold text-xs mb-2 text-emerald-400">
                      EVIDENCE SOURCES
                    </div>

                    {msg.sources.map((source, idx) => (
                      <div key={idx} className="text-xs opacity-80">
                        📄 Page {source.page} — {source.title}
                      </div>
                    ))}
                  </div>
                )}
                </div>
              ))
            )}
            {loading && (
              <div className="p-3 font-mono text-sm text-yellow-500 animate-pulse">
                [ Computing embeddings and traversing database nodes... ]
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Inputs */}
          <div className="mt-4 flex gap-4">
>>>>>>> dc859da567c64e28f84fe9440a8767500577c11e
            <input 
              type="file" 
              onChange={(e) => setFile(e.target.files[0])} 
              className="file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer"
            />
            <button 
              onClick={handleUploadAndAnalyze}
              disabled={loading}
              className="bg-green-600 hover:bg-green-500 px-6 py-2 rounded font-bold transition-all disabled:opacity-50"
            >
              {loading ? "Processing Pipeline..." : "Upload & Analyze"}
            </button>
          </div>
        </section>

        {analysisData && (
          <>
            {/* SECTION 2: EXECUTIVE SUMMARY */}
            <section className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <h2 className="text-2xl font-semibold mb-4 text-purple-400">Executive Summary</h2>
              <p className="leading-relaxed">{analysisData.summary}</p>
            </section>

            {/* SECTION 3: INTERACTIVE QUIZ & TRACEABILITY */}
            <section className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <h2 className="text-2xl font-semibold mb-4 text-orange-400">Knowledge Verification</h2>
              
              <div className="mb-4">
                <label className="block text-sm text-gray-400 mb-2">Select a Question generated from the Graph:</label>
                <select 
                  className="w-full bg-gray-900 border border-gray-600 rounded p-3 text-white"
                  onChange={(e) => {
                    setActiveQuestionIndex(e.target.value);
                    setShowTrace(false);
                    setSelectedAnswer("");
                  }}
                >
                  {analysisData.quiz.map((q, idx) => (
                    <option key={idx} value={idx}>{q.question}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-3 mt-6">
                {analysisData.quiz[activeQuestionIndex].options.map((opt, i) => (
                  <button 
                    key={i}
                    onClick={() => setSelectedAnswer(opt)}
                    className={`block w-full text-left p-3 rounded border transition-all ${selectedAnswer === opt ? 'bg-blue-600 border-blue-400' : 'bg-gray-900 border-gray-700 hover:border-gray-500'}`}
                  >
                    {opt}
                  </button>
                ))}
              </div>

              {selectedAnswer && (
                <div className="mt-6 pt-4 border-t border-gray-700 flex justify-between items-center">
                  <p className="font-bold text-lg">
                    {selectedAnswer === analysisData.quiz[activeQuestionIndex].answer 
                      ? "✅ Correct!" 
                      : "❌ Incorrect"}
                  </p>
                  <button 
                    onClick={() => setShowTrace(!showTrace)}
                    className="text-sm bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded"
                  >
                    {showTrace ? "Hide Explainability Trace" : "Why this answer?"}
                  </button>
                </div>
              )}

              {/* THE TRACE PIPELINE */}
              {showTrace && (
                <div className="mt-4 p-4 bg-black rounded border border-orange-900 font-mono text-sm text-orange-300">
                  <p className="font-bold mb-2">⚡ Pipeline Execution Trace:</p>
                  <ul className="list-disc pl-5 space-y-1">
                    {analysisData.quiz[activeQuestionIndex].trace.map((step, idx) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          </>
        )}

        {/* SECTION 4: ADAPTIVE ASK ENGINE */}
        <section className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h2 className="text-2xl font-semibold mb-4 text-emerald-400">Multi-Modal Ask Engine</h2>
          <div className="flex gap-4 mb-4">
            <input 
              type="text" 
              placeholder="Ask anything about the document..." 
              className="flex-1 bg-gray-900 border border-gray-600 rounded p-3 text-white"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <select 
              className="bg-gray-900 border border-gray-600 rounded p-3 text-white"
              value={format}
              onChange={(e) => setFormat(e.target.value)}
            >
              <option value="paragraph">Paragraph</option>
              <option value="bullets">Bullet Points</option>
              <option value="visual">Visual / Diagram</option>
            </select>
            <button 
              onClick={handleAskEngine}
              className="bg-emerald-600 hover:bg-emerald-500 px-6 py-2 rounded font-bold transition-all"
            >
              Ask
            </button>
          </div>
          
          {askResponse && (
            <div className="p-4 bg-gray-900 rounded border border-gray-600 whitespace-pre-wrap">
              {askResponse}
            </div>
          )}
        </section>

      </div>
    </div>
  );
}