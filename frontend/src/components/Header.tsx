// src/components/Header.tsx
import React from "react";
import { Github } from "lucide-react";

interface HeaderProps {
  isAnalyzing: boolean;
  onReset: () => void;
}

const Header: React.FC<HeaderProps> = ({ isAnalyzing, onReset }) => {
  return (
    <header className="bg-gray-800 border-b border-gray-700 p-4">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        <div className="flex items-center">
          <Github className="h-6 w-6 mr-2 text-purple-400" />
          <h1 className="text-lg font-medium text-gray-100">GitHub Repository Analyzer</h1>
        </div>
        {!isAnalyzing && (
          <button onClick={onReset} className="text-sm text-gray-400 hover:text-gray-200 transition-colors">
            New Analysis
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;
