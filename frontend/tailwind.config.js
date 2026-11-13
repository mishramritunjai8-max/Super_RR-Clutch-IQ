/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        graphite: {
          DEFAULT: '#1C1D20',
          base: '#1C1D20',
          elevated: '#25262A',
          surface: '#2B2C30',
        },
        cloud: {
          DEFAULT: '#F2F4F1',
          white: '#F2F4F1',
          muted: '#A6A9A5',
        },
        sunshine: {
          DEFAULT: '#FFC928',
          yellow: '#FFC928',
          hover: '#E5B422',
          glow: 'rgba(255, 201, 40, 0.18)',
        },
        glass: {
          bg: 'rgba(242, 244, 241, 0.045)',
          border: 'rgba(242, 244, 241, 0.12)',
          subtle: 'rgba(242, 244, 241, 0.08)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'Manrope', 'system-ui', 'sans-serif'],
        display: ['Manrope', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'sunshine-sm': '0 0 15px rgba(255, 201, 40, 0.25)',
        'sunshine-md': '0 0 25px rgba(255, 201, 40, 0.35)',
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
