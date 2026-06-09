"use client";
import { useState, useRef, useEffect } from "react";

interface Message {
  role: "assistant" | "user";
  content: string;
}

interface ChatBubbleProps {
  visible: boolean;
  onClose: () => void;
  greetingDelay?: number;
}

export default function ChatBubble({ visible, onClose, greetingDelay: defaultGreetingDelay = 8 }: ChatBubbleProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [greeted, setGreeted] = useState(false);
  const [greetingDelay, setGreetingDelay] = useState(defaultGreetingDelay);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Load settings from API
  useEffect(() => {
    fetch("/api/mascot/settings")
      .then((r) => r.json())
      .then((s) => {
        if (s.greetingEnabled != null && !s.greetingEnabled) setGreeted(true); // skip if disabled
        if (s.greetingDelaySeconds != null) setGreetingDelay(s.greetingDelaySeconds);
      })
      .catch(() => {});
  }, []);

  // Auto greeting
  useEffect(() => {
    if (!visible || greeted) return;
    const timer = setTimeout(async () => {
      try {
        const res = await fetch("/api/mascot/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: "你好呀~" }),
        });
        const data = await res.json();
        setMessages([{ role: "assistant", content: data.reply }]);
      } catch {
        setMessages([{ role: "assistant", content: "你好呀！欢迎来到 Atelier~ ⚡" }]);
      }
      setGreeted(true);
    }, greetingDelay * 1000);
    return () => clearTimeout(timer);
  }, [visible, greeted, greetingDelay]);

  // Focus input + scroll on new messages
  useEffect(() => {
    if (visible) setTimeout(() => inputRef.current?.focus(), 150);
  }, [visible]);

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/mascot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "呜...脑子有点乱，待会再聊吧 (´•ω•`)" }]);
    } finally {
      setLoading(false);
    }
  };

  if (!visible) return null;

  return (
    <div
      style={{
        position: "absolute",
        bottom: "100%",
        right: 0,
        marginBottom: 12,
        width: 288,
        borderRadius: 12,
        border: "1px solid var(--c-border)",
        background: "oklch(0.08 0.012 270 / 0.92)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid var(--c-border)",
          padding: "10px 16px",
        }}
      >
        <span style={{ fontFamily: "var(--ff-body)", fontSize: "var(--fs-meta)", fontWeight: 500, color: "var(--c-fg-dim)" }}>
          与小光聊天
        </span>
        <button
          onClick={onClose}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 20,
            height: 20,
            borderRadius: "50%",
            border: "none",
            background: "transparent",
            color: "var(--c-fg-dim)",
            cursor: "pointer",
            fontSize: 14,
            lineHeight: 1,
          }}
        >
          ×
        </button>
      </div>

      {/* Messages */}
      <div
        ref={listRef}
        style={{
          maxHeight: 224,
          overflowY: "auto",
          padding: "12px 16px",
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        {messages.length === 0 && !loading && (
          <p style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", textAlign: "center", padding: "16px 0" }}>
            输入消息开始聊天~
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              fontSize: "var(--fs-meta)",
              lineHeight: 1.6,
              color: msg.role === "assistant" ? "var(--c-fg)" : "var(--c-accent)",
              textAlign: msg.role === "user" ? "right" : "left",
            }}
          >
            {msg.content}
          </div>
        ))}
        {loading && (
          <div style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", opacity: 0.7 }}>
            小光正在思考...
          </div>
        )}
      </div>

      {/* Input */}
      <div
        style={{
          borderTop: "1px solid var(--c-border)",
          padding: "10px 12px",
          display: "flex",
          gap: 8,
          alignItems: "center",
        }}
      >
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") handleSend(); }}
          placeholder="说点什么..."
          disabled={loading}
          style={{
            flex: 1,
            minWidth: 0,
            borderRadius: 8,
            border: "1px solid var(--c-border)",
            background: "rgba(255,255,255,0.04)",
            padding: "6px 12px",
            fontSize: "var(--fs-meta)",
            fontFamily: "var(--ff-body)",
            color: "var(--c-fg)",
            outline: "none",
          }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{
            flexShrink: 0,
            borderRadius: 8,
            border: "1px solid var(--c-accent)",
            background: "oklch(0.55 0.06 90 / 0.15)",
            color: "var(--c-accent)",
            padding: "6px 12px",
            fontSize: "var(--fs-meta)",
            fontFamily: "var(--ff-body)",
            cursor: "pointer",
            fontWeight: 500,
            opacity: loading || !input.trim() ? 0.4 : 1,
          }}
        >
          发送
        </button>
      </div>
    </div>
  );
}
