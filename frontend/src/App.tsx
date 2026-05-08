import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import AdminLayout from './components/admin/AdminLayout';
import HomePage from './pages/HomePage';
import BlogPage from './pages/BlogPage';
import ProductsPage from './pages/ProductsPage';
import ProductPage from './pages/ProductPage';
import AboutPage from './pages/AboutPage';
import ArticlePage from './pages/ArticlePage';
import LoginPage from './pages/LoginPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminArticles from './pages/admin/AdminArticles';
import AdminProducts from './pages/admin/AdminProducts';
import AdminPages from './pages/admin/AdminPages';
import AdminSettings from './pages/admin/AdminSettings';
import AdminMascot from './pages/admin/AdminMascot';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="blog" element={<BlogPage />} />
            <Route path="products" element={<ProductsPage />} />
            <Route path="products/:slug" element={<ProductPage />} />
            <Route path="about" element={<AboutPage />} />
            <Route path="articles/:slug" element={<ArticlePage />} />
            <Route path="login" element={<LoginPage />} />
          </Route>
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="articles" element={<AdminArticles />} />
            <Route path="products" element={<AdminProducts />} />
            <Route path="pages" element={<AdminPages />} />
            <Route path="settings" element={<AdminSettings />} />
            <Route path="mascot" element={<AdminMascot />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
