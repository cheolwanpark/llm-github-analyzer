// src/components/MessageList.tsx
import React, { useRef, useEffect } from "react";
import { Message } from "../types";
import MessageBubble from "./MessageBubble";
import LoadingIndicator from "./LoadingIndicator";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  loadingMessage: string;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading, loadingMessage }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="space-y-6 py-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {isLoading && <LoadingIndicator message={loadingMessage} />}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
