import React, { useState, useRef, useEffect } from 'react'
import ChatbotImage from '../assets/images/Chabot-image-2D.png'

const CognitiveTestPage = ({ onBackClick }) => {
  const [currentStep, setCurrentStep] = useState(0) // 0: 단일과제 시작, 1: 단일과제 진행, 2: 이중과제 시작, 3: 이중과제 진행, 4: 결과
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)
  const [videoVolume, setVideoVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [singleTaskStartTime, setSingleTaskStartTime] = useState(null)
  const [dualTaskStartTime, setDualTaskStartTime] = useState(null)
  const [singleTaskDuration, setSingleTaskDuration] = useState(0)
  const [dualTaskDuration, setDualTaskDuration] = useState(0)
  const [randomMessage, setRandomMessage] = useState('')
  const videoRef = useRef(null)

  // 챗봇 메시지 배열
  const chatbotMessages = [
    '조금만 더! 멋지게 걷는 모습 최고예요!',
    '지금 속도 최고예요! 계속 이렇게만 걸어볼까요?',
    '혼자가 아니에요~ 워키가 함께 걷고 있어요 😊'
  ]

  // 단일과제 시작 시 랜덤 메시지 선택
  useEffect(() => {
    if (currentStep === 1) {
      const randomIndex = Math.floor(Math.random() * chatbotMessages.length)
      setRandomMessage(chatbotMessages[randomIndex])
    }
    if (currentStep === 3) {
      const randomIndex = Math.floor(Math.random() * chatbotMessages.length)
      setRandomMessage(chatbotMessages[randomIndex])
    }
  }, [currentStep])

  const startSingleTask = () => {
    setSingleTaskStartTime(Date.now())
    setCurrentStep(1)
  }

  const completeSingleTask = () => {
    if (singleTaskStartTime) {
      const duration = (Date.now() - singleTaskStartTime) / 1000 // 초 단위
      setSingleTaskDuration(duration)
    }
    setCurrentStep(2)
  }

  const startDualTask = () => {
    setDualTaskStartTime(Date.now())
    setCurrentStep(3)
  }

  const completeDualTask = () => {
    if (dualTaskStartTime) {
      const duration = (Date.now() - dualTaskStartTime) / 1000 // 초 단위
      setDualTaskDuration(duration)
    }
    setCurrentStep(4)
  }

  // 비디오 컨트롤 함수들
  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isVideoPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsVideoPlaying(!isVideoPlaying)
    }
  }

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value)
    setVideoVolume(newVolume)
    if (videoRef.current) {
      videoRef.current.volume = newVolume
    }
    setIsMuted(newVolume === 0)
  }

  const toggleMute = () => {
    if (videoRef.current) {
      const newMutedState = !isMuted
      setIsMuted(newMutedState)
      if (newMutedState) {
        videoRef.current.volume = 0
        setVideoVolume(0)
      } else {
        videoRef.current.volume = 0.5
        setVideoVolume(0.5)
      }
    }
  }

  // 단일과제 테스트 화면
  const renderSingleTaskTest = () => (
    <div className="page-container w-full h-full flex flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-6 pt-6">
        <button 
          onClick={() => setCurrentStep(0)}
          className="flex items-center justify-center w-10 h-10 rounded-full border border-gray-300"
        >
          <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.42-1.41L7.83 13H20v-2z"/>
          </svg>
        </button>
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-blue-600 text-sm font-semibold">2D</span>
          </div>
        </div>
      </div>

      {/* Progress Status */}
      <div className="px-6 mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-sm font-medium text-gray-700">단일과제 진행 중</span>
        </div>
      </div>

      {/* Current Step */}
      <div className="px-6 mb-6">
        <p className="text-lg font-semibold text-gray-800">
          1단계 : 의자에서 일어나기<br/>
          2단계 : 의자에서 일어나서 3m 걷기<br/>
          3단계 : 돌아와서 의자에 앉기<br/>
          4단계 : 완료하기 버튼 누르기<br/>
        </p>
      </div>

      {/* Chatbot Section */}
      <div className="flex-1 px-6 flex flex-col justify-center">
        {/* Chatbot Image */}
        <div className="flex justify-center mb-4">
          <img 
            src={ChatbotImage} 
            alt="Chatbot" 
            className="w-112 h-56 object-contain wiggle-animation"
          />
        </div>
        <div className="bg-blue-50 rounded-2xl p-6 mb-6">
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <p className="text-gray-800 text-center font-bold">
              {randomMessage}
            </p>
          </div>
        </div>
      </div>

      {/* Complete Button */}
      <div className="p-6">
        <button
          onClick={completeSingleTask}
          className="w-full bg-blue-600 text-white py-4 rounded-2xl font-semibold text-lg"
        >
          완료 하기
        </button>
      </div>
    </div>
  )

  // 이중과제 테스트 화면
  const renderDualTaskTest = () => (
    <div className="page-container w-full h-full flex flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-6 pt-6">
        <button 
          onClick={() => setCurrentStep(2)}
          className="flex items-center justify-center w-10 h-10 rounded-full border border-gray-300"
        >
          <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.42-1.41L7.83 13H20v-2z"/>
          </svg>
        </button>
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-blue-600 text-sm font-semibold">2D</span>
          </div>
        </div>
      </div>

      {/* Progress Status */}
      <div className="px-6 mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
          <span className="text-sm font-medium text-gray-700">이중과제 진행 중</span>
        </div>
      </div>

      {/* Current Step */}
      <div className="px-6 mb-6">
        <p className="text-lg font-semibold text-gray-800">
          1단계 : 의자에서 일어나기<br/>
          2단계 : 의자에서 일어나서 3m 걷기<br/>
          3단계 : 돌아와서 의자에 앉기<br/>
          4단계 : 완료하기 버튼 누르기<br/>
        </p>
        <p className="text-lg font-bold mt-3" style={{color: '#f2663f'}}>
          워키의 질문에 대답하며 걸어주세요!
        </p>
      </div>

      {/* Chatbot Section */}
      <div className="flex-1 px-6 flex flex-col justify-center">
        {/* Chatbot Image */}
        <div className="flex justify-center mb-4">
          <img 
            src={ChatbotImage} 
            alt="Chatbot" 
            className="w-112 h-56 object-contain wiggle-animation"
          />
        </div>
        <div className="bg-blue-50 rounded-2xl p-6 mb-6">
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <p className="text-gray-800 text-center font-bold">
              {randomMessage}
            </p>
          </div>
        </div>
      </div>

      {/* Complete Button */}
      <div className="p-6">
        <button
          onClick={completeDualTask}
          className="w-full bg-blue-600 text-white py-4 rounded-2xl font-semibold text-lg"
        >
          완료 하기
        </button>
      </div>
    </div>
  )

  // 테스트 결과 화면
  const renderTestResults = () => (
    <div className="page-container w-full h-full flex flex-col bg-white overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between p-6 pt-6">
        <button 
          onClick={() => setCurrentStep(3)}
          className="flex items-center justify-center w-10 h-10 rounded-full border border-gray-300"
        >
          <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.42-1.41L7.83 13H20v-2z"/>
          </svg>
        </button>
        <h1 className="text-lg font-semibold">인지 기능 테스트 결과</h1>
        <div className="w-10"></div>
      </div>

      {/* Score Section */}
      <div className="px-6 mb-8">
        <div className="bg-blue-50 rounded-2xl p-6 text-center">
          <div className="text-6xl font-bold text-blue-600 mb-2">84</div>
          <div className="text-blue-800 font-medium">점</div>
          <div className="text-green-600 font-semibold mt-2">
            인지 기능 전반이 안정적
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="px-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">상세 통계</h3>
        
        <div className="space-y-4">
          {(() => {
            // 개별 시간 계산
            const singleSeconds = Math.round(singleTaskDuration)
            const dualSeconds = Math.round(dualTaskDuration)
            
            // 총 소요 시간 계산
            const totalSeconds = singleSeconds + dualSeconds
            const totalMinutes = Math.floor(totalSeconds / 60)
            const totalRemainingSeconds = totalSeconds % 60
            
            // 이중과제 시간 계산
            const dualMinutes = Math.floor(dualSeconds / 60)
            const dualRemainingSeconds = dualSeconds % 60
            
            // 단일과제 시간 계산
            const singleMinutes = Math.floor(singleSeconds / 60)
            const singleRemainingSeconds = singleSeconds % 60
            
            // 시간 차이 계산
            const timeDiff = dualSeconds - singleSeconds
            
            return (
              <>
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">총 소요 시간</span>
                  <span className="font-semibold">
                    {`${totalMinutes.toString().padStart(2, '0')}:${totalRemainingSeconds.toString().padStart(2, '0')}`}
                  </span>
                </div>
                
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">이중 과제 시간</span>
                  <span className="font-semibold">
                    {`${dualMinutes.toString().padStart(2, '0')}:${dualRemainingSeconds.toString().padStart(2, '0')}`}
                  </span>
                </div>
                
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">단일 과제 시간</span>
                  <span className="font-semibold">
                    {`${singleMinutes.toString().padStart(2, '0')}:${singleRemainingSeconds.toString().padStart(2, '0')}`}
                  </span>
                </div>
                
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">이중-단일과제 시간 차이</span>
                  <span className="font-semibold">
                    {timeDiff <= 0 ? '정상' : `${timeDiff}초`}
                  </span>
                </div>
                
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">정답 개수</span>
                  <span className="font-semibold">34개</span>
                </div>
              </>
            )
          })()}
        </div>
      </div>

      {/* Cognitive Assessment Categories */}
      <div className="px-6 mb-8">
        <h3 className="text-lg font-semibold mb-4">인지 기능 평가</h3>
        
        <div className="space-y-4">
          <div className="bg-gray-50 rounded-xl p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">주의 배분 능력</span>
              <span className="font-bold text-blue-600">92/100</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{width: '92%'}}></div>
            </div>
          </div>

          <div className="bg-gray-50 rounded-xl p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">작업 기억 능력</span>
              <span className="font-bold text-orange-600">73/100</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-orange-600 h-2 rounded-full" style={{width: '73%'}}></div>
            </div>
          </div>

          <div className="bg-gray-50 rounded-xl p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">행동 조정 능력</span>
              <span className="font-bold text-red-600">52/100</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-red-600 h-2 rounded-full" style={{width: '52%'}}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Back to Main Button */}
      <div className="p-6">
        <button
          onClick={onBackClick}
          className="w-full bg-blue-600 text-white py-4 rounded-2xl font-semibold text-lg"
        >
          메인으로 돌아가기
        </button>
      </div>
    </div>
  )

  // 이중과제 시작 화면
  const renderDualTaskStartScreen = () => (
    <div className="page-container w-full h-full flex flex-col bg-white overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between p-6 pt-6">
        <button 
          onClick={() => setCurrentStep(1)}
          className="flex items-center justify-center w-10 h-10 rounded-full border border-gray-300"
        >
          <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.42-1.41L7.83 13H20v-2z"/>
          </svg>
        </button>
        <div className="w-10"></div>
      </div>

      {/* Title */}
      <div className="px-8 mb-6">
        <h1 className="text-[30px] font-bold text-[#181E4B] leading-[1.29]" style={{fontFamily: 'Volkhov'}}>
          인지기능 검사(이중과제)
        </h1>
      </div>

      {/* Video Section */}
      <div className="px-5 mb-0">
        <div className="relative bg-gray-200 rounded-t-[21px] h-[193px] overflow-hidden">
          {/* 실제 비디오가 있을 때 사용할 비디오 엘리먼트 */}
          <video
            ref={videoRef}
            className="w-full h-full object-cover hidden" // 비디오 파일이 없으므로 hidden
            onPlay={() => setIsVideoPlaying(true)}
            onPause={() => setIsVideoPlaying(false)}
          >
            {/* 비디오 소스가 추가되면 여기에 <source> 태그 추가 */}
          </video>
          
          {/* 임시 플레이스홀더 */}
          <div className="w-full h-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-white bg-opacity-80 rounded-full flex items-center justify-center mb-3 mx-auto">
                <svg viewBox="0 0 24 24" className="w-8 h-8 text-blue-600" fill="currentColor">
                  <path d="M8,5.14V19.14L19,12.14L8,5.14Z"/>
                </svg>
              </div>
              <p className="text-blue-800 font-medium">동작 영상</p>
            </div>
          </div>

          {/* 비디오 컨트롤 (향후 비디오 추가 시 사용) */}
          <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 p-3 hidden">
            <div className="flex items-center space-x-3">
              <button
                onClick={togglePlayPause}
                className="text-white hover:text-blue-300 transition-colors"
              >
                {isVideoPlaying ? (
                  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
                    <path d="M14,19H18V5H14M6,19H10V5H6V19Z"/>
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
                    <path d="M8,5.14V19.14L19,12.14L8,5.14Z"/>
                  </svg>
                )}
              </button>
              
              <button
                onClick={toggleMute}
                className="text-white hover:text-blue-300 transition-colors"
              >
                {isMuted ? (
                  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
                    <path d="M12,4L9.91,6.09L12,8.18M4.27,3L3,4.27L7.73,9H3V15H7L12,20V13.27L16.25,17.52C15.58,18.04 14.83,18.46 14,18.7V20.77C15.38,20.45 16.63,19.82 17.68,18.96L19.73,21L21,19.73L12,10.73M19,12C19,12.94 18.8,13.82 18.46,14.64L19.97,16.15C20.62,14.91 21,13.5 21,12C21,7.72 18,4.14 14,3.23V5.29C16.89,6.15 19,8.83 19,12M16.5,12C16.5,10.23 15.5,8.71 14,7.97V10.18L16.45,12.63C16.5,12.43 16.5,12.21 16.5,12Z"/>
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
                    <path d="M14,3.23V5.29C16.89,6.15 19,8.83 19,12C19,15.17 16.89,17.85 14,18.71V20.77C18,19.86 21,16.28 21,12C21,7.72 18,4.14 14,3.23M16.5,12C16.5,10.23 15.5,8.71 14,7.97V16.03C15.5,15.29 16.5,13.77 16.5,12M3,9V15H7L12,20V4L7,9H3Z"/>
                  </svg>
                )}
              </button>
              
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={videoVolume}
                onChange={handleVolumeChange}
                className="flex-1 h-1 bg-gray-300 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Video Description */}
        <div className="bg-[#00278C] h-[52px] flex items-center justify-center rounded-b-none">
          <p className="text-white font-medium text-[19px] leading-[1.5]" style={{fontFamily: 'Poppins'}}>
            먼저 영상을 보며 동작을 익혀주세요!
          </p>
        </div>
      </div>

      {/* Time and Materials Info */}
      <div className="px-5 pt-7 pb-4">
        <div className="space-y-1">
          <p className="text-[#181E4B] text-[17.3px] leading-[1.75]" style={{fontFamily: 'Poppins'}}>
            <span className="font-bold">소요 시간 :</span> 2분 내외
          </p>
          <p className="text-[#181E4B] text-[17.3px] leading-[1.75]" style={{fontFamily: 'Poppins'}}>
            <span className="font-bold">준비물 :</span> 의자 1개, 3m 걷기 공간
          </p>
        </div>
      </div>

      {/* Instructions */}
      <div className="px-5 pb-6">
        <div className="space-y-3">
          <h3 className="text-[#181E4B] font-bold text-[17.3px] leading-[1.5]" style={{fontFamily: 'Poppins'}}>
            순서
          </h3>
          <div className="space-y-2 text-[#181E4B] text-[17.3px] leading-[1.5]" style={{fontFamily: 'Poppins'}}>
            <p>• 반드시 <span className="font-bold" style={{color: '#f2663f'}}>보호자</span>와 함께 진행해주세요.</p>
            <p>• 의자에 앉아 일어날 준비를 해주세요.</p>
            <p>• 준비가 되셨다면, <span className="font-bold" style={{color: '#f2663f'}}>시작하기</span>를 눌러주세요.</p>
            <p>• 의자에서 일어나서 3m를 걷고, <span className="font-bold" style={{color: '#f2663f'}}>다시 돌아오신 후</span>, 자리에 다시 앉고, <span className="font-bold" style={{color: '#f2663f'}}>완료하기</span> 버튼을 눌러주세요.</p>
            <p>• <span className="font-bold" style={{color: '#f2663f'}}>챗봇의 질문에 대해 대답하면서 걸어주세요.</span></p>
          </div>
        </div>
      </div>

      {/* Start Button */}
      <div className="px-5 pb-6">
        <button
          onClick={startDualTask}
          className="w-full bg-[#BACAF5] text-[#0C2C80] py-[18px] rounded-2xl font-semibold text-[20px] leading-[1.4] shadow-lg"
          style={{fontFamily: 'Pretendard'}}
        >
          시작하기
        </button>
      </div>
    </div>
  )

  // 단일과제 시작 화면
  const renderStartScreen = () => (
    <div className="page-container w-full h-full flex flex-col bg-white overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between p-6 pt-6">
        <button 
          onClick={onBackClick}
          className="flex items-center justify-center w-10 h-10 rounded-full border border-gray-300"
        >
          <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.42-1.41L7.83 13H20v-2z"/>
          </svg>
        </button>
        <div className="w-10"></div>
      </div>

      {/* Title */}
      <div className="px-8 mb-6">
        <h1 className="text-[30px] font-bold text-[#181E4B] leading-[1.29]" style={{fontFamily: 'Volkhov'}}>
          인지기능 검사(단일과제)
        </h1>
      </div>

      {/* Video Section */}
      <div className="px-5 mb-0">
        <div className="relative bg-gray-200 rounded-t-[21px] h-[193px] overflow-hidden">
          {/* 실제 비디오가 있을 때 사용할 비디오 엘리먼트 */}
          <video
            ref={videoRef}
            className="w-full h-full object-cover hidden" // 비디오 파일이 없으므로 hidden
            onPlay={() => setIsVideoPlaying(true)}
            onPause={() => setIsVideoPlaying(false)}
          >
            {/* 비디오 소스가 추가되면 여기에 <source> 태그 추가 */}
          </video>
          
          {/* 임시 플레이스홀더 */}
          <div className="w-full h-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-white bg-opacity-80 rounded-full flex items-center justify-center mb-3 mx-auto">
                <svg viewBox="0 0 24 24" className="w-8 h-8 text-blue-600" fill="currentColor">
                  <path d="M8,5.14V19.14L19,12.14L8,5.14Z"/>
                </svg>
              </div>
              <p className="text-blue-800 font-medium">동작 영상</p>
            </div>
          </div>

          {/* 비디오 컨트롤 (향후 비디오 추가 시 사용) */}
          <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 p-3 hidden">
            <div className="flex items-center space-x-3">
              <button
                onClick={togglePlayPause}
                className="text-white hover:text-blue-300 transition-colors"
              >
                {isVideoPlaying ? (
                  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
                    <path d="M14,19H18V5H14M6,19H10V5H6V19Z"/>
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
                    <path d="M8,5.14V19.14L19,12.14L8,5.14Z"/>
                  </svg>
                )}
              </button>
              
              <button
                onClick={toggleMute}
                className="text-white hover:text-blue-300 transition-colors"
              >
                {isMuted ? (
                  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
                    <path d="M12,4L9.91,6.09L12,8.18M4.27,3L3,4.27L7.73,9H3V15H7L12,20V13.27L16.25,17.52C15.58,18.04 14.83,18.46 14,18.7V20.77C15.38,20.45 16.63,19.82 17.68,18.96L19.73,21L21,19.73L12,10.73M19,12C19,12.94 18.8,13.82 18.46,14.64L19.97,16.15C20.62,14.91 21,13.5 21,12C21,7.72 18,4.14 14,3.23V5.29C16.89,6.15 19,8.83 19,12M16.5,12C16.5,10.23 15.5,8.71 14,7.97V10.18L16.45,12.63C16.5,12.43 16.5,12.21 16.5,12Z"/>
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
                    <path d="M14,3.23V5.29C16.89,6.15 19,8.83 19,12C19,15.17 16.89,17.85 14,18.71V20.77C18,19.86 21,16.28 21,12C21,7.72 18,4.14 14,3.23M16.5,12C16.5,10.23 15.5,8.71 14,7.97V16.03C15.5,15.29 16.5,13.77 16.5,12M3,9V15H7L12,20V4L7,9H3Z"/>
                  </svg>
                )}
              </button>
              
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={videoVolume}
                onChange={handleVolumeChange}
                className="flex-1 h-1 bg-gray-300 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Video Description */}
        <div className="bg-[#00278C] h-[52px] flex items-center justify-center rounded-b-none">
          <p className="text-white font-medium text-[19px] leading-[1.5]" style={{fontFamily: 'Poppins'}}>
            먼저 영상을 보며 동작을 익혀주세요!
          </p>
        </div>
      </div>

      {/* Time and Materials Info */}
      <div className="px-5 pt-7 pb-4">
        <div className="space-y-1">
          <p className="text-[#181E4B] text-[17.3px] leading-[1.75]" style={{fontFamily: 'Poppins'}}>
            <span className="font-bold">소요 시간 :</span> 2분 내외
          </p>
          <p className="text-[#181E4B] text-[17.3px] leading-[1.75]" style={{fontFamily: 'Poppins'}}>
            <span className="font-bold">준비물 :</span> 의자 1개, 3m 걷기 공간
          </p>
        </div>
      </div>

      {/* Instructions */}
      <div className="px-5 pb-6">
        <div className="space-y-3">
          <h3 className="text-[#181E4B] font-bold text-[17.3px] leading-[1.5]" style={{fontFamily: 'Poppins'}}>
            순서
          </h3>
          <div className="space-y-2 text-[#181E4B] text-[17.3px] leading-[1.5]" style={{fontFamily: 'Poppins'}}>
            <p>• 반드시 <span className="font-bold" style={{color: '#f2663f'}}>보호자</span>와 함께 진행해주세요.</p>
            <p>• 의자에 앉아 일어날 준비를 해주세요.</p>
            <p>• 준비가 되셨다면, <span className="font-bold" style={{color: '#f2663f'}}>시작하기</span>를 눌러주세요.</p>
            <p>• 의자에서 일어나서 3m를 걷고, <span className="font-bold" style={{color: '#f2663f'}}>다시 돌아오신 후</span>, 자리에 다시 앉고, <span className="font-bold" style={{color: '#f2663f'}}>완료하기</span> 버튼을 눌러주세요.</p>
          </div>
        </div>
      </div>

      {/* Start Button */}
      <div className="px-5 pb-6">
        <button
          onClick={startSingleTask}
          className="w-full bg-[#BACAF5] text-[#0C2C80] py-[18px] rounded-2xl font-semibold text-[20px] leading-[1.4] shadow-lg"
          style={{fontFamily: 'Pretendard'}}
        >
          시작하기
        </button>
      </div>
    </div>
  )

  // 메인 렌더링 로직
  return (
    <>
             <style jsx>{`
         @keyframes wiggle {
           0% { 
             transform: translateX(-10px) rotate(-2deg); 
           }
           50% { 
             transform: translateX(10px) rotate(2deg); 
           }
           100% { 
             transform: translateX(-10px) rotate(-2deg); 
           }
         }
         .wiggle-animation {
           animation: wiggle 2.4s ease-in-out infinite;
         }
       `}</style>
      {(() => {
        switch (currentStep) {
          case 0:
            return renderStartScreen() // 단일과제 시작
          case 1:
            return renderSingleTaskTest() // 단일과제 진행
          case 2:
            return renderDualTaskStartScreen() // 이중과제 시작
          case 3:
            return renderDualTaskTest() // 이중과제 진행
          case 4:
            return renderTestResults() // 결과
          default:
            return renderStartScreen()
        }
      })()}
    </>
  )
}

export default CognitiveTestPage 