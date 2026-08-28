import { useState } from 'react';
import InputTabs from '../components/InputTabs';
import RiskMeter from '../components/RiskMeter';
import ResultCard from '../components/ResultCard';

export default function Scanner() {
  const [result, setResult] = useState(null);

  const handleAnalyze = (data) => {
    setResult(data);
  };

  const handleClear = () => {
    setResult(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-white tracking-tight">Scan for Threats</h1>
        <p className="text-gray-400">Analyze links, emails, SMS messages, and QR codes for potential phishing threats.</p>
      </div>

      <InputTabs onAnalyze={handleAnalyze} onClear={handleClear} />

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
  );
}
