import { useState, useEffect } from 'react';
import { getHistory } from '../api';
import { Link2, Mail, MessageSquare, QrCode, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';

const TYPE_ICONS = {
  url: Link2,
  email: Mail,
  sms: MessageSquare,
  qr: QrCode
};

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    getHistory()
      .then(data => {
        setHistory(data || []);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to fetch history.');
        setLoading(false);
      });
  }, []);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getVerdictColor = (verdict) => {
    switch (verdict?.toLowerCase()) {
      case 'safe': return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'suspicious': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      case 'dangerous': return 'bg-red-500/10 text-red-400 border-red-500/20';
      default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white tracking-tight">Scan History</h1>
        <div className="text-sm text-gray-400">{history.length} scans found</div>
      </div>

      {error && <div className="text-red-400 bg-red-500/10 p-4 rounded-lg border border-red-500/20">{error}</div>}

      {!loading && history.length === 0 && !error && (
        <div className="text-center py-12 bg-gray-900 rounded-xl border border-gray-800">
          <p className="text-gray-400">No scan history available.</p>
        </div>
      )}

      <div className="space-y-4">
        {history.map((item) => {
          const Icon = TYPE_ICONS[item.input_type?.toLowerCase()] || Link2;
          const isExpanded = expandedId === item.id;

          return (
            <div key={item.id} className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden shadow-sm transition-all hover:border-gray-700">
              <div 
                className="flex items-center justify-between p-4 cursor-pointer"
                onClick={() => toggleExpand(item.id)}
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="bg-gray-800 p-2 rounded-lg shrink-0">
                    <Icon className="w-5 h-5 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white truncate">
                      {item.input_value || 'QR Code Scan'}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(item.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4 shrink-0 ml-4">
                  <div className="text-right">
                    <div className={`text-xs font-semibold px-2.5 py-1 rounded-full border inline-block ${getVerdictColor(item.verdict)}`}>
                      {item.verdict || 'Unknown'}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {typeof item.confidence === 'number' ? item.confidence.toFixed(1) : parseFloat(item.confidence || 0).toFixed(1)}% Confidence
                    </div>
                  </div>
                  {isExpanded ? <ChevronUp className="w-5 h-5 text-gray-500" /> : <ChevronDown className="w-5 h-5 text-gray-500" />}
                </div>
              </div>

              {isExpanded && (
                <div className="p-4 border-t border-gray-800 bg-gray-900/50">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-sm font-medium text-gray-400 mb-2">Explanation</h4>
                      <p className="text-sm text-gray-300">{item.explanation || 'No explanation available.'}</p>
                    </div>
                    <div>
                      {item.red_flags && item.red_flags.length > 0 && (
                        <>
                          <h4 className="text-sm font-medium text-gray-400 mb-2">Red Flags</h4>
                          <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
                            {item.red_flags.split(', ').filter(Boolean).map((flag, idx) => (
                              <li key={idx}>{flag}</li>
                            ))}
                          </ul>
                        </>
                      )}
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
