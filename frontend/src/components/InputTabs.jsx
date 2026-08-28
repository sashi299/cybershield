import { useState, useRef } from 'react';
import { Link2, Mail, MessageSquare, QrCode, Loader2, Upload } from 'lucide-react';
import { analyzeUrl, analyzeText, analyzeQr } from '../api';

const TABS = [
  { id: 'url', label: 'URL', icon: Link2, placeholder: 'Enter a suspicious link (e.g., https://example.com)' },
  { id: 'email', label: 'Email', icon: Mail, placeholder: 'Paste email content here...' },
  { id: 'sms', label: 'SMS', icon: MessageSquare, placeholder: 'Paste text message here...' },
  { id: 'qr', label: 'QR Code', icon: QrCode, placeholder: 'Upload a QR code image' },
];

export default function InputTabs({ onAnalyze, onClear }) {
  const [activeTab, setActiveTab] = useState('url');
  const [inputValue, setInputValue] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    setInputValue('');
    setFile(null);
    setError('');
    if (onClear) onClear();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (activeTab !== 'qr' && !inputValue.trim()) {
      setError('Please enter some content to analyze.');
      return;
    }
    if (activeTab === 'qr' && !file) {
      setError('Please upload a QR code image.');
      return;
    }

    setLoading(true);
    try {
      let result;
      if (activeTab === 'url') {
        result = await analyzeUrl(inputValue);
      } else if (activeTab === 'email' || activeTab === 'sms') {
        result = await analyzeText(inputValue, activeTab);
      } else if (activeTab === 'qr') {
        result = await analyzeQr(file);
      }
      if (onAnalyze) onAnalyze(result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during analysis.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 rounded-xl shadow-lg border border-gray-800 overflow-hidden">
      <div className="flex border-b border-gray-800">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 py-4 px-2 text-sm font-medium transition-all
                ${isActive ? 'bg-gray-800 text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      <form onSubmit={handleSubmit} className="p-6">
        {activeTab !== 'qr' ? (
          activeTab === 'url' ? (
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={TABS.find(t => t.id === activeTab).placeholder}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg p-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
            />
          ) : (
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={TABS.find(t => t.id === activeTab).placeholder}
              rows={6}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg p-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all resize-none"
            />
          )
        ) : (
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="w-full bg-gray-950 border-2 border-dashed border-gray-700 rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer hover:border-cyan-500 hover:bg-gray-900/50 transition-all"
          >
            <Upload className="w-8 h-8 text-gray-500 mb-3" />
            <p className="text-gray-300 font-medium">Click to upload QR code</p>
            <p className="text-gray-500 text-sm mt-1">Supports PNG, JPG, JPEG</p>
            {file && (
              <div className="mt-4 p-2 bg-gray-800 rounded text-cyan-400 text-sm">
                Selected: {file.name}
              </div>
            )}
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => setFile(e.target.files[0])}
              accept="image/*"
              className="hidden"
            />
          </div>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-2 text-red-300 text-sm">
            <span className="font-bold shrink-0">⚠️ Error:</span>
            <div className="flex-1">{error}</div>
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            type="submit"
            disabled={loading || (activeTab !== 'qr' ? !inputValue.trim() : !file)}
            className="bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-2.5 px-6 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
            {loading ? 'Analyzing...' : `Analyze ${TABS.find(t => t.id === activeTab).label}`}
          </button>
        </div>
      </form>
    </div>
  );
}
