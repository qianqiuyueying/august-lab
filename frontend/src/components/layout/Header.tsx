import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export default function Header() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <header className="bg-white dark:bg-gray-800 shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-xl font-bold text-gray-900 dark:text-white">
            Tech Blog
          </Link>
          <nav className="flex items-center space-x-4">
            <Link to="/" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
              首页
            </Link>
            {isAuthenticated ? (
              <>
                <Link to="/articles/new" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                  写文章
                </Link>
                <Link to="/pages/manage" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                  页面管理
                </Link>
                <button onClick={logout} className="text-red-600 hover:text-red-500">
                  退出
                </button>
              </>
            ) : (
              <Link to="/login" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                登录
              </Link>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
