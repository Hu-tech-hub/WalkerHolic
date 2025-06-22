/**
 * 낙상 감지 시스템 디버깅 컴포넌트
 * 연결 상태 모니터링 및 테스트 기능 제공
 * 
 * @file src/components/common/FallAlertDebug.jsx
 * @description 낙상 감지 시스템의 디버깅 및 테스트를 위한 컴포넌트
 * @version 1.0.0
 * @created 2025-01-15
 */

import React, { useState } from 'react'
import { supabase } from '../../services/supabaseClient'
import { toast } from 'react-hot-toast'

const FallAlertDebug = ({ connectionStatus, isSubscriptionActive, reconnectAttempts, maxReconnectAttempts }) => {
  const [isVisible, setIsVisible] = useState(false)

  // 테스트 낙상 데이터 삽입
  const handleTestFallDetection = async () => {
    try {
      console.log('🧪 테스트 낙상 데이터를 삽입합니다...')
      
      const now = new Date()
      const testData = {
        timestamp: now.toISOString(),
        detected_at: now.toISOString(),
        unix_timestamp: Math.floor(now.getTime() / 1000)
      }

      const { data, error } = await supabase
        .from('fall_history')
        .insert([testData])
        .select()

      if (error) {
        console.error('❌ 테스트 데이터 삽입 실패:', error)
        toast.error(`테스트 실패: ${error.message}`)
      } else {
        console.log('✅ 테스트 데이터 삽입 성공:', data)
        toast.success('테스트 낙상 데이터가 삽입되었습니다!')
      }
    } catch (error) {
      console.error('❌ 테스트 중 오류 발생:', error)
      toast.error(`테스트 오류: ${error.message}`)
    }
  }

  // Supabase 연결 테스트
  const handleConnectionTest = async () => {
    try {
      console.log('🔍 Supabase 연결을 테스트합니다...')
      
      const { data, error } = await supabase
        .from('fall_history')
        .select('count')
        .limit(1)

      if (error) {
        console.error('❌ 연결 테스트 실패:', error)
        toast.error(`연결 실패: ${error.message}`)
      } else {
        console.log('✅ Supabase 연결 성공')
        toast.success('Supabase 연결이 정상입니다!')
      }
    } catch (error) {
      console.error('❌ 연결 테스트 중 오류:', error)
      toast.error(`연결 오류: ${error.message}`)
    }
  }

  // 환경변수 확인
  const checkEnvironmentVariables = () => {
    const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
    const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

    console.log('🔧 환경변수 확인:')
    console.log('VITE_SUPABASE_URL:', supabaseUrl)
    console.log('VITE_SUPABASE_ANON_KEY:', supabaseAnonKey ? '설정됨' : '설정되지 않음')

    if (!supabaseUrl || !supabaseAnonKey) {
      toast.error('환경변수가 설정되지 않았습니다!')
    } else {
      toast.success('환경변수가 정상적으로 설정되었습니다!')
    }
  }

  // 수동 재연결 시도
  const handleManualReconnect = () => {
    console.log('🔄 수동 재연결을 시도합니다...')
    toast('수동 재연결을 시도합니다...', {
      duration: 2000,
      icon: '🔄'
    })
    
    // 페이지 새로고침을 통한 완전한 재연결
    window.location.reload()
  }

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-4 bg-blue-500 text-white px-3 py-2 rounded-lg text-sm z-50 hover:bg-blue-600"
      >
        🐛 디버그
      </button>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 max-w-md w-full max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold">낙상 감지 시스템 디버그</h3>
          <button
            onClick={() => setIsVisible(false)}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        {/* 연결 상태 */}
        <div className="mb-4 p-3 bg-gray-100 rounded">
          <h4 className="font-semibold mb-2">연결 상태</h4>
          <p className="text-sm">
            <span className="font-medium">구독 상태:</span> {connectionStatus}
          </p>
          <p className="text-sm">
            <span className="font-medium">구독 활성:</span> {isSubscriptionActive ? '활성' : '비활성'}
          </p>
          {reconnectAttempts !== undefined && (
            <p className="text-sm">
              <span className="font-medium">재연결 시도:</span> {reconnectAttempts}/{maxReconnectAttempts || 5}
            </p>
          )}
        </div>

        {/* 테스트 정보 */}
        <div className="mb-4 p-3 bg-gray-100 rounded">
          <h4 className="font-semibold mb-2">테스트 데이터 구조</h4>
          <div className="text-xs text-gray-600 space-y-1">
            <p>• timestamp: 낙상 발생 시각</p>
            <p>• detected_at: 감지 시각</p>
            <p>• unix_timestamp: Unix 타임스탬프</p>
          </div>
        </div>

        {/* 버튼들 */}
        <div className="space-y-2">
          <button
            onClick={checkEnvironmentVariables}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
          >
            🔧 환경변수 확인
          </button>

          <button
            onClick={handleConnectionTest}
            className="w-full bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600"
          >
            🔍 연결 테스트
          </button>

          <button
            onClick={handleManualReconnect}
            className="w-full bg-orange-500 text-white py-2 px-4 rounded hover:bg-orange-600"
          >
            🔄 수동 재연결
          </button>

          <button
            onClick={handleTestFallDetection}
            className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600"
          >
            🧪 테스트 낙상 발생
          </button>
        </div>

        {/* 안내 메시지 */}
        <div className="mt-4 p-3 bg-yellow-100 rounded text-sm">
          <p className="font-medium text-yellow-800 mb-1">테스트 방법:</p>
          <ol className="text-yellow-700 text-xs space-y-1 list-decimal list-inside">
            <li>환경변수 확인 → 정상인지 확인</li>
            <li>연결 테스트 → Supabase 접근 가능한지 확인</li>
            <li>테스트 낙상 발생 → 실제 알림이 뜨는지 확인</li>
          </ol>
        </div>

        {/* 개발자 도구 안내 */}
        <div className="mt-4 p-3 bg-blue-100 rounded text-sm">
          <p className="font-medium text-blue-800 mb-1">디버깅 팁:</p>
          <p className="text-blue-700 text-xs">
            브라우저 개발자 도구(F12) → 콘솔 탭에서 자세한 로그를 확인하세요.
          </p>
        </div>
      </div>
    </div>
  )
}

export default FallAlertDebug 