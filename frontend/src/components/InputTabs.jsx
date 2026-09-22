import { useState, useRef, useEffect } from 'react';
import { Link2, Mail, MessageSquare, QrCode, Loader2, Upload, Clipboard, Image as ImageIcon, X } from 'lucide-react';
import { analyzeUrl, analyzeText, analyzeQr } from '../api';

const TABS = [
  { id: 'url', label: 'URL / Link', icon: Link2, placeholder: 'Enter suspicious website link (e.g. http://paypal-security.xyz/login)...' },
  { id: 'sms', label: 'SMS & Messages', icon: MessageSquare, placeholder: 'Paste suspicious SMS, WhatsApp message, or digital arrest script...' },
  { id: 'email', label: 'Email Phishing', icon: Mail, placeholder: 'Paste email body with suspicious headers or urgency requests...' },
  { id: 'qr', label: 'QR & Screenshots', icon: QrCode, placeholder: 'Drop a QR code image or screenshot here...' },
];

export default function InputTabs({ onAnalyze, onClear, presetInput }) {
  const [activeTab, setActiveTab] = useState('url');
  const [inputValue, setInputValue] = useState('');
  const [file, setFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  // Handle demo mode preset input injection from parent
  useEffect(() => {
    if (presetInput) {
      if (presetInput.tab) setActiveTab(presetInput.tab);
      if (presetInput.value) setInputValue(presetInput.value);
      if (presetInput.file) {
        setFile(presetInput.file);
        setFilePreview(URL.createObjectURL(presetInput.file));
      }
    }
  }, [presetInput]);

  // Handle global paste event (Ctrl+V) for images and text
  useEffect(() => {
    const handlePaste = (e) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const blob = items[i].getAsFile();
          if (blob) {
            setActiveTab('qr');
            setFile(blob);
            setFilePreview(URL.createObjectURL(blob));
            setError('');
          }
          break;
        }
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, []);

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    setInputValue('');
    setFile(null);
    setFilePreview(null);
    setError('');
    if (onClear) onClear();
  };

  const handleFileChange = (selectedFile) => {
    if (selectedFile) {
      setFile(selectedFile);
      setFilePreview(URL.createObjectURL(selectedFile));
      setError('');
    }
  };

  const handleClearFile = (e) => {
    e.stopPropagation();
    setFile(null);
    setFilePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      if (dropped.type.startsWith('image/')) {
        setActiveTab('qr');
        handleFileChange(dropped);
      } else {
        setError('Please drop an image file (PNG, JPG, JPEG, WEBP).');
      }
    }
  };

  const handlePasteFromClipboard = async () => {
    try {
      if (window.desktopAPI?.readClipboardText) {
        const text = window.desktopAPI.readClipboardText();
        if (text) setInputValue(text);
      } else if (navigator.clipboard?.readText) {
        const text = await navigator.clipboard.readText();
        if (text) setInputValue(text);
      }
    } catch (e) {
      console.error('Clipboard read failed:', e);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (activeTab !== 'qr' && !inputValue.trim()) {
      setError('Please enter or paste some content to scan.');
      return;
    }
    if (activeTab === 'qr' && !file) {
      setError('Please upload, drop, or paste a QR code or screenshot.');
      return;
    }

    setLoading(true);
    try {
      let result;
      if (activeTab === 'url') {
        result = await analyzeUrl(inputValue.trim());
      } else if (activeTab === 'email' || activeTab === 'sms') {
        result = await analyzeText(inputValue.trim(), activeTab);
      } else if (activeTab === 'qr') {
        result = await analyzeQr(file);
      }
      if (onAnalyze) onAnalyze(result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during threat analysis.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 rounded-xl shadow-2xl border border-gray-800 overflow-hidden backdrop-blur-sm">
      {/* Tab Navigation */}
      <div className="flex border-b border-gray-800 bg-gray-950/60">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 py-4 px-3 text-sm font-medium transition-all
                ${isActive ? 'bg-gray-900 text-white border-b-2 border-[#CE0F3D] font-bold shadow-sm' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-900/50'}`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#CE0F3D]' : ''}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        {activeTab !== 'qr' ? (
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                {activeTab === 'url' ? 'Target Web Address' : 'Message Contents for NPU Analysis'}
              </label>
              <button
                type="button"
                onClick={handlePasteFromClipboard}
                className="flex items-center gap-1.5 text-xs text-rose-400 hover:text-rose-300 font-medium px-2.5 py-1 rounded bg-[#CE0F3D]/10 hover:bg-[#CE0F3D]/20 border border-[#CE0F3D]/20 transition-colors"
                title="Paste from system clipboard"
              >
                <Clipboard className="w-3.5 h-3.5" />
                Paste Clipboard
              </button>
            </div>

            {activeTab === 'url' ? (
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={TABS.find((t) => t.id === activeTab).placeholder}
                className="w-full bg-gray-950 border border-gray-700/80 rounded-lg p-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#CE0F3D] focus:border-transparent transition-all font-mono text-sm"
              />
            ) : (
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={TABS.find((t) => t.id === activeTab).placeholder}
                rows={6}
                className="w-full bg-gray-950 border border-gray-700/80 rounded-lg p-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#CE0F3D] focus:border-transparent transition-all resize-none text-sm leading-relaxed"
              />
            )}
          </div>
        ) : (
          /* Drag & Drop File Upload Stage */
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`w-full bg-gray-950 border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${
              isDragging
                ? 'border-[#CE0F3D] bg-red-950/20 scale-[1.01]'
                : 'border-gray-700 hover:border-[#CE0F3D]/60 hover:bg-gray-900/60'
            }`}
          >
            {filePreview ? (
              <div className="relative group max-w-xs">
                <img
                  src={filePreview}
                  alt="QR or screenshot preview"
                  className="max-h-48 rounded-lg shadow-md border border-gray-700 object-contain mx-auto"
                />
                <button
                  type="button"
                  onClick={handleClearFile}
                  className="absolute -top-2 -right-2 p-1.5 rounded-full bg-red-600 text-white hover:bg-red-500 transition-colors shadow-lg"
                  title="Remove image"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
                <p className="text-center text-xs text-gray-400 mt-2 truncate max-w-xs">
                  {file?.name || 'Pasted image from clipboard'}
                </p>
              </div>
            ) : (
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-full bg-[#CE0F3D]/10 text-rose-400 flex items-center justify-center mx-auto mb-3 border border-[#CE0F3D]/20">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-white font-semibold text-base">
                  Drag & Drop Screenshot or QR Image Here
                </p>
                <p className="text-gray-400 text-xs">
                  Or click to browse from PC • Supports PNG, JPG, WEBP
                </p>
                <div className="pt-2">
                  <span className="inline-flex items-center gap-1.5 text-xs text-rose-300 bg-gray-900 border border-gray-800 px-3 py-1 rounded-full">
                    <ImageIcon className="w-3 h-3 text-rose-400" /> Tip: Press <kbd className="bg-gray-800 px-1.5 py-0.5 rounded text-[10px] text-gray-300">Ctrl+V</kbd> to paste screenshot directly
                  </span>
                </div>
              </div>
            )}

            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => handleFileChange(e.target.files?.[0])}
              accept="image/*"
              className="hidden"
            />
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-2 text-red-300 text-sm">
            <span className="font-bold shrink-0">⚠️ Error:</span>
            <div className="flex-1">{error}</div>
          </div>
        )}

        {/* Action Button */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-xs text-gray-500">
            {activeTab === 'qr' ? 'Runs PyZbar Decoder + On-Device MobileNet-v2 Vision Classifier' : 'Runs DistilBERT (ONNX INT8) + 15-Rule Heuristic Engine'}
          </div>

          <button
            type="submit"
            disabled={loading || (activeTab !== 'qr' ? !inputValue.trim() : !file)}
            className="bg-gradient-to-r from-[#CE0F3D] to-[#990A2C] hover:from-[#E6002A] hover:to-[#B30C34] text-white font-medium py-3 px-8 rounded-lg flex items-center gap-2.5 transition-all shadow-lg shadow-red-950/40 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {loading ? 'Evaluating On-Device...' : `Scan with AI Guard`}
          </button>
        </div>
      </form>
    </div>
  );
}
