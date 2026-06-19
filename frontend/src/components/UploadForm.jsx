import { useState } from 'react';
import axios from 'axios';

export default function UploadForm() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus('Please select a file first.');
      return;
    }

    setIsUploading(true);
    setStatus('Uploading...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setStatus(`Success! ${response.data.filename} is ready for parsing.`);
    } catch (error) {
      setStatus('Upload failed. Is the backend running?');
      console.error(error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto mt-8 p-6 bg-slate-800 rounded-xl border border-slate-700 shadow-xl">
      <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-600 rounded-lg p-8 bg-slate-800/50 hover:border-blue-500 transition-colors">
        
        {/* Native SVG replacing the broken lucide-react icon */}
        <svg className="w-12 h-12 text-blue-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>

        <h3 className="text-lg font-medium text-slate-200 mb-2">Upload Document</h3>
        <p className="text-sm text-slate-400 text-center mb-6">
          Drop your PDF or DOCX here to build the intelligence graph.
        </p>
        
        <input 
          type="file" 
          onChange={handleFileChange} 
          accept=".pdf,.docx"
          className="text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-500 file:text-white hover:file:bg-blue-600 transition-colors cursor-pointer"
        />
      </div>

      <button 
        onClick={handleUpload}
        disabled={!file || isUploading}
        className="w-full mt-4 py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg font-medium transition-colors"
      >
        {isUploading ? 'Uploading...' : 'Process Document'}
      </button>

      {status && (
        <p className="mt-4 text-center text-sm font-medium text-emerald-400">
          {status}
        </p>
      )}
    </div>
  );
}