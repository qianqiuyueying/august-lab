import { useState, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { login } from '../api/auth';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login: authLogin } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const result = await login(username, password);
      authLogin(result.access_token);
      navigate('/admin');
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-md"
      >
        {/* Brand header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-4">
            <svg className="w-8 h-8" viewBox="0 0 32 32" fill="none">
              <rect x="2" y="2" width="28" height="28" rx="7" className="fill-slate-800 dark:fill-white" />
              <path d="M9 23V9h2.5l3.5 10 3.5-10H21v14h-2V13l-3.2 9h-1.6L11 13v10H9z" className="fill-slate-200 dark:fill-slate-800" />
            </svg>
            <span className="text-lg font-bold text-zinc-900 dark:text-white tracking-tight">August&apos;s Lab</span>
          </Link>
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">登录</h1>
          <p className="text-sm text-zinc-400 dark:text-zinc-500 mt-1">输入凭据以管理后台</p>
        </div>

        {/* Card */}
        <div className="bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 sm:p-8 shadow-sm">
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 text-red-600 dark:text-red-400 p-3 rounded-lg mb-5 text-sm"
            >
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">
                用户名
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full border border-zinc-200 dark:border-zinc-800 rounded-lg px-3.5 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-accent-start/30 focus:border-accent-start transition-all placeholder:text-zinc-400 dark:placeholder:text-zinc-600"
                placeholder="输入用户名"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">
                密码
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full border border-zinc-200 dark:border-zinc-800 rounded-lg px-3.5 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-accent-start/30 focus:border-accent-start transition-all placeholder:text-zinc-400 dark:placeholder:text-zinc-600"
                placeholder="输入密码"
              />
            </div>
            <motion.button
              type="submit"
              disabled={loading}
              whileTap={{ scale: loading ? 1 : 0.98 }}
              className="w-full bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 py-2.5 rounded-lg hover:bg-zinc-800 dark:hover:bg-zinc-100 disabled:opacity-50 font-medium text-sm transition-colors"
            >
              {loading ? '登录中...' : '登录'}
            </motion.button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
