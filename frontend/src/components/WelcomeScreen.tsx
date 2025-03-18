// src/components/WelcomeScreen.tsx
import React, { useState } from "react";
import { Github, SendHorizontal, Loader2 } from "lucide-react";

interface WelcomeScreenProps {
  onSubmit: (url: string) => Promise<void>;
  isLoading: boolean;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSubmit, isLoading }) => {
  const [repoUrl, setRepoUrl] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (repoUrl.trim()) {
      await onSubmit(repoUrl);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-full text-center space-y-6 py-12">
      <Github className="h-16 w-16 text-purple-400" />
      <h2 className="text-2xl font-medium text-gray-100">Analyze any GitHub Repository</h2>
      <p className="text-gray-400 max-w-md">
        Enter a GitHub repository URL to get started. I'll analyze the repository and answer any questions you have
        about it.
      </p>
      <form onSubmit={handleSubmit} className="w-full max-w-md">
        <div className="relative flex items-center">
          <input
            type="text"
            placeholder="https://github.com/username/repository"
            className="w-full p-4 bg-gray-800 border border-gray-700 rounded-md text-gray-100 placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !repoUrl.trim()}
            className="absolute right-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:text-gray-500 text-white p-1 rounded-md transition-colors"
          >
            {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <SendHorizontal className="h-5 w-5" />}
          </button>
        </div>
      </form>

      <p className="text-sm text-gray-500">
        Examples: https://github.com/facebook/react, https://github.com/lodash/lodash
      </p>
    </div>
  );
};

export default WelcomeScreen;
