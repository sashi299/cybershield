export default function RiskMeter({ verdict, confidence }) {
  let color = 'text-green-500';
  let strokeColor = '#22c55e'; // green
  
  if (verdict?.toLowerCase() === 'suspicious') {
    color = 'text-yellow-500';
    strokeColor = '#eab308'; // yellow
  } else if (verdict?.toLowerCase() === 'dangerous') {
    color = 'text-red-500';
    strokeColor = '#ef4444'; // red
  }

  // Semi-circle math
  const radius = 60;
  const circumference = radius * Math.PI;
  const numConfidence = typeof confidence === 'number' ? confidence : parseFloat(confidence || 0);
  const offset = circumference - (numConfidence / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-gray-900 rounded-xl border border-gray-800 shadow-lg">
      <div className="relative w-48 h-24 overflow-hidden flex justify-center">
        <svg className="w-48 h-48 transform -rotate-180 origin-center" viewBox="0 0 140 140">
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke="#1f2937"
            strokeWidth="12"
            strokeDasharray={`${circumference} ${circumference}`}
          />
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth="12"
            strokeDasharray={`${circumference} ${circumference}`}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute bottom-0 flex flex-col items-center">
          <span className={`text-xl font-bold uppercase tracking-wider ${color}`}>
            {verdict || 'Unknown'}
          </span>
        </div>
      </div>
      <div className="mt-4 text-center">
        <span className="text-gray-400 text-sm">Confidence Score</span>
        <div className="text-3xl font-bold text-white">{numConfidence.toFixed(1)}%</div>
      </div>
    </div>
  );
}
