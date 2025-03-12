// src/components/LoadingIndicator.tsx
import React from "react";
import { Loader2 } from "lucide-react";

interface LoadingIndicatorProps {
  message: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ message }) => {
  return (
    <div className="flex justify-start">
      <div className="bg-gray-800 border border-gray-700 rounded-2xl px-5 py-4 text-gray-300 max-w-2xl">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-5 w-5 animate-spin text-purple-400" />
          <span>{message}</span>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;
