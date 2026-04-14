import { useState, type FormEvent } from 'react';
import { motion } from 'framer-motion';

interface CommentFormProps {
  onSubmit: (comment: { author_name: string; author_email: string; content: string }) => Promise<unknown>;
}

export default function CommentForm({ onSubmit }: CommentFormProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name || !email || !content) return;
    setSubmitting(true);
    try {
      await onSubmit({ author_name: name, author_email: email, content });
      setName('');
      setEmail('');
      setContent('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="昵称"
          required
          className="border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
        />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="邮箱"
          required
          className="border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
        />
      </div>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="写下你的评论..."
        required
        rows={3}
        className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
      />
      <motion.button
        type="submit"
        disabled={submitting}
        whileTap={{ scale: submitting ? 1 : 0.98 }}
        className="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors"
      >
        {submitting ? '提交中...' : '发表评论'}
      </motion.button>
    </form>
  );
}
