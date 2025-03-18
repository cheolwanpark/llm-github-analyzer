import React from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Message } from "../types";

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  return (
    <div className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-2xl rounded-2xl px-5 py-4 prose prose-invert ${
          message.role === "user" ? "bg-purple-600 text-white" : "bg-gray-800 border border-gray-700 text-gray-100"
        }`}
      >
        <Markdown remarkPlugins={[remarkGfm]}>{message.content}</Markdown>
      </div>
    </div>
  );
};

export default MessageBubble;
