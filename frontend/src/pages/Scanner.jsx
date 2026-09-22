import { useState, useEffect } from 'react';
import InputTabs from '../components/InputTabs';
import RiskMeter from '../components/RiskMeter';
import ResultCard from '../components/ResultCard';
import { getHistory } from '../api';
import { Play, Sparkles, Clock, AlertTriangle, ShieldCheck, HelpCircle, ChevronRight, Zap, RefreshCw } from 'lucide-react';

const DEMO_PRESETS = [
  {
    id: 'digital_arrest',
    title: '🚨 Digital Arrest Scam',
    type: 'High Threat',
    tagColor: 'text-red-400 bg-red-500/10 border-red-500/20',
    tab: 'sms',
    value: 'URGENT NOTICE: CBI Officer Cyber Crime Branch. An arrest warrant has been issued against your Aadhaar for illegal money laundering. Do not disconnect this call or you will be placed under digital arrest immediately. Transfer funds to safe verification account.',
  },
  {
    id: 'sbi_phishing',
    title: '🚨 Bank Phishing Link',
    type: 'High Threat',
    tagColor: 'text-red-400 bg-red-500/10 border-red-500/20',
    tab: 'url',
    value: 'http://sbi-netbanking-kyc-update.xyz/login',
  },
  {
    id: 'password_expiry',
    title: '⚠️ Password Expiry Scam',
    type: 'Suspicious',
    tagColor: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
    tab: 'email',
    value: 'ACTION REQUIRED: Your corporate email credentials expire in 2 hours. Verify your account immediately to prevent service interruption: http://company-login-auth.com/portal',
  },
  {
    id: 'clean_otp',
    title: '✅ Legitimate Bank OTP',
    type: 'Verified Safe',
    tagColor: 'text-green-400 bg-green-500/10 border-green-500/20',
    tab: 'sms',
    value: 'Your OTP for SBI Net Banking transaction is 482910. Valid for 10 minutes. Do not share this OTP with anyone, including bank officials.',
  },
];

export default function Scanner() {
  const [result, setResult] = useState(null);
  const [presetInput, setPresetInput] = useState(null);
  const [historyItems, setHistoryItems] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const fetchRecentHistory = async () => {
    try {
      setLoadingHistory(true);
      const res = await getHistory();
      setHistoryItems(res.slice(0, 10)); // Take last 10 scans
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchRecentHistory();
  }, []);

  const handleAnalyze = (data) => {
    setResult(data);
    fetchRecentHistory(); // Refresh sidebar history
  };

  const handleClear = () => {
    setResult(null);
    setPresetInput(null);
  };

  const handleSelectPreset = (preset) => {
    setPresetInput({
      tab: preset.tab,
      value: preset.value,
      file: null,
    });
    setResult(null);
  };

  const handleSelectHistoryItem = (item) => {
    setResult({
      id: item.id,
      verdict: item.verdict,
      confidence: item.confidence,
      redFlags: item.redFlags || [],
      explanation: item.explanation,
      recommendation: item.recommendation,
      tips: item.tips || [],
      target: item.target,
      visual_analysis: item.visual_analysis,
    });
  };

  return (
    <div className="space-y-6">
      {/* Top Demo Mode Banner */}
      <div className="bg-gradient-to-r from-gray-900 via-gray-900 to-gray-950 border border-gray-800 rounded-xl p-4 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-[#CE0F3D]/10 text-rose-400 border border-[#CE0F3D]/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <span className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                Challenge Judge Demo Mode
                <span className="text-[10px] font-mono bg-[#CE0F3D]/20 text-rose-300 px-2 py-0.5 rounded-full border border-[#CE0F3D]/30">
                  1-Click Presets
                </span>
              </span>
              <p className="text-xs text-gray-400">
                Click any preset to test on-device transformer NLP & vision detection instantly:
              </p>
            </div>
          </div>

          {/* Preset Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            {DEMO_PRESETS.map((preset) => (
              <button
                key={preset.id}
                onClick={() => handleSelectPreset(preset)}
                className={`text-xs font-medium px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 hover:scale-[1.02] ${preset.tagColor}`}
              >
                <span>{preset.title}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Multi-Pane Desktop Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Pane: Scan History Sidebar */}
        <div className={`lg:col-span-3 bg-gray-900 border border-gray-800 rounded-xl p-4 shadow-xl space-y-4`}>
          <div className="flex items-center justify-between border-b border-gray-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-rose-400" />
              Recent Scan Log
            </h3>
            <button
              onClick={fetchRecentHistory}
              title="Refresh log"
              className="text-gray-400 hover:text-white p-1 rounded transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingHistory ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div className="space-y-2 max-h-[620px] overflow-y-auto pr-1">
            {historyItems.length === 0 ? (
              <div className="text-center py-8 text-gray-500 text-xs">
                No past scans recorded yet.
              </div>
            ) : (
              historyItems.map((item) => {
                const isDangerous = item.verdict?.toLowerCase() === 'dangerous';
                const isSuspicious = item.verdict?.toLowerCase() === 'suspicious';
                const color = isDangerous
                  ? 'text-red-400 bg-red-500/10 border-red-500/20'
                  : isSuspicious
                  ? 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20'
                  : 'text-green-400 bg-green-500/10 border-green-500/20';

                return (
                  <div
                    key={item.id}
                    onClick={() => handleSelectHistoryItem(item)}
                    className="p-3 bg-gray-950/70 hover:bg-gray-800/80 rounded-lg border border-gray-800/80 cursor-pointer transition-all space-y-1.5 group"
                  >
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${color}`}>
                        {item.verdict}
                      </span>
                      <span className="text-[10px] text-gray-500 font-mono">
                        {item.confidence?.toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-xs text-gray-300 font-mono truncate group-hover:text-rose-400 transition-colors">
                      {item.target || item.input_value || 'Message content'}
                    </p>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Center / Right Pane: Main Scan Console & Results */}
        <div className="lg:col-span-9 space-y-6">
          <InputTabs onAnalyze={handleAnalyze} onClear={handleClear} presetInput={presetInput} />

          {/* Results Display */}
          {result && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="md:col-span-1">
                <RiskMeter verdict={result.verdict} confidence={result.confidence} />
              </div>
              <div className="md:col-span-2">
                <ResultCard result={result} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
