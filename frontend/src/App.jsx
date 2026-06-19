import { useState } from 'react';
import UploadForm from './components/UploadForm';

export default function App() {
  const [theme, setTheme] = useState('dark');
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const handleTransmit = async () => {
    if (!query.strip && query.trim() === '') return;
    
    const userMessage = query;
    setChatHistory((prev) => [...prev, { sender: 'user', text: userMessage }]);
    setQuery('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage }),
      });
      
      const data = await response.json();
      
      setChatHistory((prev) => [
        ...prev, 
        { sender: 'system', text: data.answer || 'Error interpreting return stream.' }
      ]);
    } catch (error) {
      setChatHistory((prev) => [
        ...prev, 
        { sender: 'system', text: 'Connection terminal fault. Ensure backend is online.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen transition-colors duration-500 font-sans flex flex-col ${
      theme === 'dark' ? 'bg-zinc-950 text-cyan-50' : 'bg-slate-50 text-slate-900'
    }`}>
      
      {/* Navigation / Header */}
      <header className={`px-8 py-4 flex justify-between items-center border-b backdrop-blur-md sticky top-0 z-50 ${
        theme === 'dark' ? 'border-cyan-900/50 bg-zinc-950/80' : 'border-slate-300 bg-white/80'
      }`}>
        <div className="flex items-center gap-3">
          <svg className={`w-8 h-8 animate-pulse ${theme === 'dark' ? 'text-cyan-400' : 'text-blue-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
          </svg>
          <h1 className="text-2xl font-black tracking-widest uppercase">
            DIG // <span className={theme === 'dark' ? 'text-cyan-400' : 'text-blue-600'}>Core</span>
          </h1>
        </div>
        
        <button 
          onClick={toggleTheme}
          className={`px-4 py-2 rounded-none border-2 font-bold uppercase text-xs tracking-widest transition-all duration-300 hover:-translate-y-1 ${
            theme === 'dark' 
              ? 'border-cyan-500 text-cyan-400 hover:bg-cyan-500 hover:text-zinc-950 hover:shadow-[0_0_15px_rgba(34,211,238,0.5)]' 
              : 'border-slate-900 text-slate-900 hover:bg-slate-900 hover:text-white'
          }`}
        >
          {theme === 'dark' ? 'Engage Light' : 'Engage Dark'}
        </button>
      </header>

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
                </div>
              ))
            )}
            {loading && (
              <div className="p-3 font-mono text-sm text-yellow-500 animate-pulse">
                [ Computing embeddings and traversing database nodes... ]
              </div>
            )}
          </div>

          {/* Chat Inputs */}
          <div className="mt-4 flex gap-4">
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleTransmit()}
              placeholder="Query the document network..." 
              className={`flex-1 p-4 font-mono text-sm focus:outline-none focus:ring-1 rounded-none border ${
                theme === 'dark' 
                  ? 'bg-zinc-950 border-zinc-800 text-cyan-400 focus:ring-cyan-500 placeholder-zinc-700' 
                  : 'bg-white border-slate-300 text-slate-900 focus:ring-blue-500 placeholder-slate-400'
              }`}
            />
            <button 
              onClick={handleTransmit}
              disabled={loading}
              className={`px-8 font-bold uppercase tracking-widest transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50 ${
                theme === 'dark' 
                  ? 'bg-cyan-500 text-zinc-950 hover:bg-cyan-400 hover:shadow-[0_0_20px_rgba(34,211,238,0.6)]' 
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              Transmit
            </button>
          </div>
        </div>

      </main>
    </div>
  );
}