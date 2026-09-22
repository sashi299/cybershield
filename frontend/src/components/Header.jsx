import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { getSystemStatus } from '../api';

// Distinctive Snapdragon Hexagon Silicon Chip Icon
function SnapdragonHexagonIcon({ className = "w-5 h-5", color = "#CE0F3D" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L20.66 7V17L12 22L3.34 17V7L12 2Z" stroke={color} strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M12 6.5L16.8 9.3V14.7L12 17.5L7.2 14.7V9.3L12 6.5Z" fill={color} fillOpacity="0.2" stroke={color} strokeWidth="1.2" />
      <circle cx="12" cy="12" r="2.4" fill={color} />
      <path d="M12 2V6.5M12 17.5V22M3.34 7L7.2 9.3M16.8 14.7L20.66 17M3.34 17L7.2 14.7M16.8 9.3L20.66 7" stroke={color} strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}

export default function Header() {
  const location = useLocation();
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    getSystemStatus()
      .then(data => setSystemStatus(data))
      .catch(() => setSystemStatus(null));
  }, []);

  return (
    <header className="bg-gray-950 border-b border-gray-800/90 sticky top-0 z-50 backdrop-blur-md bg-opacity-90">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group">
          {/* Snapdragon Silicon Hexagon Brand Icon */}
          <div className="p-2 rounded-xl bg-gradient-to-br from-[#CE0F3D]/20 to-red-950/40 border border-[#CE0F3D]/40 group-hover:border-[#CE0F3D] transition-all shadow-md shadow-red-950/30">
            <SnapdragonHexagonIcon className="w-6 h-6" color="#CE0F3D" />
          </div>
          
          <div className="flex items-center gap-2.5 shrink-0">
            <span className="text-xl font-extrabold text-white tracking-tight shrink-0">Cyber Shield</span>
            <span className="hidden sm:inline-flex items-center whitespace-nowrap shrink-0 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#CE0F3D]/20 text-rose-200 border border-[#CE0F3D]/40 leading-normal select-none">
              Snapdragon® X
            </span>
          </div>

          {/* Snapdragon NPU Status Badge */}
          {systemStatus && (
            <span className={`ml-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all ${
              systemStatus.npu_available
                ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'bg-[#CE0F3D]/10 text-rose-200 border border-[#CE0F3D]/30'
            }`}>
              <SnapdragonHexagonIcon className="w-3.5 h-3.5 shrink-0" color={systemStatus.npu_available ? "#10b981" : "#CE0F3D"} />
              <span className="font-mono">
                {systemStatus.npu_available ? 'NPU: Active (Hexagon HTP)' : 'NPU: Ready (CPU Fallback)'}
              </span>
            </span>
          )}
        </Link>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-2">
          <Link
            to="/"
            className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-all ${
              location.pathname === '/' 
                ? 'text-white bg-[#CE0F3D] shadow-sm shadow-red-900/30' 
                : 'text-gray-400 hover:text-white hover:bg-gray-900'
            }`}
          >
            Scanner
          </Link>
          <Link
            to="/performance"
            className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-all ${
              location.pathname === '/performance' 
                ? 'text-white bg-[#CE0F3D] shadow-sm shadow-red-900/30' 
                : 'text-gray-400 hover:text-white hover:bg-gray-900'
            }`}
          >
            Performance & NPU
          </Link>
          <Link
            to="/history"
            className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-all ${
              location.pathname === '/history' 
                ? 'text-white bg-[#CE0F3D] shadow-sm shadow-red-900/30' 
                : 'text-gray-400 hover:text-white hover:bg-gray-900'
            }`}
          >
            History
          </Link>
        </nav>
      </div>
    </header>
  );
}
