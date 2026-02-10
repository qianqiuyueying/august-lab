/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // 明确启用 class 模式
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'], // 核心字体
      },
      colors: {
        // 工业风色板
        lab: {
          bg: '#0b0c10',      // 深邃背景
          card: '#1f2833',    // 卡片/模块背景
          text: '#c5c6c7',    // 主要文字
          accent: '#66fcf1',  // 亮青色强调（电光蓝）
          darkAccent: '#45a29e', // 暗青色
        },
        slate: {
          850: '#151f2e',     // 介于 800 和 900 之间
          950: '#020617',
        }
      },
      backgroundImage: {
        'grid-pattern': "linear-gradient(to right, rgba(0,0,0,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(0,0,0,0.05) 1px, transparent 1px)",
        'grid-pattern-dark': "linear-gradient(to right, rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.03) 1px, transparent 1px)",
      },
      animation: {
        'cursor-blink': 'blink 1s step-end infinite',
        'scan': 'scan 8s linear infinite',
      },
      keyframes: {
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        }
      }
    },
  },
  plugins: [],
}
