import React from 'react'
import chatbotImage from '../assets/images/worky-original.png'

const MainPage = ({ onGaitAnalysisClick, onCognitiveTestClick }) => {
  // 긴급연락 핸들러
  const handleEmergencyCall = () => {
    try {
      // 로컬 스토리지에서 보호자 전화번호 가져오기
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      const guardianPhone = userInfo.guardianPhone
      
      if (guardianPhone) {
        console.log(`📞 긴급연락: ${guardianPhone}`)
        // 전화 연결
        window.location.href = `tel:${guardianPhone}`
      } else {
        alert('보호자 전화번호가 설정되지 않았습니다.\n로그인 시 보호자 전화번호를 입력해주세요.')
      }
    } catch (error) {
      console.error('❌긴급연락 실패:', error)
      alert('긴급연락에 실패했습니다.')
    }
  }
  return (
    <div className="w-full h-full flex items-center justify-center">
      {/* 메인 컨테이너 - 반응형 flex 레이아웃 */}
      <div 
        className="main-container w-full max-w-md overflow-y-auto relative min-h-screen"
        style={{
          borderRadius: '34.73px'
        }}
      >
        {/* 하단 배경 그라데이션 (전체 덮기) */}
        <div 
          className="absolute top-0 left-0 w-full h-full"
          style={{
            minHeight: '100vh',
            background: 'linear-gradient(180deg, #CAD6FF 0%, #CAD6FF 100%)',
            borderRadius: '34.73px',
            zIndex: 1
          }}
        />
        
        {/* 상단 배경 그라데이션 */}
        <div 
          className="absolute top-0 left-0 w-full"
          style={{
            height: '27.2%',
            minHeight: '272px',
            background: 'linear-gradient(180deg, #ECF1FF 0%, #FFFFFF 100%)',
            borderRadius: '34.73px 34.73px 0 0',
            zIndex: 2
          }}
        />

        {/* 콘텐츠 영역 - 배경 위에 표시되도록 relative z-index 적용 */}
        <div className="relative z-10">
          {/* Header - PWA에서 Safe Area 처리됨 */}
          <div className="flex items-center justify-between p-6 pt-6">
            {/* 좌측 로고 영역 */}
            <div className="flex flex-col">
              <h1 
                className="font-lilita"
                style={{
                  fontSize: 'clamp(1.6rem, 4vw, 1.8rem)',
                  lineHeight: '100%',
                  letterSpacing: '5%',
                  textTransform: 'capitalize',
                  color: '#2260FF',
                  textShadow: '2px 2px 0px #00278C, 4px 4px 8px rgba(21, 33, 167, 0.25)'
                }}
              >
                bODYFENCE
              </h1>
              <p 
                className="font-league-spartan mt-1"
                style={{
                  fontWeight: 100,
                  fontSize: 'clamp(0.9rem, 2.5vw, 0.9rem)',
                  lineHeight: '100%',
                  textTransform: 'capitalize',
                  color: '#4378FF'
                }}
              >
                Walk Safe, Live Smart
              </p>
            </div>

            {/* 우측 버튼 영역 */}
            <div className="flex items-center space-x-3">
              {/* 알림 버튼 */}
              <div 
                className="cursor-pointer relative flex items-center justify-center"
                style={{
                  width: '32px',
                  height: '32px',
                  backgroundColor: '#CAD6FF',
                  borderRadius: '50%'
                }}
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4" style={{ color: '#000000' }}>
                  <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
                </svg>
                {/* 알림 점 */}
                <div 
                  className="absolute top-1 right-1"
                  style={{
                    width: '6px',
                    height: '6px',
                    backgroundColor: '#2260FF',
                    borderRadius: '50%'
                  }}
                />
              </div>

              {/* 설정 버튼 */}
              <div 
                className="cursor-pointer flex items-center justify-center"
                style={{
                  width: '32px',
                  height: '32px',
                  backgroundColor: '#CAD6FF',
                  borderRadius: '50%'
                }}
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4" style={{ color: '#000000' }}>
                  <path d="M12 15.5A3.5 3.5 0 0 1 8.5 12A3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5 3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97 0-.33-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.31-.61-.22l-2.49 1c-.52-.39-1.06-.73-1.69-.98l-.37-2.65A.506.506 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.37 2.65c-.63.25-1.17.59-1.69.98l-2.49-1c-.22-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64L4.57 11c-.04.34-.07.67-.07 1 0 .33.03.65.07.97l-2.11 1.66c-.19.15-.25.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1c.52.4 1.06.74 1.69.99l.37 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.37-2.65c.63-.26 1.17-.59 1.69-.99l2.49 1c.22.08.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.66Z"/>
                </svg>
              </div>
            </div>
          </div>

          {/* 인사말 섹션 */}
          <div className="px-8 mb-6">
            <div className="flex items-baseline space-x-2">
              <p 
                className="font-noto-emoji"
                style={{
                  fontWeight: 300,
                  fontSize: 'clamp(1rem, 4vw, 1.4rem)',
                  color: '#00278C'
                }}
              >
                안녕하세요
              </p>
              <p 
                className="font-noto-sans"
                style={{
                  fontWeight: 600,
                  fontSize: 'clamp(1.5rem, 6vw, 2.2rem)',
                  color: '#00278C'
                }}
              >
                김순자님!
              </p>
            </div>
          </div>

          {/* 챗봇 버튼 */}
          <div className="px-8 mb-6 relative">
            <div 
              className="cursor-pointer p-6 bg-white border-2 border-[#00278C] rounded-[26px]"
              style={{
                minHeight: '118px'
              }}
            >
              <div className="flex items-center space-x-1 mb-4">
                {/* 음성 아이콘 */}
                <div 
                  className="flex items-center justify-center"
                  style={{
                    width: '35px',
                    height: '38px'
                  }}
                >
                  <img 
                    src="/마이크.png" 
                    alt="마이크"
                    className="w-full h-full object-contain"
                  />
                </div>

                {/* 검색 아이콘 */}
                <div 
                  className="flex items-center justify-center"
                  style={{
                    width: '36px',
                    height: '39px'
                  }}
                >
                  <img 
                    src="/돋보기.png" 
                    alt="돋보기"
                    className="w-full h-full object-contain"
                  />
                </div>
              </div>

              {/* 워키를 불러보세요! 텍스트 */}
              <div>
                <p 
                  className="font-league-spartan text-[#00278C]"
                  style={{
                    fontWeight: 500,
                    fontSize: '19.68px',
                    lineHeight: '92%'
                  }}
                >
                  워키를 불러보세요!
                </p>
              </div>
            </div>
            
            {/* 챗봇 이미지 - 우측에 절대 위치로 배치 */}
            <div 
              className="absolute"
              style={{
                right: '0px',
                top: '-35px',
                width: '200px',
                height: '190px',
                borderRadius: '15px',
                zIndex: 10
              }}
            >
              <img 
                src={chatbotImage} 
                alt="챗봇 이미지" 
                className="w-full h-full object-cover rounded-[15px]"
              />
            </div>
          </div>

          {/* 전체보기 텍스트 */}
          <div className="px-8 mb-2">
            <p 
              className="font-league-spartan text-[#2260FF]"
              style={{
                fontWeight: 300,
                fontSize: 'clamp(0.6rem, 2.5vw, 0.8rem)',
                lineHeight: '100%',
                textAlign: 'left',
                textTransform: 'capitalize'
              }}
            >
              전체보기
            </p>
          </div>

          {/* 테스트모드 버튼 */}
          <div className="px-8 mb-6">
            <div 
              onClick={onCognitiveTestClick}
              className="cursor-pointer p-6 bg-white border-2 border-[#3D6DEA] rounded-3xl shadow-lg hover:opacity-90 transition-opacity"
            >
              <div className="flex items-center justify-between">
                <div className="flex flex-col">
                  <p 
                    className="font-league-spartan text-[#00278C] mb-2"
                    style={{
                      fontWeight: 700,
                      fontSize: 'clamp(1.2rem, 5vw, 1.6rem)',
                      lineHeight: '100%'
                    }}
                  >
                    테스트 모드
                  </p>
                  <p 
                    className="font-league-spartan text-[#00278C]"
                    style={{
                      fontWeight: 500,
                      fontSize: 'clamp(0.6rem, 2.5vw, 0.8rem)',
                      lineHeight: '100%'
                    }}
                  >
                    낙상 위험 및 인지기능 검사
                  </p>
                </div>

                <div className="flex items-center space-x-4">
                  <p 
                    className="font-league-spartan text-[#00278C]"
                    style={{
                      fontWeight: 500,
                      fontSize: 'clamp(1.5rem, 6vw, 2.2rem)',
                      lineHeight: '100%',
                      textAlign: 'center'
                    }}
                  >
                    88점
                  </p>

                  {/* 테스트 모드 아이콘 */}
                  <div 
                    className="flex items-center justify-center"
                    style={{
                      width: '53.35px',
                      height: '48.57px'
                    }}
                  >
                    <img 
                      src="/테스트모드.png" 
                      alt="테스트모드"
                      className="w-full h-full object-contain"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 카드 그리드 섹션 */}
          <div className="px-8 mb-6">
            {/* 첫 번째 행 */}
            <div className="flex gap-3 mb-4">
              {/* 건강상태 버튼 */}
              <div 
                className="cursor-pointer bg-white border-2 border-[#3D6DEA] rounded-3xl shadow-lg p-4 flex-1"
                style={{
                  height: '155.11px'
                }}
              >
                <div className="flex flex-col h-full">
                  {/* 제목 */}
                  <p 
                    className="font-league-spartan text-[#00278C] mb-3"
                    style={{
                      fontWeight: 700,
                      fontSize: '20.835px',
                      lineHeight: '92%',
                      textAlign: 'left'
                    }}
                  >
                    건강 상태
                  </p>

                  {/* 아이콘 */}
                  <div 
                    className="flex items-center justify-center mb-4"
                    style={{
                      width: '47.56px',
                      height: '41.67px',
                      margin: '0 auto'
                    }}
                  >
                    <img 
                      src="/chart-line.png" 
                      alt="건강 상태"
                      className="w-full h-full object-contain"
                      style={{ 
                        filter: 'brightness(0) saturate(100%) invert(27%) sepia(99%) saturate(7426%) hue-rotate(233deg) brightness(102%) contrast(101%)'
                      }}
                    />
                  </div>

                  {/* 수치 */}
                  <div className="text-center mt-auto">
                    <p 
                      className="font-league-spartan text-[#00278C] mb-1"
                      style={{
                        fontWeight: 500,
                        fontSize: '27.78px',
                        lineHeight: '92%'
                      }}
                    >
                      86%
                    </p>

                    {/* 상태 메시지 */}
                    <p 
                      className="font-league-spartan text-[#00278C]"
                      style={{
                        fontWeight: 500,
                        fontSize: '13.89px',
                        lineHeight: '92%'
                      }}
                    >
                      건강 상태 매우 양호
                    </p>
                  </div>
                </div>
              </div>

              {/* 보행분석 버튼 */}
              <div 
                onClick={onGaitAnalysisClick}
                className="cursor-pointer bg-white border-2 border-[#3D6DEA] rounded-3xl shadow-lg hover:opacity-90 transition-opacity p-4 flex-1"
                style={{
                  height: '155.11px'
                }}
              >
                <div className="flex flex-col h-full">
                  {/* 제목 */}
                  <p 
                    className="font-league-spartan text-[#00278C] mb-3"
                    style={{
                      fontWeight: 700,
                      fontSize: '20.835px',
                      lineHeight: '92%',
                      textAlign: 'left'
                    }}
                  >
                    보행 분석
                  </p>

                  {/* 아이콘 */}
                  <div 
                    className="flex items-center justify-center mb-4"
                    style={{
                      width: '50px',
                      height: '48px',
                      margin: '-8px auto 0 auto'
                    }}
                  >
                    <img 
                      src="/보행_f.png" 
                      alt="보행 분석"
                      className="w-full h-full object-contain"
                    />
                  </div>

                  {/* 수치 */}
                  <div className="text-center mt-auto">
                    <p 
                      className="font-league-spartan text-[#00278C] mb-1"
                      style={{
                        fontWeight: 500,
                        fontSize: '27.78px',
                        lineHeight: '92%'
                      }}
                    >
                      46점
                    </p>

                    {/* 상태 메시지 */}
                    <p 
                      className="font-league-spartan text-[#00278C]"
                      style={{
                        fontWeight: 500,
                        fontSize: '13.89px',
                        lineHeight: '92%'
                      }}
                    >
                      보행 안정성 낮은 상태
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* 두 번째 행 */}
            <div className="flex gap-3">
              {/* 에어백 상태 버튼 */}
              <div 
                className="cursor-pointer bg-white border-2 border-[#3D6DEA] rounded-3xl shadow-lg p-4 flex-1"
                style={{
                  height: '155.11px'
                }}
              >
                <div className="flex flex-col h-full">
                  {/* 제목 */}
                  <p 
                    className="font-league-spartan text-[#00278C] mb-3"
                    style={{
                      fontWeight: 700,
                      fontSize: '20.835px',
                      lineHeight: '92%',
                      textAlign: 'left'
                    }}
                  >
                    에어백 상태
                  </p>

                  {/* 아이콘 */}
                  <div 
                    className="flex items-center justify-center mb-4"
                    style={{
                      width: '55px',
                      height: '50px',
                      margin: '0 auto'
                    }}
                  >
                    <img 
                      src="/에어백 상태_f.png" 
                      alt="에어백 상태"
                      className="w-full h-full object-contain"
                    />
                  </div>

                  {/* 수치 */}
                  <div className="text-center mt-auto">
                    <p 
                      className="font-league-spartan text-[#00278C] mb-1"
                      style={{
                        fontWeight: 500,
                        fontSize: '27.78px',
                        lineHeight: '92%'
                      }}
                    >
                      100%
                    </p>

                    {/* 상태 메시지 */}
                    <p 
                      className="font-league-spartan text-[#00278C]"
                      style={{
                        fontWeight: 500,
                        fontSize: '13.89px',
                        lineHeight: '92%'
                      }}
                    >
                      펌웨어 매우 안정적
                    </p>
                  </div>
                </div>
              </div>

              {/* 보행기록 버튼 */}
              <div 
                className="cursor-pointer bg-white border-2 border-[#3D6DEA] rounded-3xl shadow-lg p-4 flex-1"
                style={{
                  height: '155.11px'
                }}
              >
                <div className="flex flex-col h-full">
                  {/* 제목 */}
                  <p 
                    className="font-league-spartan text-[#00278C] mb-3"
                    style={{
                      fontWeight: 700,
                      fontSize: '20.835px',
                      lineHeight: '92%',
                      textAlign: 'left'
                    }}
                  >
                    보행 기록
                  </p>

                  {/* 아이콘 */}
                  <div 
                    className="flex items-center justify-center mb-4"
                    style={{
                      width: '47.56px',
                      height: '41.67px',
                      margin: '0 auto'
                    }}
                  >
                    <img 
                      src="/지도.png" 
                      alt="보행 기록"
                      className="w-full h-full object-contain"
                    />
                  </div>

                  {/* 수치 */}
                  <div className="text-center mt-auto">
                    <p 
                      className="font-pretendard text-[#00278C] mb-1"
                      style={{
                        fontWeight: 600,
                        fontSize: '20px',
                        lineHeight: '92%'
                      }}
                    >
                      위치 찾기
                    </p>

                    {/* 상태 메시지 */}
                    <p 
                      className="font-league-spartan text-[#00278C]"
                      style={{
                        fontWeight: 500,
                        fontSize: '13.89px',
                        lineHeight: '92%'
                      }}
                    >
                      정상 위치 확인됨
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 긴급연락 버튼 */}
          <div className="px-8 pb-8">
            <div 
              onClick={handleEmergencyCall}
              className="cursor-pointer bg-[#FB5959] rounded-2xl p-4 flex items-center justify-between hover:bg-[#e54545] transition-colors"
            >
              <p 
                className="font-league-spartan text-white"
                style={{
                  fontWeight: 600,
                  fontSize: 'clamp(1rem, 4vw, 1.4rem)',
                  lineHeight: '100%'
                }}
              >
                긴급 연락
              </p>

              {/* 전화 아이콘 */}
              <div 
                className="border-2 border-white rounded p-1 flex items-center justify-center"
                style={{
                  width: '32px',
                  height: '32px'
                }}
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-white">
                  <path d="M6.62,10.79C8.06,13.62 10.38,15.94 13.21,17.38L15.41,15.18C15.69,14.9 16.08,14.82 16.43,14.93C17.55,15.3 18.75,15.5 20,15.5A1,1 0 0,1 21,16.5V20A1,1 0 0,1 20,21A17,17 0 0,1 3,4A1,1 0 0,1 4,3H7.5A1,1 0 0,1 8.5,4C8.5,5.25 8.7,6.45 9.07,7.57C9.18,7.92 9.1,8.31 8.82,8.59L6.62,10.79Z"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MainPage