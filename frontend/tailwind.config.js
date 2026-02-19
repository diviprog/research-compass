/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Campus Blue
        campus: {
          50: '#E6F2FF',
          100: '#CCE4FF',
          200: '#99CAFF',
          300: '#66AFFF',
          400: '#3395FF',
          500: '#0070F3',
          600: '#0060D9',
          700: '#0050BF',
          800: '#0040A6',
          900: '#00308C',
        },
        // Coral Signal
        coral: {
          50: '#FEF2F2',
          100: '#FEE2E2',
          200: '#FECACA',
          300: '#FCA5A5',
          400: '#F87171',
          500: '#EF4444',
          600: '#DC2626',
          700: '#B91C1C',
          800: '#991B1B',
          900: '#7F1D1D',
        },
        // Mint Green
        mint: {
          50: '#ECFDF5',
          100: '#D1FAE5',
          200: '#A7F3D0',
          300: '#6EE7B7',
          400: '#34D399',
          500: '#10B981',
          600: '#059669',
          700: '#047857',
          800: '#065F46',
          900: '#064E3B',
        },
      },
      fontFamily: {
        display: ['Satoshi', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
        body: ['"Roboto Flex"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
        mono: ['"Roboto Mono"', '"Fira Code"', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '104': '26rem',
        '128': '32rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'elevation-1': '0 1px 3px rgba(0, 112, 243, 0.08)',
        'elevation-2': '0 4px 8px rgba(0, 112, 243, 0.12)',
        'elevation-3': '0 8px 16px rgba(0, 112, 243, 0.16)',
        'elevation-4': '0 16px 32px rgba(0, 112, 243, 0.2)',
      },
      transitionTimingFunction: {
        'campus-snap': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'campus-slide': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'campus-float': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      },
      transitionDuration: {
        '50': '50ms',
        '350': '350ms',
      },
      animation: {
        'slide-up': 'slideUp 150ms cubic-bezier(0.34, 1.56, 0.64, 1)',
        'slide-down': 'slideDown 150ms cubic-bezier(0.34, 1.56, 0.64, 1)',
        'fade-in': 'fadeIn 250ms cubic-bezier(0.16, 1, 0.3, 1)',
        'scale-in': 'scaleIn 150ms cubic-bezier(0.34, 1.56, 0.64, 1)',
        'shimmer': 'shimmer 2s infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-4px)' },
        },
      },
    },
  },
  plugins: [],
}

