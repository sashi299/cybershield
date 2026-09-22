import { Link, useLocation } from 'react-router-dom';
import { Shield, Cpu, Zap } from 'lucide-react';
import { getSystemStatus } from '../api';

export default function Header() {
  const location = useLocation();
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    // Fetch NPU/system status for the badge indicator
    getSystemStatus()
      .then(data => setSystemStatus(data))
      .catch(() => setSystemStatus(null));
  }, []);

  return (
    <header className="bg-gray-900 border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="bg-cyan-500/10 p-2 rounded-lg">
            <Shield className="w-6 h-6 text-cyan-400" />
          </div>
          <span className="text-xl font-bold text-white tracking-tight">Cyber Shield</span>
          {/* NPU / CPU Status Badge */}
          {systemStatus && (
            <span className={`ml-2 inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${
              systemStatus.npu_available
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
            }`}>
              {systemStatus.npu_available ? (
                <><Zap className="w-3 h-3 text-green-400" /> NPU: Active</>
              ) : (
                <><Cpu className="w-3 h-3 text-blue-400" /> NPU: Not available (CPU fallback)</>
              )}
            </span>
          )}
        </Link>
        <nav className="flex gap-6">
          <Link
            to="/"
            className={`text-sm font-medium transition-colors ${
              location.pathname === '/' ? 'text-cyan-400' : 'text-gray-400 hover:text-white'
            }`}
          >
            Scanner
          </Link>
          <Link
            to="/performance"
            className={`text-sm font-medium transition-colors ${
              location.pathname === '/performance' ? 'text-cyan-400' : 'text-gray-400 hover:text-white'
            }`}
          >
            Performance & NPU
          </Link>
          <Link
            to="/history"
            className={`text-sm font-medium transition-colors ${
              location.pathname === '/history' ? 'text-cyan-400' : 'text-gray-400 hover:text-white'
            }`}
          >
            History
          </Link>
        </nav>
      </div>
    </header>
  );
}
