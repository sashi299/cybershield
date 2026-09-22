import { useState } from 'react';
import { AlertTriangle, Info, Lightbulb, MessageSquareWarning, ChevronDown, ChevronUp } from 'lucide-react';
import { reportThreat } from '../api';

export default function ResultCard({ result }) {
  const [reportComment, setReportComment] = useState('');
  const [showReport, setShowReport] = useState(false);
  const [reportStatus, setReportStatus] = useState('');
  const [tipsExpanded, setTipsExpanded] = useState(false);

  const handleReport = async () => {
    try {
      await reportThreat(result.id, reportComment);
      setReportStatus('Reported successfully. Thank you!');
      setReportComment('');
      setTimeout(() => setShowReport(false), 3000);
    } catch (err) {
      setReportStatus('Failed to submit report.');
    }
  };

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-lg p-6 space-y-6">
      
      {/* Red Flags Section */}
      {result.redFlags && result.redFlags.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            Red Flags Detected
          </h3>
          <ul className="space-y-2">
            {result.redFlags.map((flag, idx) => (
              <li key={idx} className="flex items-start gap-2 bg-red-500/10 p-3 rounded-lg border border-red-500/20">
                <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <span className="text-red-200 text-sm">{typeof flag === 'string' ? flag : flag.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Model & Rule Explainability Inspector */}
      <div className="bg-gray-950/80 rounded-xl p-4 border border-gray-800 space-y-3">
        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
          <Info className="w-4 h-4 text-cyan-400" />
          Explainability & Defense Attribution Breakdown
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-gray-900 rounded-lg border border-gray-800">
            <div className="flex justify-between items-center mb-1">
              <span className="text-gray-300 font-semibold">1. Heuristic Rule Engine</span>
              <span className="text-cyan-400 font-mono">70% Weight</span>
            </div>
            <p className="text-gray-400 text-[11px]">
              {result.redFlags && result.redFlags.length > 0
                ? `${result.redFlags.length} structural indicator(s) triggered (typosquatting, IP links, urgency language).`
                : 'Zero heuristic red flags detected. Clean domain and message patterns.'}
            </p>
          </div>

          <div className="p-3 bg-gray-900 rounded-lg border border-gray-800">
            <div className="flex justify-between items-center mb-1">
              <span className="text-gray-300 font-semibold">2. On-Device DistilBERT NLP</span>
              <span className="text-purple-400 font-mono">30% Weight</span>
            </div>
            <p className="text-gray-400 text-[11px]">
              Analyzed semantic threat intent via Qualcomm AI Hub transformer model running on-device.
            </p>
          </div>
        </div>
      </div>

      {/* Visual Scam Detection (MobileNet-v2 On-Device) */}
      {result.visual_analysis && (
        <div className="bg-gray-800/80 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-white flex items-center gap-2">
              <span className="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
              On-Device Vision Scan (MobileNet-v2)
            </h4>
            <span className="text-xs text-gray-400 font-mono">
              {result.visual_analysis.inference_ms}ms
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-300">Visual Pattern:</span>
            <span className={`font-medium capitalize ${
              result.visual_analysis.detected_class === 'safe_content' ? 'text-green-400' : 'text-yellow-400'
            }`}>
              {result.visual_analysis.detected_class.replace(/_/g, ' ')}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm mt-1">
            <span className="text-gray-400 text-xs">Model Confidence:</span>
            <span className="text-gray-300 text-xs font-mono">
              {(result.visual_analysis.confidence * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      )}

      {/* Analysis Explanation */}
      {result.explanation && (
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-3">
            <Info className="w-5 h-5 text-cyan-400" />
            Analysis Explanation
          </h3>
          <div className="bg-gray-800 p-4 rounded-lg">
            <p className="text-gray-300 text-sm leading-relaxed">{result.explanation}</p>
          </div>
        </div>
      )}

      {/* Recommendation */}
      {result.recommendation && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-3">Recommendation</h3>
          <div className="bg-cyan-500/10 border border-cyan-500/20 p-4 rounded-lg">
            <p className="text-cyan-100 text-sm font-medium">{result.recommendation}</p>
          </div>
        </div>
      )}

      {/* Security Tips */}
      {result.tips && result.tips.length > 0 && (
        <div>
          <button 
            onClick={() => setTipsExpanded(!tipsExpanded)}
            className="w-full flex items-center justify-between text-lg font-semibold text-white mb-2"
          >
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-400" />
              Security Tips
            </div>
            {tipsExpanded ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
          </button>
          
          {tipsExpanded && (
            <ul className="space-y-2 mt-3">
              {result.tips.map((tip, idx) => (
                <li key={idx} className="flex items-start gap-2 bg-gray-800 p-3 rounded-lg">
                  <Lightbulb className="w-4 h-4 text-yellow-400 mt-0.5 shrink-0" />
                  <span className="text-gray-300 text-sm">{tip}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Report Action */}
      {result.id && (
        <div className="pt-4 border-t border-gray-800">
          {!showReport ? (
            <button 
              onClick={() => setShowReport(true)}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm"
            >
              <MessageSquareWarning className="w-4 h-4" />
              Report incorrect analysis
            </button>
          ) : (
            <div className="space-y-3">
              <label className="text-sm font-medium text-gray-300">Why is this analysis incorrect?</label>
              <textarea
                value={reportComment}
                onChange={(e) => setReportComment(e.target.value)}
                className="w-full bg-gray-950 border border-gray-700 rounded-lg p-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                rows={3}
                placeholder="Add your comments here..."
              />
              <div className="flex gap-2">
                <button
                  onClick={handleReport}
                  className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm transition-colors"
                >
                  Submit Report
                </button>
                <button
                  onClick={() => setShowReport(false)}
                  className="text-gray-400 hover:text-white px-4 py-2 rounded text-sm transition-colors"
                >
                  Cancel
                </button>
              </div>
              {reportStatus && <p className="text-cyan-400 text-sm mt-2">{reportStatus}</p>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
