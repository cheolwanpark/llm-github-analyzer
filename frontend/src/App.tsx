// src/App.tsx
import React, { useState } from "react";
import { Message, RepoContext } from "./types";
import Header from "./components/Header";
import WelcomeScreen from "./components/WelcomeScreen";
import MessageList from "./components/MessageList";
import ChatInput from "./components/ChatInput";
import { fetchRepoData, generateResponse } from "./services/githubService";

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [repo, setRepo] = useState<RepoContext | null>(null);
  const [introStep, setIntroStep] = useState<boolean>(true);

  // Handle initial repo URL submission
  const handleRepoSubmit = async (url: string) => {
    if (!url.trim() || !url.includes("github.com/")) {
      setMessages([
        {
          id: Date.now().toString(),
          role: "assistant",
          content: "Please enter a valid GitHub repository URL (e.g., https://github.com/facebook/react)",
        },
      ]);
      return;
    }

    setIsLoading(true);

    try {
      const repoData = await fetchRepoData(url);
      setRepo(repoData);

      const welcomeMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `I've analyzed the GitHub repository **${
          repoData.name
        }**.\n\nThis repository has ${repoData.stars.toLocaleString()} stars, ${repoData.forks.toLocaleString()} forks, and ${
          repoData.issues
        } open issues. It was last updated ${
          repoData.lastUpdated
        }.\n\nWhat would you like to know about this repository?`,
      };

      setMessages([welcomeMessage]);
      setIntroStep(false);
    } catch (error) {
      setMessages([
        {
          id: Date.now().toString(),
          role: "assistant",
          content: "I encountered an error analyzing that repository. Please check the URL and try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle chat messages after repo is set
  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || !repo) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const responseContent = await generateResponse(input, repo);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: responseContent,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I encountered an error processing your question. Please try asking in a different way.",
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Reset the conversation and start with a new repo
  const handleReset = () => {
    setRepo(null);
    setIntroStep(true);
    setMessages([]);
    setInput("");
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-100 font-sans">
      <Header isAnalyzing={introStep} onReset={handleReset} />

      <main className="flex-1 overflow-auto p-4 md:p-6">
        <div className="max-w-3xl mx-auto">
          {introStep ? (
            <WelcomeScreen onSubmit={handleRepoSubmit} isLoading={isLoading} />
          ) : (
            <MessageList messages={messages} isLoading={isLoading} loadingMessage="Thinking..." />
          )}
        </div>
      </main>

      {!introStep && <ChatInput input={input} setInput={setInput} onSubmit={handleChatSubmit} isLoading={isLoading} />}
    </div>
  );
};

export default App;
