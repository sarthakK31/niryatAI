"use client";
import { useState, useEffect, useRef } from "react";
import AuthLayout from "@/components/AuthLayout";
import { chat } from "@/lib/api";
import { Send, ImagePlus, Plus, MessageSquare, Loader2 } from "lucide-react";

interface Message {
  role: string;
  content: string;
  created_at?: string;
}

interface Session {
  id: string;
  title: string;
  updated_at: string;
}

export default function ChatPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSession, setActiveSession] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load sessions
  useEffect(() => {
    chat.sessions().then(setSessions).catch(console.error);
  }, []);

  // Load messages when session changes
  useEffect(() => {
    if (activeSession) {
      chat.messages(activeSession).then(setMessages).catch(console.error);
    } else {
      setMessages([]);
    }
  }, [activeSession]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() && !image) return;
    const userMsg = input.trim();
    setInput("");
    setSending(true);

    // Optimistic UI update
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);

    try {
      const res = await chat.send(userMsg, activeSession || undefined, image || undefined);
      setActiveSession(res.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.response }]);
      setImage(null);
      // Refresh session list
      chat.sessions().then(setSessions).catch(console.error);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setSending(false);
    }
  };

  const startNewChat = () => {
    setActiveSession(null);
    setMessages([]);
  };

  return (
    <AuthLayout>
      <div className="flex h-[calc(100vh-4rem)] gap-4">
        {/* Session sidebar */}
        <div className="w-64 bg-[var(--bg-card)] rounded-xl border border-[var(--border)] flex flex-col">
          <div className="p-4 border-b border-[var(--border)]">
            <button
              onClick={startNewChat}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-[var(--primary)] hover:bg-[var(--primary-light)] rounded-lg text-sm font-medium transition-colors"
            >
              <Plus size={16} /> New Chat
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {sessions.map((s) => (
              <button
                key={s.id}
                onClick={() => setActiveSession(s.id)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-sm truncate transition-colors ${
                  activeSession === s.id
                    ? "bg-[var(--primary)] text-white"
                    : "text-[var(--text-secondary)] hover:bg-[var(--border)]"
                }`}
              >
                <MessageSquare size={14} className="inline mr-2" />
                {s.title}
              </button>
            ))}
            {sessions.length === 0 && (
              <p className="text-center text-[var(--text-secondary)] text-sm py-8">
                No conversations yet
              </p>
            )}
          </div>
        </div>

        {/* Chat area */}
        <div className="flex-1 bg-[var(--bg-card)] rounded-xl border border-[var(--border)] flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <MessageSquare size={48} className="text-[var(--border)] mb-4" />
                <h3 className="text-lg font-semibold">How can I help you today?</h3>
                <p className="text-[var(--text-secondary)] text-sm mt-2 max-w-md">
                  Ask me about export procedures, market intelligence, compliance
                  requirements, or upload a document image for analysis.
                </p>
                <div className="flex flex-wrap gap-2 mt-6 max-w-lg justify-center">
                  {[
                    "How do I get an IEC code?",
                    "Best markets for HS 0901?",
                    "What documents do I need to export?",
                    "Country risk for Germany",
                  ].map((q) => (
                    <button
                      key={q}
                      onClick={() => setInput(q)}
                      className="px-3 py-1.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--primary-light)] transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-[var(--primary)] text-white rounded-br-md"
                      : "bg-[var(--bg-dark)] border border-[var(--border)] rounded-bl-md"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {sending && (
              <div className="flex justify-start">
                <div className="bg-[var(--bg-dark)] border border-[var(--border)] px-4 py-3 rounded-2xl rounded-bl-md">
                  <Loader2 size={16} className="animate-spin text-[var(--primary-light)]" />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Image preview */}
          {image && (
            <div className="px-6 py-2 border-t border-[var(--border)]">
              <div className="inline-flex items-center gap-2 bg-[var(--bg-dark)] px-3 py-1.5 rounded-lg text-sm">
                <ImagePlus size={14} />
                {image.name}
                <button
                  onClick={() => setImage(null)}
                  className="text-red-400 hover:text-red-300 ml-1"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-4 border-t border-[var(--border)]">
            <div className="flex items-center gap-3">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => setImage(e.target.files?.[0] || null)}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="p-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--primary-light)] transition-colors"
                title="Upload image"
              >
                <ImagePlus size={20} />
              </button>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                placeholder="Ask about exporting, markets, compliance..."
                className="flex-1 px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-[var(--text-primary)] focus:border-[var(--primary-light)] focus:outline-none"
                disabled={sending}
              />
              <button
                onClick={handleSend}
                disabled={sending || (!input.trim() && !image)}
                className="p-2.5 rounded-lg bg-[var(--primary)] hover:bg-[var(--primary-light)] text-white transition-colors disabled:opacity-50"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </AuthLayout>
  );
}
