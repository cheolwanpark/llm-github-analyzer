// src/components/MessageBubble.tsx
import React from "react";
import { Message } from "../types";

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  // Format message content with markdown-like styling
  const formatMessage = (content: string) => {
    return content.split("\n").map((line, i) => {
      if (line.startsWith("- ")) {
        return (
          <li key={i} className="ml-5 list-disc">
            {line.substring(2).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")}
          </li>
        );
      } else if (line === "") {
        return <br key={i} />;
      } else {
        return (
          <p
            key={i}
            dangerouslySetInnerHTML={{
              __html: line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"),
            }}
          />
        );
      }
    });
  };

  return (
    <div className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-2xl rounded-2xl px-5 py-4 ${
          message.role === "user" ? "bg-purple-600 text-white" : "bg-gray-800 border border-gray-700 text-gray-100"
        }`}
      >
        {formatMessage(message.content)}
      </div>
    </div>
  );
};

export default MessageBubble;
