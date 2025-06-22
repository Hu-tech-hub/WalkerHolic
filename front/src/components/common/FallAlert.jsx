/**
 * 낙상 감지 알림 컴포넌트
 * 낙상이 감지되었을 때 화면에 표시되는 경고 모달
 * 
 * @file src/components/common/FallAlert.jsx
 * @description 낙상 감지 시 표시되는 경고 알림 모달
 * @version 1.0.0
 * @created 2025-01-15
 */

import React, { useState, useEffect } from 'react'

const FallAlert = ({ isVisible, onCancel, onEmergencyCall, guardianPhone }) => {
  const [countdown, setCountdown] = useState(10)
  const [isCallInProgress, setIsCallInProgress] = useState(false)

  useEffect(() => {
    if (!isVisible) {
      setCountdown(10)
      setIsCallInProgress(false)
      return
    }

    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          // 카운트다운 종료 시 자동으로 긴급전화
          handleEmergencyCall()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [isVisible])

  const handleEmergencyCall = () => {
    setIsCallInProgress(true)
    if (onEmergencyCall) {
      onEmergencyCall(guardianPhone)
    }
  }

  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    }
  }

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* 배경 블러 */}
      <div className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm" />
      
      {/* 알림 모달 */}
      <div className="relative bg-red-500 rounded-3xl p-8 mx-4 max-w-sm w-full border-4 border-red-600">
        <div className="flex flex-col items-center space-y-4">
          {/* 경고 아이콘과 제목 */}
          <div className="flex items-center space-x-2">
            <div className="w-12 h-10 flex items-center justify-center">
              {/* 경고 아이콘 (Figma 디자인 기반) */}
              <div className="relative">
                <div className="w-12 h-9 bg-yellow-400 rounded-full flex items-center justify-center">
                  <div className="w-1.5 h-6 bg-gray-800 rounded-full"></div>
                </div>
                <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 w-1.5 h-1.5 bg-gray-800 rounded-full"></div>
              </div>
            </div>
            <h2 className="text-white text-3xl font-bold text-center">
              낙상 감지
            </h2>
          </div>

          {/* 메시지 */}
          <p className="text-white text-center text-base font-medium leading-tight">
            낙상이 감지되었습니다.<br />
            자동으로 긴급번호로 연결합니다.
          </p>

          {/* 카운트다운과 버튼 */}
          <div className="flex flex-col items-center space-y-3 w-full">
            {/* 카운트다운 */}
            <div className="bg-black rounded-full px-4 py-2 min-w-[60px] flex items-center justify-center">
              <span className="text-white text-2xl font-bold">
                {countdown.toString().padStart(2, '0')}
              </span>
            </div>

            {/* 버튼 그룹 */}
            <div className="flex items-center space-x-3 w-full justify-center">
              {/* 긴급연락 버튼 */}
              <button
                onClick={handleEmergencyCall}
                disabled={isCallInProgress}
                className="bg-black border-2 border-black rounded-full px-4 py-2 min-h-[43px] flex items-center justify-center disabled:opacity-50"
              >
                <span className="text-white bg-red-600 px-3 py-1 rounded-full text-lg font-semibold">
                  긴급연락
                </span>
              </button>

              {/* 연결취소 버튼 */}
              <button
                onClick={handleCancel}
                disabled={isCallInProgress}
                className="bg-black border-2 border-black rounded-full px-4 py-2 min-h-[43px] flex items-center justify-center disabled:opacity-50"
              >
                <span className="text-black bg-white px-3 py-1 rounded-full text-lg font-semibold">
                  연결취소
                </span>
              </button>
            </div>
          </div>

          {isCallInProgress && (
            <p className="text-white text-sm text-center mt-2">
              {guardianPhone}로 연결 중...
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default FallAlert 