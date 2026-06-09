"use client";
import { useEffect, useRef } from "react";

interface ParallaxHeroProps {
  image: string;
  label: string;
  title: string;
  description?: string;
  height?: string;
}

export function ParallaxHero({ image, label, title, description, height = "55vh" }: ParallaxHeroProps) {
  const bgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (!bgRef.current) return;
      const scrollY = window.scrollY;
      bgRef.current.style.transform = `translateY(${scrollY * 0.3}px)`;
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      style={{
        position: "relative",
        width: "100%",
        height,
        minHeight: "420px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      <div
        ref={bgRef}
        style={{
          position: "absolute",
          inset: "-10%",
          willChange: "transform",
        }}
      >
        <img src={image} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </div>

      {/* 渐变遮罩 */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(180deg, oklch(0 0 0 / 0.55) 0%, oklch(0 0 0 / 0.25) 50%, var(--c-bg) 100%)`,
        }}
      />
      {/* 中心聚光 */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse 70% 60% at 50% 50%, transparent 0%, oklch(0 0 0 / 0.3) 100%)",
          pointerEvents: "none",
          zIndex: 1,
        }}
      />

      <div style={{ position: "relative", zIndex: 2, textAlign: "center" }}>
        <p style={{
          fontFamily: "var(--ff-mono)",
          fontSize: "var(--fs-meta)",
          letterSpacing: "0.3em",
          textTransform: "uppercase",
          color: "oklch(0.7 0.01 270 / 0.45)",
          marginBottom: "var(--sp-md)",
        }}>
          {label}
        </p>
        <h1 style={{
          fontFamily: "var(--ff-display)",
          fontSize: "clamp(2.5rem, 5vw, 4.5rem)",
          fontWeight: 400,
          color: "#fff",
          lineHeight: 1.1,
          textShadow: "0 2px 40px oklch(0 0 0 / 0.5)",
          marginBottom: "var(--sp-sm)",
        }}>
          {title}
        </h1>
        {description && (
          <p style={{
            color: "oklch(0.7 0.01 270 / 0.65)",
            fontWeight: 300,
            fontSize: "var(--fs-body)",
            maxWidth: "480px",
            margin: "0 auto",
          }}>
            {description}
          </p>
        )}
      </div>
    </header>
  );
}
