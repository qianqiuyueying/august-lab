"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import "./login.css";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  /* ===== URL 参数状态 ===== */
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const state = params.get("state");
    if (state) {
      document.body.dataset.state = state;
      if (state === "error") setError("用户名或密码错误，请重试。");
    }
    return () => { document.body.dataset.state = ""; };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      if (res.ok) {
        router.push("/admin");
        router.refresh();
      } else {
        setLoading(false);
        setError("用户名或密码错误，请重试。");
      }
    } catch {
      setLoading(false);
      document.body.dataset.state = "error";
    }
  };

  return (
    <>
      <main className="login">
        {/* 背景 */}
        <div className="login__bg photo-hero">
          <img src="/uploads/glass-shadow.png" alt="" loading="eager" />
          <div className="photo-hero__overlay"></div>
        </div>

        {/* 登录卡片 */}
        <div className="login__card">
          <div className="login__brand">Atelier</div>

          <div className="login__header">
            <h1 className="login__title">登录</h1>
            <p className="login__sub">输入凭据以管理后台</p>
          </div>

          <div className={`login__error${error ? " login__error--visible" : ""}`}>
            {error || "用户名或密码错误，请重试。"}
          </div>

          <form className="login__form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="password">密码</label>
              <input id="password" type="password" placeholder="输入密码" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            <button type="submit" className={`login__submit${loading ? " login__submit--loading" : ""}`} disabled={loading}>
              {loading ? "验证中…" : "登录"}
            </button>
          </form>
        </div>
      </main>

      {/* 状态 */}
      <div className="state-card login-state-loading login-state-override" style={{ minHeight: "100vh", position: "fixed", inset: 0, zIndex: 9999, background: "var(--c-bg)" }}>
        <div className="state-card__icon" style={{ animation: "pulse 1.5s ease-in-out infinite" }}>⟳</div>
        <div className="state-card__title">验证中</div>
        <p className="state-card__desc">正在验证身份…</p>
        <style>{`@keyframes pulse { 0%,100% { opacity:0.3; } 50% { opacity:0.8; } }`}</style>
      </div>
      <div className="state-card login-state-error login-state-override" style={{ minHeight: "100vh", position: "fixed", inset: 0, zIndex: 9999, background: "var(--c-bg)" }}>
        <div className="state-card__icon">!</div>
        <div className="state-card__title">验证失败</div>
        <p className="state-card__desc">无法连接到认证服务。</p>
        <button className="btn" style={{ marginTop: "var(--sp-lg)" }} onClick={() => window.location.reload()}>重试</button>
      </div>
      <div className="state-card login-state-empty login-state-override" style={{ minHeight: "100vh", position: "fixed", inset: 0, zIndex: 9999, background: "var(--c-bg)" }}>
        <div className="state-card__icon">—</div>
        <div className="state-card__title">服务不可用</div>
        <p className="state-card__desc">认证服务暂未配置。</p>
      </div>
    </>
  );
}
