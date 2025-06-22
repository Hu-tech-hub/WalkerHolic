/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      screens: {
        'mobile': '430px',
      },
      height: {
        'mobile': '932px',
        'splash': '926px',
      },
      width: {
        'mobile': '430px',
        'splash': '428px',
      },
      colors: {
        'splash-blue': '#2260FF',
        'splash-blue-dark': '#00278C',
        'login-bg': '#ECF1FF',
        'login-blue': '#2260FF',
        'login-text-blue': '#4378FF',
        'login-demo-bg': '#CAD6FF',
      },
      fontFamily: {
        'lilita': ['Lilita One', 'cursive'],
        'league-spartan': ['League Spartan', 'sans-serif'],
        'noto-sans': ['Noto Sans KR', 'sans-serif'],
        'noto-emoji': ['Noto Emoji', 'sans-serif'],
        'pretendard': ['Pretendard', 'sans-serif'],
        'mulish': ['Mulish', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
      },
      animation: {
        'pulse-delay-150': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) 0.15s infinite',
        'pulse-delay-300': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) 0.3s infinite',
      },
      animationDelay: {
        '150': '150ms',
        '300': '300ms',
        '500': '500ms',
        '1000': '1000ms',
      }
    },
  },
  plugins: [],
}
