import React, { useState } from 'react'

const LoginPage = ({ onDemoClick, onLoginClick }) => {
  const [isVisible, setIsVisible] = useState(false)
  const [step, setStep] = useState('login') // 'login' | 'userInfo'
  const [userInfo, setUserInfo] = useState({
    name: '',
    height: '',
    gender: '',
    guardianPhone: ''
  })

  React.useEffect(() => {
    // 페이지 로드 시 애니메이션 효과
    setIsVisible(true)
  }, [])

  // 로그인 버튼 클릭 처리
  const handleLoginClick = () => {
    setStep('userInfo')
  }

  // 개인정보 입력 완료 처리
  const handleUserInfoSubmit = () => {
    // 입력 검증
    if (!userInfo.name.trim()) {
      alert('이름을 입력해주세요.')
      return
    }
    if (!userInfo.height || userInfo.height < 100 || userInfo.height > 250) {
      alert('키를 올바르게 입력해주세요. (100-250cm)')
      return
    }
    if (!userInfo.gender) {
      alert('성별을 선택해주세요.')
      return
    }
    if (!userInfo.guardianPhone.trim()) {
      alert('보호자 전화번호를 입력해주세요.')
      return
    }
    // 전화번호 형식 검증 (간단한 검증)
    const phoneRegex = /^[0-9-+\s()]{10,15}$/
    if (!phoneRegex.test(userInfo.guardianPhone.replace(/\s/g, ''))) {
      alert('올바른 전화번호 형식을 입력해주세요.')
      return
    }

    // 로컬 스토리지에 사용자 정보 저장
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    localStorage.setItem('userId', `user_${Date.now()}`) // 임시 사용자 ID 생성

    // 메인 페이지로 이동
    if (onLoginClick) {
      onLoginClick()
    }
  }

  // 로그인 화면 렌더링
  if (step === 'login') {
    return (
      <div className="w-full h-full flex items-center justify-center">
        {/* 메인 컨테이너 - 반응형 flex 레이아웃 */}
        <div 
          className="page-container bg-login-bg w-full h-full max-w-md flex flex-col items-center justify-center relative"
          style={{
            borderRadius: '34.725px',
            height: 'calc(var(--vh, 1vh) * 100)', // 동적 뷰포트 높이
            paddingTop: 'max(env(safe-area-inset-top), 48px)',
            paddingBottom: 'max(env(safe-area-inset-bottom), 48px)',
            paddingLeft: 'calc(max(env(safe-area-inset-left), 16px) + 24px)',
            paddingRight: 'calc(max(env(safe-area-inset-right), 16px) + 24px)'
          }}
        >
          {/* 중앙 컨텐츠 영역 */}
          <div className="flex-1 flex flex-col items-center justify-center space-y-8">
            {/* WALKer HOLIC - 상단 텍스트 */}
            <div 
              className={`transform transition-all duration-1000 ease-out ${
                isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
              }`}
            >
              <p 
                className="font-league-spartan font-semibold text-login-blue uppercase text-center"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 0.9rem)',
                  lineHeight: '0.92em',
                  fontWeight: 600
                }}
              >
                WALKer HOLIC
              </p>
            </div>

            {/* bODYFENCE - 메인 타이틀 */}
            <div 
              className={`transform transition-all duration-1000 ease-out delay-200 ${
                isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
              }`}
            >
              <h1 
                className="font-lilita text-login-text-blue uppercase text-center"
                style={{
                  fontSize: 'clamp(3rem, 10vw, 5rem)',
                  lineHeight: '1.143em',
                  fontWeight: 400,
                  textShadow: '0px 4.63px 4.63px rgba(21, 33, 167, 0.25)',
                  WebkitTextStroke: '1.16px #00278C'
                }}
              >
                bODYFENCE
              </h1>
            </div>
            
            {/* Walk Safe, Live Smart - 부제목 */}
            <div 
              className={`transform transition-all duration-1000 ease-out delay-400 ${
                isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
              }`}
            >
              <p 
                className="font-league-spartan font-thin text-login-text-blue uppercase text-center px-4"
                style={{
                  fontSize: 'clamp(1.2rem, 4vw, 1.8rem)',
                  lineHeight: '0.92em',
                  fontWeight: 100
                }}
              >
                Walk Safe, Live Smart
              </p>
            </div>
          </div>

          {/* 하단 버튼 영역 */}
          <div className="w-full space-y-4 max-w-xs">
            {/* 시작하기 버튼 */}
            <div 
              className={`cursor-pointer transform transition-all duration-1000 ease-out delay-600 ${
                isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
              }`}
              onClick={handleLoginClick}
            >
              <div 
                className="w-full h-12 bg-login-blue flex items-center justify-center"
                style={{
                  borderRadius: '34.73px'
                }}
              >
                <span 
                  className="text-white text-center uppercase"
                  style={{
                    fontFamily: 'SUIT Variable, sans-serif',
                    fontSize: 'clamp(1rem, 4vw, 1.4rem)',
                    lineHeight: '1.248em',
                    fontWeight: 600,
                    letterSpacing: '10%'
                  }}
                >
                  시작하기
                </span>
              </div>
            </div>

            {/* 데모버전 버튼 */}
            <div 
              className={`cursor-pointer transform transition-all duration-1000 ease-out delay-800 ${
                isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
              }`}
              onClick={onDemoClick}
            >
              <div 
                className="w-full h-12 bg-login-demo-bg flex items-center justify-center"
                style={{
                  borderRadius: '34.73px'
                }}
              >
                <span 
                  className="text-login-blue text-center uppercase"
                  style={{
                    fontFamily: 'Abhaya Libre ExtraBold, serif',
                    fontSize: 'clamp(1rem, 4vw, 1.4rem)',
                    lineHeight: '1.18em',
                    fontWeight: 800,
                    letterSpacing: '-1%'
                  }}
                >
                  데모버전
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // 개인정보 입력 화면 렌더링
  return (
    <div className="w-full h-full flex items-center justify-center">
      <div 
        className="page-container bg-login-bg w-full h-full max-w-md flex flex-col relative overflow-y-auto"
                  style={{
            borderRadius: '34.725px',
            height: 'calc(var(--vh, 1vh) * 100)', // 동적 뷰포트 높이
            paddingTop: 'max(env(safe-area-inset-top), 16px)',
            paddingBottom: 'max(env(safe-area-inset-bottom), 16px)',
            paddingLeft: 'calc(max(env(safe-area-inset-left), 16px) + 24px)',
            paddingRight: 'calc(max(env(safe-area-inset-right), 16px) + 24px)'
          }}
      >
        {/* 헤더 */}
        <div className="pt-4 pb-6 flex-shrink-0">
          <button 
            onClick={() => setStep('login')}
            className="text-login-blue text-2xl mb-4"
          >
            ←
          </button>
          <h2 
            className="font-lilita text-login-text-blue text-2xl mb-2"
            style={{
              textShadow: '0px 4.63px 4.63px rgba(21, 33, 167, 0.25)',
              WebkitTextStroke: '0.5px #00278C'
            }}
          >
            개인정보 입력
          </h2>
          <p className="text-login-blue text-sm">
            정확한 보행 분석을 위해 정보를 입력해주세요
          </p>
        </div>

        {/* 입력 폼 - 스크롤 가능 영역 */}
        <div className="flex-1 space-y-5 min-h-0 px-2">
          {/* 이름 입력 */}
          <div>
            <label className="block text-login-blue text-sm font-medium mb-2">
              이름 *
            </label>
            <input
              type="text"
              value={userInfo.name}
              onChange={(e) => setUserInfo({...userInfo, name: e.target.value})}
              placeholder="이름을 입력하세요"
              className="w-full px-4 py-3 rounded-full border border-login-blue bg-white text-login-blue placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-login-blue"
            />
          </div>

          {/* 키 입력 */}
          <div>
            <label className="block text-login-blue text-sm font-medium mb-2">
              키 (cm) *
            </label>
            <input
              type="number"
              value={userInfo.height}
              onChange={(e) => setUserInfo({...userInfo, height: parseInt(e.target.value) || ''})}
              placeholder="예: 175"
              min="100"
              max="250"
              className="w-full px-4 py-3 rounded-full border border-login-blue bg-white text-login-blue placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-login-blue"
            />
          </div>

          {/* 성별 선택 */}
          <div>
            <label className="block text-login-blue text-sm font-medium mb-3">
              성별 *
            </label>
            <div className="flex space-x-4">
              <button
                onClick={() => setUserInfo({...userInfo, gender: 'male'})}
                className={`flex-1 py-3 rounded-full border transition-all ${
                  userInfo.gender === 'male' 
                    ? 'bg-login-blue text-white border-login-blue' 
                    : 'bg-white text-login-blue border-login-blue'
                }`}
              >
                남성
              </button>
              <button
                onClick={() => setUserInfo({...userInfo, gender: 'female'})}
                className={`flex-1 py-3 rounded-full border transition-all ${
                  userInfo.gender === 'female' 
                    ? 'bg-login-blue text-white border-login-blue' 
                    : 'bg-white text-login-blue border-login-blue'
                }`}
              >
                여성
              </button>
            </div>
          </div>

          {/* 보호자 전화번호 입력 */}
          <div className="pb-4">
            <label className="block text-login-blue text-sm font-medium mb-2">
              보호자 전화번호 *
            </label>
            <input
              type="tel"
              value={userInfo.guardianPhone}
              onChange={(e) => setUserInfo({...userInfo, guardianPhone: e.target.value})}
              placeholder="예: 010-1234-5678"
              className="w-full px-4 py-3 rounded-full border border-login-blue bg-white text-login-blue placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-login-blue"
            />
            <p className="text-xs text-gray-500 mt-1">
              낙상 감지 시 긴급연락을 위한 번호입니다
            </p>
          </div>
        </div>

        {/* 완료 버튼 - 하단 고정 */}
        <div className="pt-4 pb-4 flex-shrink-0 sticky bottom-0 bg-login-bg px-2">
          <button
            onClick={handleUserInfoSubmit}
            className="w-full h-12 bg-login-blue text-white rounded-full font-semibold text-lg transition-all hover:bg-opacity-90 shadow-lg"
          >
            분석 시작하기
          </button>
        </div>
      </div>
    </div>
  )
}

export default LoginPage 