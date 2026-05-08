import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { sendMascotChat } from '../../api/mascot';

interface Message {
  role: 'assistant' | 'user';
  content: string;
}

interface ChatBubbleProps {
  visible: boolean;
  greetingEnabled?: boolean;
  greetingDelaySeconds?: number;
  onClose: () => void;
}

export default function ChatBubble({
  visible,
  greetingEnabled = true,
  greetingDelaySeconds = 8,
  onClose,
}: ChatBubbleProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [greeted, setGreeted] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto greeting
  useEffect(() => {
    if (!visible || !greetingEnabled || greeted) return;
    const timer = setTimeout(async () => {
      try {
        const res = await sendMascotChat('你好呀~');
        setMessages([{ role: 'assistant', content: res.reply }]);
      } catch {
        setMessages([{ role: 'assistant', content: '你好呀！欢迎来到 August\'s Lab~ ⚡' }]);
      }
      setGreeted(true);
    }, greetingDelaySeconds * 1000);
    return () => clearTimeout(timer);
  }, [visible, greetingEnabled, greeted, greetingDelaySeconds]);

  // Focus input when visible
  useEffect(() => {
    if (visible) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [visible]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    setLoading(true);

    try {
      const context = document.title;
      const res = await sendMascotChat(text, context);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.reply }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'assistant', content: '呜...脑子有点乱，待会再聊吧 (´•ω•`)' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSend();
  };

  if (!visible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 8, scale: 0.96 }}
      transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
      className="absolute bottom-full mb-3 right-0 w-72 rounded-xl border border-white/10 bg-surface-dark/90 backdrop-blur-xl shadow-2xl overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-2.5">
        <span className="text-xs font-bold text-text-muted-dark">与刻晴聊天</span>
        <button
          onClick={onClose}
          className="flex h-5 w-5 items-center justify-center rounded-full text-text-muted-dark hover:bg-white/10 hover:text-text-primary-dark transition-colors text-xs"
        >
          ×
        </button>
      </div>

      {/* Messages */}
      <div className="max-h-56 overflow-y-auto px-4 py-3 space-y-3">
        {messages.length === 0 && !loading && (
          <p className="text-xs text-text-muted-dark text-center py-4">
            输入消息开始聊天~
          </p>
        )}
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className={`text-xs leading-relaxed ${
                msg.role === 'assistant'
                  ? 'text-text-primary-dark'
                  : 'text-accent-mid text-right'
              }`}
            >
              {msg.content}
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <div className="text-xs text-text-muted-dark animate-pulse">
            刻晴正在思考...
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-white/[0.06] px-3 py-2.5 flex items-center gap-2">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="说点什么..."
          disabled={loading}
          className="flex-1 min-w-0 rounded-lg border border-white/[0.08] bg-white/[0.04] px-3 py-1.5 text-xs text-text-primary-dark placeholder:text-text-muted-dark focus:outline-none focus:border-accent/40 transition-colors"
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="shrink-0 rounded-lg bg-accent px-3 py-1.5 text-xs font-bold text-white hover:bg-accent-hover disabled:opacity-40 transition-all"
        >
          发送
        </button>
      </div>
    </motion.div>
  );
}
