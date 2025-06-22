import React, { useEffect, useState } from 'react'

const SplashPage = ({ onComplete }) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // 페이지 로드 시 애니메이션 효과
    setIsVisible(true)
    
    // 3초 후 자동으로 메인 페이지로 이동
    const timer = setTimeout(() => {
      if (onComplete) {
        onComplete()
      }
    }, 3000)

    return () => clearTimeout(timer)
  }, [onComplete])

  return (
    <div className="w-full h-full flex items-center justify-center bg-gray-100">
      {/* 메인 컨테이너 - 반응형 flex 레이아웃 */}
      <div 
        className="page-container bg-splash-blue flex flex-col items-center justify-between p-8 w-full h-full max-w-md relative"
        style={{
          borderRadius: '34.73px',
          maxHeight: '100vh'
        }}
      >
        {/* 상단 컨텐츠 영역 */}
        <div className="flex-1 flex flex-col items-center justify-center">
          <div 
            className={`flex flex-col items-center gap-6 transform transition-all duration-1000 ease-out ${
              isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
            }`}
          >
            {/* 타이틀 섹션 */}
            <div className="flex flex-col items-center gap-3 text-center">
              {/* bODYFENCE - 메인 타이틀 */}
              <h1 
                className="font-lilita text-white uppercase leading-none"
                style={{
                  fontSize: 'clamp(3rem, 10vw, 5rem)',
                  textShadow: '0px 4.63px 4.63px rgba(21, 33, 167, 0.25)',
                  WebkitTextStroke: '1.16px #00278C'
                }}
              >
                bODYFENCE
              </h1>
              
              {/* Walk Safe, Live Smart - 부제목 */}
              <p 
                className="font-league-spartan font-thin text-white uppercase text-center px-4"
                style={{
                  fontSize: 'clamp(1.2rem, 4vw, 1.8rem)',
                  lineHeight: '0.92em'
                }}
              >
                Walk Safe, Live Smart
              </p>
            </div>
          </div>
        </div>

        {/* 하단 WALKer HOLIC 텍스트 */}
        <div 
          className={`mb-8 transform transition-all duration-1000 ease-out delay-500 ${
            isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
          }`}
        >
          <p 
            className="font-league-spartan font-semibold text-white uppercase text-center"
            style={{
              fontSize: 'clamp(0.8rem, 3vw, 1.1rem)',
              lineHeight: '0.92em',
              fontWeight: 600
            }}
          >
            WALKer HOLIC
          </p>
        </div>

        {/* 로딩 인디케이터 */}
        <div 
          className={`absolute bottom-16 left-1/2 transform -translate-x-1/2 transition-all duration-1000 ease-out delay-1000 ${
            isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
          }`}
        >
          <div className="flex space-x-2">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-white rounded-full animate-pulse delay-150"></div>
            <div className="w-2 h-2 bg-white rounded-full animate-pulse delay-300"></div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SplashPage 