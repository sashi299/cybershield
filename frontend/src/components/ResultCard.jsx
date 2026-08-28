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
