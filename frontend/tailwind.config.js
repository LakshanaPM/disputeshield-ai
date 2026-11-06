/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        paypal: {
          navy: '#00457C',
          marine: '#0079C1',
          blue: '#0079C1',      // backwards compat
          dark: '#00457C',      // backwards compat
          cyan: '#00cfde',
          sky: '#E6F4FC',
          light: '#E6F4FC',
        },
        surface: {
          light: '#F8FAFC',
          card: '#FFFFFF',
          elevated: '#FFFFFF',
          dark: '#0a0e17',
        },
        status: {
          green: '#10b981',
          yellow: '#f59e0b',
          orange: '#f97316',
          red: '#ef4444',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': {
            opacity: '1',
            transform: 'scale(1)',
            boxShadow: '0 0 0 0 rgba(16, 185, 129, 0.7)',
          },
          '50%': {
            opacity: '0.85',
            transform: 'scale(1.05)',
            boxShadow: '0 0 0 6px rgba(16, 185, 129, 0)',
          },
        },
        fadeIn: {
          from: { opacity: '0', transform: 'translateY(4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s infinite cubic-bezier(0.4, 0, 0.6, 1)',
        'fade-in': 'fadeIn 0.3s ease-out forwards',
      },
    },
  },
  plugins: [],
};
