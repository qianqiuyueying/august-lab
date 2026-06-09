import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Atelier · 光影几何",
  description: "一个以光影和几何为核心的深色设计系统。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
