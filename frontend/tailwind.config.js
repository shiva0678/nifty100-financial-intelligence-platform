export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f7ff',
          100: '#eef2ff',
          200: '#e0e7ff',
          300: '#c7d2fe',
          400: '#a5b4fc',
          500: '#7c3aed',
          600: '#6d28d9',
          700: '#5b21b6',
          800: '#4c1d95',
          900: '#3b1464',
        },
        glass: {
          DEFAULT: 'rgba(255,255,255,0.04)',
          strong: 'rgba(255,255,255,0.06)'
        }
      },
      fontFamily: {
        sans: ['Manrope', 'Inter', 'ui-sans-serif', 'system-ui'],
        display: ['Manrope', 'Inter', 'ui-sans-serif', 'system-ui'],
      },
      boxShadow: {
        'card-sm': '0 6px 18px rgba(2,6,23,0.6)',
        'card-md': '0 12px 40px rgba(2,6,23,0.7)',
        'glow-primary': '0 8px 30px rgba(124,58,237,0.18)'
      },
      borderRadius: {
        'lg-2xl': '1rem'
      },
      keyframes: {
        'float-up': {
          '0%': { transform: 'translateY(6px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'pulse-strong': {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '50%': { transform: 'scale(1.02)', opacity: '.9' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        }
      },
      animation: {
        'float-up': 'float-up 360ms cubic-bezier(.16,1,.3,1)',
        'pulse-strong': 'pulse-strong 3s ease-in-out infinite'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
