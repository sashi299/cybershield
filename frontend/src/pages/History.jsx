import { useState, useEffect } from 'react';
import { getHistory } from '../api';
import { Link2, Mail, MessageSquare, QrCode, ChevronDown, ChevronUp, Loader2, RefreshCw, AlertTriangle } from 'lucide-react';

const TYPE_ICONS = {
  url: Link2,
  email: Mail,
  sms: MessageSquare,
  text: MessageSquare,
  qr: QrCode
};

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  const loadHistory = async (isManual = false) => {
    try {
      if (isManual) setRefreshing(true);
      else setLoading(true);
      setError('');
      const data = await getHistory();
      setHistory(data || []);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch history from local database.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getVerdictColor = (verdict) => {
    switch (verdict?.toLowerCase()) {
      case 'safe': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'suspicious': return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'dangerous': return 'bg-red-500/10 text-rose-400 border-red-500/20';
      default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 animate-spin text-[#CE0F3D]" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <span>Scan History</span>
            <span className="text-xs font-mono font-normal px-2.5 py-0.5 rounded-full bg-[#CE0F3D]/10 text-rose-400 border border-[#CE0F3D]/20">
              {history.length} scans recorded
            </span>
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Persisted on-device threat audits across URL, SMS, email, and QR vision scans
          </p>
        </div>

        <button
          onClick={() => loadHistory(true)}
          disabled={refreshing}
          className="flex items-center gap-2 text-xs font-medium px-3.5 py-2 rounded-lg bg-gray-900 border border-gray-800 hover:border-[#CE0F3D]/40 text-gray-300 hover:text-white transition-all shadow-sm"
          title="Refresh scan history"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-rose-400 ${refreshing ? 'animate-spin' : ''}`} />
          <span>{refreshing ? 'Refreshing...' : 'Refresh Log'}</span>
        </button>
      </div>

      {error && (
        <div className="text-red-400 bg-red-500/10 p-4 rounded-lg border border-red-500/20 text-sm">
          {error}
        </div>
      )}

      {!loading && history.length === 0 && !error && (
        <div className="text-center py-16 bg-gray-900 rounded-xl border border-gray-800 space-y-2">
          <p className="text-gray-300 font-medium">No past scans recorded yet.</p>
          <p className="text-xs text-gray-500">Run a scan in the Scanner tab or select a Demo Preset to record entries.</p>
        </div>
      )}

      <div className="space-y-3">
        {history.map((item) => {
          const Icon = TYPE_ICONS[item.input_type?.toLowerCase()] || Link2;
          const isExpanded = expandedId === item.id;
          const displayContent = item.target || item.input_value || (item.input_type === 'qr' ? 'QR Code Image Scan' : 'Scanned Content');

          const redFlagsList = Array.isArray(item.redFlags) && item.redFlags.length > 0
            ? item.redFlags
            : (typeof item.red_flags === 'string' && item.red_flags.trim().length > 0
                ? item.red_flags.split(', ').filter(Boolean).map(f => ({ description: f }))
                : []);

          return (
            <div 
              key={item.id} 
              className={`bg-gray-900 rounded-xl border transition-all ${
                isExpanded ? 'border-gray-700 shadow-md' : 'border-gray-800 hover:border-gray-700'
              }`}
            >
              <div 
                className="flex items-center justify-between p-4 cursor-pointer select-none"
                onClick={() => toggleExpand(item.id)}
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="bg-gray-800/80 p-2.5 rounded-lg shrink-0 border border-gray-700/60">
                    <Icon className="w-5 h-5 text-gray-300" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-white truncate font-mono">
                      {displayContent}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                      <span className="capitalize text-gray-400 font-medium">{item.input_type || 'Scan'}</span>
                      <span>•</span>
                      <span>{new Date(item.timestamp).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4 shrink-0 ml-4">
                  <div className="text-right">
                    <div className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border inline-block ${getVerdictColor(item.verdict)}`}>
                      {item.verdict || 'Unknown'}
                    </div>
                    <div className="text-xs text-gray-500 mt-1 font-mono">
                      {typeof item.confidence === 'number' ? item.confidence.toFixed(1) : parseFloat(item.confidence || 0).toFixed(1)}% Confidence
                    </div>
                  </div>
                  {isExpanded ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-500" />}
                </div>
              </div>

              {isExpanded && (
                <div className="p-4 border-t border-gray-800/80 bg-gray-950/50 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Analysis Explanation</h4>
                      <p className="text-sm text-gray-300 leading-relaxed bg-gray-900/80 p-3 rounded-lg border border-gray-800">
                        {item.explanation || 'No explanation available.'}
                      </p>
                    </div>

                    <div className="space-y-1.5">
                      <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                        {item.verdict === 'Safe' ? 'Security Recommendation' : 'Threat Flags & Recommendation'}
                      </h4>
                      <div className="bg-gray-900/80 p-3 rounded-lg border border-gray-800 space-y-2">
                        {item.recommendation && (
                          <p className="text-xs font-medium text-rose-200">
                            {item.recommendation}
                          </p>
                        )}
                        {redFlagsList.length > 0 ? (
                          <ul className="space-y-1 pt-1 border-t border-gray-800">
                            {redFlagsList.map((flag, idx) => (
                              <li key={idx} className="flex items-start gap-1.5 text-xs text-red-300">
                                <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                                <span>{typeof flag === 'string' ? flag : (flag.description || flag.rule_id)}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-xs text-emerald-400">Zero threat flags detected.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
