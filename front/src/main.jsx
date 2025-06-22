import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// PWA 풀스크린 최적화
const optimizePWA = () => {
  // iOS 상태바 스타일 설정
  const setStatusBarStyle = () => {
    // iOS 상태바를 앱 색상에 맞게 설정
    let metaStatusBar = document.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]')
    if (metaStatusBar) {
      metaStatusBar.setAttribute('content', 'black-translucent')
    }
  }

  // 뷰포트 높이 동적 조정 (iOS Safari 하단바 대응)
  const setViewportHeight = () => {
    const vh = window.innerHeight * 0.01
    document.documentElement.style.setProperty('--vh', `${vh}px`)
  }

  // 전체화면 모드 요청 (Android Chrome 등)
  const requestFullscreen = () => {
    if ('requestFullscreen' in document.documentElement) {
      // 사용자 제스처 이후에만 fullscreen 가능
      document.addEventListener('touchstart', () => {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(err => {
            console.log('Fullscreen request failed:', err)
          })
        }
      }, { once: true })
    }
  }

  // PWA 설치 감지
  const handlePWAInstall = () => {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault()
      console.log('PWA 설치 가능')
    })
  }

  // iOS PWA 감지
  const isiOSPWA = () => {
    return window.navigator.standalone === true
  }

  // Android PWA 감지  
  const isAndroidPWA = () => {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.matchMedia('(display-mode: fullscreen)').matches
  }

  // 초기 설정
  setStatusBarStyle()
  setViewportHeight()
  handlePWAInstall()

  // PWA 환경에서만 fullscreen 시도
  if (isiOSPWA() || isAndroidPWA()) {
    console.log('PWA 모드 감지됨')
    // iOS PWA에서는 이미 fullscreen이므로 추가 처리 불필요
    if (!isiOSPWA()) {
      requestFullscreen()
    }
  }

  // 리사이즈 이벤트 처리
  window.addEventListener('resize', setViewportHeight)
  window.addEventListener('orientationchange', () => {
    setTimeout(setViewportHeight, 100)
  })
}

// DOM 로드 후 PWA 최적화 실행
document.addEventListener('DOMContentLoaded', optimizePWA)

// 개발 환경에서는 StrictMode 해제 (Supabase 실시간 구독 테스트를 위해)
// 프로덕션에서는 StrictMode 활성화
const AppWrapper = import.meta.env.DEV ? 
  ({ children }) => children : 
  ({ children }) => <StrictMode>{children}</StrictMode>

createRoot(document.getElementById('root')).render(
  <AppWrapper>
    <App />
  </AppWrapper>,
)
