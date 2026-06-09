"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });

    setLoading(false);

    if (res.ok) {
      router.push("/admin");
      router.refresh();
    } else {
      setError("密码错误，请重试。");
    }
  };

  return (
    <main className="login">
      {/* 背景 */}
      <div className="login__bg">
        <img src="/uploads/glass-shadow.png" alt="" />
        <div className="photo-hero__overlay" />
      </div>

      {/* 登录卡片 */}
      <div className="login__card">
        <div className="login__brand">Atelier</div>

        <div className="login__header">
          <h1 className="login__title">登录</h1>
          <p className="login__sub">输入凭据以管理后台</p>
        </div>

        {error && <div className="login__error login__error--visible">{error}</div>}

        <form className="login__form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="password">密码</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="输入密码"
            />
          </div>
          <button type="submit" disabled={loading} className="login__submit">
            {loading ? "验证中…" : "登录"}
          </button>
        </form>
      </div>
    </main>
  );
}
