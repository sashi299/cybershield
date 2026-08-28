import React from 'react';
import { ShieldCheck, Zap, Lock } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-gray-800/80 bg-gray-950/80 backdrop-blur text-gray-400 py-6 mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-2 text-gray-300">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <span className="font-semibold text-white">Cyber Shield</span> — Intelligent Phishing & Fraud Detection Engine
        </div>
        <div className="flex items-center gap-4 text-gray-400">
          <span className="flex items-center gap-1">
            <Zap className="w-3.5 h-3.5 text-yellow-400" /> Real-time ML & Heuristics
          </span>
          <span className="flex items-center gap-1">
            <Lock className="w-3.5 h-3.5 text-green-400" /> HackSprint 2.0
          </span>
        </div>
      </div>
    </footer>
  );
}
