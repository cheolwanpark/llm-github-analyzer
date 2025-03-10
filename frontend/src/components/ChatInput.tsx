// src/components/ChatInput.tsx
import React, { useRef, useEffect } from "react";
import { SendHorizontal } from "lucide-react";

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
  inputRef: React.RefObject<HTMLTextAreaElement> | null;
}

const ChatInput: React.FC<ChatInputProps> = ({ input, setInput, onSubmit, isLoading, inputRef }) => {
  // Adjust textarea height based on content
  useEffect(() => {
    if (!inputRef) return;
    if (inputRef.current) {
      inputRef.current.style.height = "24px";
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [input, inputRef]);

  return (
    <div className="bg-gray-800 border-t border-gray-700 p-4">
      <div className="max-w-3xl mx-auto">
        <form onSubmit={onSubmit} className="relative">
          <textarea
            ref={inputRef}
            rows={1}
            placeholder="Ask about this repository..."
            className="w-full py-3 px-4 pr-12 bg-gray-900 border border-gray-700 rounded-md text-gray-100 placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none resize-none overflow-hidden"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSubmit(e);
              }
            }}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="absolute right-3 top-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:text-gray-500 text-white p-1 rounded-md transition-colors"
          >
            <SendHorizontal className="h-5 w-5" />
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2 text-center">Press Enter to send, Shift+Enter for a new line</p>
      </div>
    </div>
  );
};

export default ChatInput;
