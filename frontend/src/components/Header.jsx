import { Link, useLocation } from 'react-router-dom';
import { Shield } from 'lucide-react';

export default function Header() {
  const location = useLocation();

  return (
    <header className="bg-gray-900 border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="bg-cyan-500/10 p-2 rounded-lg">
            <Shield className="w-6 h-6 text-cyan-400" />
          </div>
          <span className="text-xl font-bold text-white tracking-tight">Cyber Shield</span>
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
