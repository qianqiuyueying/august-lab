import { useState, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/useAuth';
import { login } from '../api/auth';
import BrandMark from '../components/ui/BrandMark';

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
    <div className="flex min-h-[60vh] items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-md"
      >
        <div className="mb-8 text-center">
          <Link to="/" className="mb-5 inline-flex rounded-lg focus-ring">
            <BrandMark />
          </Link>
          <h1 className="text-2xl font-extrabold text-text-primary dark:text-text-primary-dark">登录</h1>
          <p className="mt-2 text-sm text-text-muted dark:text-text-muted-dark">输入凭据以管理后台</p>
        </div>

        <div className="paper-panel-strong p-6 sm:p-8">
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mb-5 rounded-lg border border-danger/20 bg-danger-subtle p-3 text-sm font-semibold text-danger dark:bg-danger-subtle-dark"
            >
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-bold text-text-secondary dark:text-text-secondary-dark">
                用户名
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="focus-ring w-full rounded-lg border border-border bg-paper px-3.5 py-2.5 text-sm text-text-primary transition-all placeholder:text-text-muted focus:border-accent dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark"
                placeholder="输入用户名"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-bold text-text-secondary dark:text-text-secondary-dark">
                密码
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="focus-ring w-full rounded-lg border border-border bg-paper px-3.5 py-2.5 text-sm text-text-primary transition-all placeholder:text-text-muted focus:border-accent dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark"
                placeholder="输入密码"
              />
            </div>
            <motion.button
              type="submit"
              disabled={loading}
              whileTap={{ scale: loading ? 1 : 0.98 }}
              className="lab-button w-full disabled:opacity-50"
            >
              {loading ? '登录中...' : '登录'}
            </motion.button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
