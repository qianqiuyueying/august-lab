import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import HomePage from './pages/HomePage';
import BlogPage from './pages/BlogPage';
import ProductsPage from './pages/ProductsPage';
import AboutPage from './pages/AboutPage';
import ArticlePage from './pages/ArticlePage';
import LoginPage from './pages/LoginPage';
import CreateArticlePage from './pages/CreateArticlePage';
import StaticPage from './pages/StaticPage';
import PageManagePage from './pages/PageManagePage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="blog" element={<BlogPage />} />
            <Route path="products" element={<ProductsPage />} />
            <Route path="about" element={<AboutPage />} />
            <Route path="articles/:slug" element={<ArticlePage />} />
            <Route path="articles/new" element={<CreateArticlePage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="pages/manage" element={<PageManagePage />} />
            <Route path=":slug" element={<StaticPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
