#!/bin/bash

# WALKerHOLIC 프로젝트 자동 설정 스크립트
# 이 스크립트는 Git Bash에서 실행하세요

echo "🚀 WALKerHOLIC 프로젝트 설정을 시작합니다..."

# 프로젝트 루트 디렉토리 설정
PROJECT_ROOT="/c/WALKerHOLIC"

# 프로젝트 디렉토리 생성
echo "📁 프로젝트 디렉토리 생성 중..."
mkdir -p "$PROJECT_ROOT"
cd "$PROJECT_ROOT"

# 필요한 디렉토리 구조 생성
mkdir -p src/{assets/images,components/common,pages,services/api,utils}
mkdir -p public

# package.json 생성
echo "📦 package.json 생성 중..."
cat > package.json << 'EOF'
{
  "name": "walkerholic",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "axios": "^1.6.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.56",
    "@types/react-dom": "^18.2.19",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "vite": "^5.1.4"
  }
}
EOF

# vite.config.js 생성
echo "⚙️ vite.config.js 생성 중..."
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    open: true
  }
})
EOF

# tailwind.config.js 생성
echo "🎨 tailwind.config.js 생성 중..."
cat > tailwind.config.js << 'EOF'
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
      },
      width: {
        'mobile': '430px',
      }
    },
  },
  plugins: [],
}
EOF

# postcss.config.js 생성
echo "📮 postcss.config.js 생성 중..."
cat > postcss.config.js << 'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# index.html 생성
echo "📄 index.html 생성 중..."
cat > index.html << 'EOF'
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>WALKerHOLIC</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
EOF

# src/main.jsx 생성
echo "🔧 src/main.jsx 생성 중..."
cat > src/main.jsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
EOF

# src/index.css 생성
echo "🎨 src/index.css 생성 중..."
cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 전역 스타일 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #root {
  width: 100%;
  height: 100%;
  overflow-x: hidden;
}

/* 모바일 앱 느낌을 위한 기본 스타일 */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  touch-action: pan-x pan-y;
  -webkit-tap-highlight-color: transparent;
}

/* 스크롤바 숨기기 */
::-webkit-scrollbar {
  display: none;
}
EOF

# src/App.jsx 생성
echo "📱 src/App.jsx 생성 중..."
cat > src/App.jsx << 'EOF'
import { useState } from 'react'
import HomePage from './pages/HomePage'

function App() {
  return (
    <div className="w-full h-full bg-gray-100">
      <div className="mx-auto max-w-[430px] h-full bg-white shadow-xl">
        <HomePage />
      </div>
    </div>
  )
}

export default App
EOF

# src/pages/HomePage.jsx 생성 (샘플 페이지)
echo "📄 src/pages/HomePage.jsx 생성 중..."
cat > src/pages/HomePage.jsx << 'EOF'
import React from 'react'

const HomePage = () => {
  return (
    <div className="flex flex-col h-full">
      {/* 헤더 */}
      <header className="flex items-center justify-between p-4 bg-white border-b">
        <h1 className="text-xl font-bold">WALKerHOLIC</h1>
        <button className="p-2">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="flex-1 overflow-y-auto p-4">
        <div className="space-y-4">
          <div className="p-6 bg-blue-50 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">환영합니다!</h2>
            <p className="text-gray-600">WALKerHOLIC 앱 개발을 시작해보세요.</p>
          </div>
          
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium mb-2">개발 가이드</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• src/pages 폴더에 새로운 페이지를 추가하세요</li>
              <li>• src/components에 재사용 가능한 컴포넌트를 만드세요</li>
              <li>• src/services/api에 API 연동 코드를 작성하세요</li>
            </ul>
          </div>
        </div>
      </main>

      {/* 하단 네비게이션 (예시) */}
      <nav className="flex items-center justify-around p-4 bg-white border-t">
        <button className="flex flex-col items-center gap-1">
          <div className="w-6 h-6 bg-gray-400 rounded"></div>
          <span className="text-xs">홈</span>
        </button>
        <button className="flex flex-col items-center gap-1">
          <div className="w-6 h-6 bg-gray-400 rounded"></div>
          <span className="text-xs">탐색</span>
        </button>
        <button className="flex flex-col items-center gap-1">
          <div className="w-6 h-6 bg-gray-400 rounded"></div>
          <span className="text-xs">기록</span>
        </button>
        <button className="flex flex-col items-center gap-1">
          <div className="w-6 h-6 bg-gray-400 rounded"></div>
          <span className="text-xs">프로필</span>
        </button>
      </nav>
    </div>
  )
}

export default HomePage
EOF

# src/services/api/index.js 생성
echo "🔌 src/services/api/index.js 생성 중..."
cat > src/services/api/index.js << 'EOF'
import axios from 'axios'

// API 기본 설정
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // 토큰이 있다면 헤더에 추가
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // 에러 처리
    if (error.response?.status === 401) {
      // 인증 에러 처리
      localStorage.removeItem('token')
      // 로그인 페이지로 리다이렉트 등
    }
    return Promise.reject(error)
  }
)

export default api
EOF

# .gitignore 생성
echo "🚫 .gitignore 생성 중..."
cat > .gitignore << 'EOF'
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Environment files
.env
.env.local
.env.production
EOF

# public/vite.svg 생성
echo "🖼️ public/vite.svg 생성 중..."
cat > public/vite.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--logos" width="31.88" height="32" preserveAspectRatio="xMidYMid meet" viewBox="0 0 256 257"><defs><linearGradient id="IconifyId1813088fe1fbc01fb466" x1="-.828%" x2="57.636%" y1="7.652%" y2="78.411%"><stop offset="0%" stop-color="#41D1FF"></stop><stop offset="100%" stop-color="#BD34FE"></stop></linearGradient><linearGradient id="IconifyId1813088fe1fbc01fb467" x1="43.376%" x2="50.316%" y1="2.242%" y2="89.03%"><stop offset="0%" stop-color="#FFEA83"></stop><stop offset="8.333%" stop-color="#FFDD35"></stop><stop offset="100%" stop-color="#FFA800"></stop></linearGradient></defs><path fill="url(#IconifyId1813088fe1fbc01fb466)" d="M255.153 37.938L134.897 252.976c-2.483 4.44-8.862 4.466-11.382.048L.875 37.958c-2.746-4.814 1.371-10.646 6.827-9.67l120.385 21.517a6.537 6.537 0 0 0 2.322-.004l117.867-21.483c5.438-.991 9.574 4.796 6.877 9.62Z"></path><path fill="url(#IconifyId1813088fe1fbc01fb467)" d="M185.432.063L96.44 17.501a3.268 3.268 0 0 0-2.634 3.014l-5.474 92.456a3.268 3.268 0 0 0 3.997 3.378l24.777-5.718c2.318-.535 4.413 1.507 3.936 3.838l-7.361 36.047c-.495 2.426 1.782 4.5 4.151 3.78l15.304-4.649c2.372-.72 4.652 1.36 4.15 3.788l-11.698 56.621c-.732 3.542 3.979 5.473 5.943 2.437l1.313-2.028l72.516-144.72c1.215-2.423-.88-5.186-3.54-4.672l-25.505 4.922c-2.396.462-4.435-1.77-3.759-4.114l16.646-57.705c.677-2.35-1.37-4.583-3.769-4.113Z"></path></svg>
EOF

# start.sh 생성
echo "🚀 start.sh 생성 중..."
cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 WALKerHOLIC 개발 서버를 시작합니다..."
echo ""
echo "📱 모바일 접속 정보:"
echo "-------------------"

# IP 주소 가져오기 (Windows용)
IP=$(ipconfig | grep -A 4 'Wireless LAN adapter Wi-Fi' | grep 'IPv4' | awk '{print $NF}')
if [ -z "$IP" ]; then
    IP=$(ipconfig | grep -A 4 'Ethernet adapter' | grep 'IPv4' | awk '{print $NF}')
fi

echo "로컬: http://localhost:5173"
echo "네트워크: http://$IP:5173"
echo ""
echo "📌 같은 Wi-Fi에 연결된 모바일 기기에서 위 네트워크 주소로 접속하세요!"
echo "-------------------"
echo ""

# 개발 서버 실행
npm run dev
EOF

# 실행 권한 부여
chmod +x start.sh

# npm 패키지 설치
echo "📦 npm 패키지 설치 중... (시간이 좀 걸릴 수 있습니다)"
npm install

echo ""
echo "✅ WALKerHOLIC 프로젝트 설정이 완료되었습니다!"
echo ""
echo "🎯 다음 단계:"
echo "1. 개발 서버 시작: ./start.sh"
echo "2. 브라우저에서 http://localhost:5173 접속"
echo "3. 모바일에서는 같은 네트워크의 IP 주소로 접속"
echo ""
echo "📁 프로젝트 위치: $PROJECT_ROOT"
echo ""
echo "Happy Coding! 🚀"
EOF

# 추가 유틸리티 파일 생성
cat > src/utils/constants.js << 'EOF'
// 앱 전역 상수
export const APP_NAME = 'WALKerHOLIC'

// 디바이스 사이즈
export const DEVICE_SIZES = {
  IPHONE_14_PLUS: {
    width: 430,
    height: 932
  }
}

// API 엔드포인트
export const API_ENDPOINTS = {
  // 예시 엔드포인트
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REGISTER: '/auth/register'
  },
  USER: {
    PROFILE: '/user/profile',
    UPDATE: '/user/update'
  }
}
EOF

# 샘플 컴포넌트 생성
cat > src/components/common/Button.jsx << 'EOF'
import React from 'react'

const Button = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'medium',
  fullWidth = false,
  disabled = false,
  className = ''
}) => {
  const baseClasses = 'font-medium rounded-lg transition-colors focus:outline-none focus:ring-2'
  
  const variants = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-300',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-300',
    danger: 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-300'
  }
  
  const sizes = {
    small: 'px-3 py-1.5 text-sm',
    medium: 'px-4 py-2',
    large: 'px-6 py-3 text-lg'
  }
  
  const classes = `
    ${baseClasses}
    ${variants[variant]}
    ${sizes[size]}
    ${fullWidth ? 'w-full' : ''}
    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
    ${className}
  `
  
  return (
    <button
      className={classes}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}

export default Button
EOF

echo "✅ 모든 파일이 성공적으로 생성되었습니다!"