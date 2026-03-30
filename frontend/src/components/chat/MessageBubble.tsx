"use client";

import { ChatMessage } from "@/types/travel";
import { Bot, User } from "lucide-react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  message: ChatMessage;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {/* Avatar - assistant only */}
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-600/80 text-white flex items-center justify-center mt-0.5">
          <Bot size={16} />
        </div>
      )}

      {/* Content */}
      <div className={isUser ? "max-w-[80%]" : "max-w-full min-w-0 flex-1"}>
        {isUser ? (
          <div className="bg-sky-500 text-white rounded-2xl rounded-tr-md px-4 py-2.5 text-sm leading-relaxed">
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
        ) : (
          <div className="bg-white/[0.04] border border-white/[0.06] rounded-2xl rounded-tl-md px-5 py-4">
            <div className="prose-chat text-[14px]">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        )}
        <p className={`mt-1 text-[10px] text-white/25 ${isUser ? "text-right mr-1" : "ml-1"}`}>
          {message.timestamp.toLocaleTimeString("pt-BR", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>

      {/* Avatar - user only */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-sky-500/80 text-white flex items-center justify-center mt-0.5">
          <User size={16} />
        </div>
      )}
    </motion.div>
  );
}
