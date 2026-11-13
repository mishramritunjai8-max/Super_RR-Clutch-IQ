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
          950: '#141517',
          900: '#1C1D20',
          850: '#212226',
          800: '#25262A',
          700: '#2B2C30',
          600: '#3A3B40',
        },
        cloud: {
          DEFAULT: '#F2F4F1',
          white: '#F2F4F1',
          muted: '#A6A9A5',
          100: '#F2F4F1',
          200: '#D8DBD6',
          300: '#A6A9A5',
          400: '#717370',
        },
        sunshine: {
          DEFAULT: '#FFC928',
          yellow: '#FFC928',
          hover: '#E5B422',
          glow: 'rgba(255, 201, 40, 0.18)',
          300: '#FFE17D',
          400: '#FFD554',
          500: '#FFC928',
          600: '#E6B015',
          700: '#B88905',
        },
        glass: {
          bg: 'rgba(242, 244, 241, 0.045)',
          border: 'rgba(242, 244, 241, 0.12)',
          subtle: 'rgba(242, 244, 241, 0.08)',
        }
      },
      fontFamily: {
        sans: ['Archivo', 'system-ui', 'sans-serif'],
        display: ['Archivo', 'sans-serif'],
        archivo: ['Archivo', 'sans-serif'],
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
