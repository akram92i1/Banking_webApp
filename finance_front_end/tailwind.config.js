/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: "#F5FBF8", // Keeping for legacy, but we will move to dark
        "brand-dark": "#0f172a", // Slate 900
        "brand-darker": "#020617", // Slate 950
        "brand-card": "#1e293b", // Slate 800
        "brand-accent": "#3b82f6", // Blue 500 (Professional Blue)
        "brand-muted": "#64748b", // Slate 500
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        thinking: {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '50%': { transform: 'scale(1.05)', opacity: '0.8' }, // Subtle thinking
          '100%': { transform: 'scale(1)', opacity: '1' },
        }
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.5s ease-out forwards',
        'pulse-soft': 'pulse-soft 3s ease-in-out infinite',
        'thinking': 'thinking 1.5s infinite ease-in-out',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}