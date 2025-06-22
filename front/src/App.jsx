import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import MainPage from './pages/MainPage'
import SplashPage from './pages/SplashPage'
import LoginPage from './pages/LoginPage'
import GaitAnalysisPage from './pages/GaitAnalysisPage'
import CognitiveTestPage from './pages/CognitiveTestPage'
import FallAlert from './components/common/FallAlert'
import FallAlertDebug from './components/common/FallAlertDebug'
import useFallAlert from './hooks/useFallAlert'

function App() {
  const [currentPage, setCurrentPage] = useState('splash') // 'splash', 'login', 'main', 'gait-analysis', 'cognitive-test'
  
  // 낙상 감지 시스템
  const { isFallDetected, isSubscriptionActive, connectionStatus, reconnectAttempts, maxReconnectAttempts, onAlertCancel, onEmergencyCall } = useFallAlert()
  
  // 로컬 스토리지에서 보호자 전화번호 가져오기
  const getGuardianPhone = () => {
    try {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      return userInfo.guardianPhone || ''
    } catch {
      return ''
    }
  }

  const handleSplashComplete = () => {
    setCurrentPage('login')
  }

  const handleDemoClick = () => {
    setCurrentPage('main')
  }

  const handleLoginClick = () => {
    // 실제 로그인 로직을 여기에 추가할 수 있음
    console.log('로그인 버튼 클릭됨')
    // 임시로 메인페이지로 이동
    setCurrentPage('main')
  }

  const handleGaitAnalysisClick = () => {
    console.log('보행 분석 페이지로 이동')
    setCurrentPage('gait-analysis')
  }

  const handleCognitiveTestClick = () => {
    console.log('인지 기능 테스트 페이지로 이동')
    setCurrentPage('cognitive-test')
  }

  const handleBackToMain = () => {
    console.log('메인 페이지로 돌아가기')
    setCurrentPage('main')
  }

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'splash':
        return <SplashPage onComplete={handleSplashComplete} />
      case 'login':
        return <LoginPage onDemoClick={handleDemoClick} onLoginClick={handleLoginClick} />
      case 'main':
        return <MainPage onGaitAnalysisClick={handleGaitAnalysisClick} onCognitiveTestClick={handleCognitiveTestClick} />
      case 'gait-analysis':
        return <GaitAnalysisPage onBackClick={handleBackToMain} />
      case 'cognitive-test':
        return <CognitiveTestPage onBackClick={handleBackToMain} />
      default:
        return <SplashPage onComplete={handleSplashComplete} />
    }
  }

  return (
    <div className="w-screen h-screen bg-gray-100 flex items-center justify-center overflow-hidden">
      <div className="w-full h-full max-w-md bg-gray-100 flex items-center justify-center relative">
        {renderCurrentPage()}
        
        {/* 낙상 감지 알림 모달 */}
        <FallAlert
          isVisible={isFallDetected}
          onCancel={onAlertCancel}
          onEmergencyCall={onEmergencyCall}
          guardianPhone={getGuardianPhone()}
        />
        
        {/* Toast 알림 컨테이너 */}
        <Toaster 
          position="top-center"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />

        {/* 디버깅 컴포넌트 (개발 환경에서만 표시) */}
        {import.meta.env.DEV && (
          <FallAlertDebug 
            connectionStatus={connectionStatus}
            isSubscriptionActive={isSubscriptionActive}
            reconnectAttempts={reconnectAttempts}
            maxReconnectAttempts={maxReconnectAttempts}
          />
        )}
      </div>
    </div>
  )
}

export default App
