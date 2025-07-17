/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6366f1',
          dark: '#4f46e5',
          light: '#818cf8'
        },
        secondary: {
          DEFAULT: '#14b8a6',
          dark: '#0d9488',
          light: '#2dd4bf'
        },
        background: {
          light: '#f9fafb',
          dark: '#111827'
        },
        surface: {
          light: '#ffffff',
          dark: '#1f2937'
        }
      },
      backgroundImage: {
        'gradient-light': 'linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 50%, #e0f7fa 100%)',
        'gradient-dark': 'linear-gradient(135deg, #1e293b 0%, #0f172a 50%, #1a237e 100%)',
      }
    },
  },
  plugins: [],
};