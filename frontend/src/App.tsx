// src/App.tsx
import React, { useEffect, useRef, useState } from "react";
import { Message, RepoContext } from "./types";
import Header from "./components/Header";
import WelcomeScreen from "./components/WelcomeScreen";
import MessageList from "./components/MessageList";
import ChatInput from "./components/ChatInput";
import {
  fetchQueryAnswer,
  fetchRepoData,
  generateResponse,
  initializeAnalyzer,
  submitQuery,
  waitForAnalyzerReady,
  waitForQueryDone,
} from "./services/githubService";

import { WELCOME_PROMPT } from "./prompts";

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [introStep, setIntroStep] = useState<boolean>(true);

  const [repoAnalyzerID, setRepoAnalyzerID] = useState<string>("");

  // Handle initial repo URL submission
  const handleRepoSubmit = async (url: string) => {
    // setIntroStep(false);

    // const content = `A paragraph with *emphasis* and **strong importance**.

    // > A block quote with ~strikethrough~ and a URL: https://reactjs.org.

    // * Lists
    // * [ ] todo
    // * [x] done

    // A table:

    // | a | b |
    // | - | - |
    // `;

    // const welcomeMessage: Message = {
    //   id: Date.now().toString(),
    //   role: "assistant",
    //   content: content,
    // };
    // setMessages([welcomeMessage]);
    // return;

    if (!url.trim() || !url.includes("github.com/")) {
      return;
    }

    setIsLoading(true);

    try {
      const analyzerID = await initializeAnalyzer(url);
      setRepoAnalyzerID(analyzerID);
      console.log("analyzer id", analyzerID);

      const isReady = await waitForAnalyzerReady(analyzerID);
      if (!isReady) {
        console.error("Analyzer never reached READY state.");
        return;
      }
      setIntroStep(false);

      const answer = await fetchQueryAnswer(analyzerID, WELCOME_PROMPT);
      console.log("answer:", answer);

      const welcomeMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: answer,
      };

      setMessages([welcomeMessage]);
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
    if (!input.trim() || !repoAnalyzerID) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const answer = await fetchQueryAnswer(repoAnalyzerID, input);
      console.log("answer:", answer);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: answer,
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
    setRepoAnalyzerID("");
    setIntroStep(true);
    setMessages([]);
    setInput("");
  };

  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Handle focusing on the ChatInput when typing anywhere
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== "Tab" && inputRef.current) {
        inputRef.current.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

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

      {!introStep && (
        <ChatInput
          input={input}
          setInput={setInput}
          onSubmit={handleChatSubmit}
          isLoading={isLoading}
          inputRef={inputRef}
        />
      )}
    </div>
  );
};

export default App;
