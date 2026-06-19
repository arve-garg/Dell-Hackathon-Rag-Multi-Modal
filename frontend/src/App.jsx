import { useState } from 'react';

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
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
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // 1. Upload the File
      await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      // 2. Fetch the Analysis (Summary + Quiz)
      const res = await fetch("http://localhost:8000/analyze");
      const data = await res.json();
      setAnalysisData(data);
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

        {/* SECTION 1: INGESTION */}
        <section className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h2 className="text-2xl font-semibold mb-4">1. Document Ingestion</h2>
          <div className="flex gap-4 items-center">
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