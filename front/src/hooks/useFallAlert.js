/**
 * 낙상 감지 실시간 알림 훅
 * Supabase realtime을 사용하여 fall_history 테이블의 INSERT 이벤트를 감지
 * 
 * @file src/hooks/useFallAlert.js
 * @description 낙상 감지 실시간 구독 및 알림 관리 훅
 * @version 1.0.0
 * @created 2025-01-15
 */

import { useEffect, useState, useRef } from 'react'
import { supabase } from '../services/supabaseClient'
import { toast } from 'react-hot-toast'

export default function useFallAlert() {
  const [isFallDetected, setIsFallDetected] = useState(false)
  const [isSubscriptionActive, setIsSubscriptionActive] = useState(true)
  const [connectionStatus, setConnectionStatus] = useState('연결 중...')
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const [maxReconnectAttempts] = useState(3)
  
  // 재연결 타이머와 채널 참조
  const reconnectTimeoutRef = useRef(null)
  const channelRef = useRef(null)
  const isReconnectingRef = useRef(false)

  useEffect(() => {
    if (!isSubscriptionActive) {
      console.log('💤 낙상 감지 구독이 비활성화되어 있습니다.')
      setConnectionStatus('구독 비활성화')
      return
    }

    // 이미 재연결 중이면 중복 실행 방지
    if (isReconnectingRef.current) {
      console.log('🔄 이미 재연결 중입니다. 중복 실행을 방지합니다.')
      return
    }

    console.log('🔔 낙상 감지 실시간 구독을 시작합니다.')
    setConnectionStatus('연결 중...')

    // Supabase 환경변수 확인
    const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
    const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY
    
    if (!supabaseUrl || !supabaseAnonKey) {
      console.error('❌ Supabase 환경변수가 설정되지 않았습니다!')
      setConnectionStatus('환경변수 오류')
      toast.error('Supabase 설정을 확인해주세요')
      return
    }

    // API Key 타입 확인 (보안 검사)
    if (supabaseAnonKey.includes('service_role')) {
      console.error('❌ 보안 경고: service_role key를 프론트엔드에서 사용하고 있습니다!')
      setConnectionStatus('보안 오류')
      toast.error('⚠️ 보안 오류: anon key를 사용해야 합니다!')
      return
    }

    // 기존 채널이 있으면 먼저 정리
    if (channelRef.current) {
      console.log('🧹 기존 채널을 정리합니다.')
      supabase.removeChannel(channelRef.current)
      channelRef.current = null
    }

    // Supabase realtime 채널 생성
    const channel = supabase
      .channel(`fall-alert-channel-${Date.now()}`, {
        config: {
          broadcast: { self: true },
          presence: { key: 'fallAlert' }
        }
      })
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'fall_history',
        },
        (payload) => {
          console.log('⚠️ 낙상 감지됨!', payload)
          console.log('📋 페이로드 상세:', JSON.stringify(payload, null, 2))
          
          // Toast 알림도 표시
          toast.error('낙상이 감지되었습니다!', {
            duration: 3000,
            icon: '⚠️'
          })
          
          // 알림 표시 상태로 변경
          setIsFallDetected(true)
          
          // 알림이 표시되는 동안 구독 일시 중지
          setIsSubscriptionActive(false)
        }
      )
      .subscribe((status, err) => {
        console.log('📡 Supabase 구독 상태:', status)
        if (err) {
          console.error('❌ 구독 에러:', err)
          setConnectionStatus(`에러: ${err.message}`)
          toast.error(`연결 에러: ${err.message}`)
        } else {
          setConnectionStatus(status)
          
          // 구독 상태에 따른 메시지
          if (status === 'SUBSCRIBED') {
            console.log('✅ fall_history 테이블 실시간 구독 성공!')
            setReconnectAttempts(0) // 성공 시 재연결 카운터 초기화
            isReconnectingRef.current = false // 재연결 플래그 해제
            
            // 기존 재연결 타이머 제거
            if (reconnectTimeoutRef.current) {
              clearTimeout(reconnectTimeoutRef.current)
              reconnectTimeoutRef.current = null
            }
            
            toast.success('낙상 감지 시스템이 활성화되었습니다', {
              duration: 2000,
              icon: '🔔'
            })
          } else if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT') {
            const errorType = status === 'CHANNEL_ERROR' ? '채널' : '타임아웃'
            console.error(`❌ ${errorType} 오류 발생!`)
            
            if (reconnectAttempts < maxReconnectAttempts && !isReconnectingRef.current) {
              isReconnectingRef.current = true
              const nextAttempt = reconnectAttempts + 1
              const delay = Math.min(5000 * nextAttempt, 30000) // 5초씩 증가, 최대 30초
              
              console.log(`🔄 ${errorType}으로 인한 ${nextAttempt}번째 재연결 시도... (${delay/1000}초 후)`)
              setConnectionStatus(`재연결 대기 중... (${nextAttempt}/${maxReconnectAttempts})`)
              
              toast.error(`${errorType} 오류 - ${delay/1000}초 후 재연결... (${nextAttempt}/${maxReconnectAttempts})`, {
                duration: 3000,
                icon: '🔄'
              })
              
              // 지연된 재연결
              reconnectTimeoutRef.current = setTimeout(() => {
                setReconnectAttempts(nextAttempt)
                setIsSubscriptionActive(false)
                setTimeout(() => {
                  setIsSubscriptionActive(true)
                }, 1000)
              }, delay)
            } else {
              console.error('❌ 최대 재연결 시도 횟수 초과 또는 이미 재연결 중')
              setConnectionStatus('연결 실패')
              isReconnectingRef.current = false
              toast.error('연결에 계속 실패합니다. 페이지를 새로고침해주세요.', {
                duration: 5000,
                icon: '❌'
              })
            }
          } else if (status === 'CLOSED') {
            console.log('🔌 연결이 종료되었습니다')
            
            // 정상적인 종료인지 확인 (구독이 활성화된 상태에서의 종료만 재연결)
            if (isSubscriptionActive && !isReconnectingRef.current && reconnectAttempts < maxReconnectAttempts) {
              isReconnectingRef.current = true
              const nextAttempt = reconnectAttempts + 1
              const delay = 3000 // CLOSED 상태에서는 3초 대기
              
              console.log(`🔄 연결 종료로 인한 ${nextAttempt}번째 재연결 시도... (${delay/1000}초 후)`)
              setConnectionStatus(`재연결 준비 중... (${nextAttempt}/${maxReconnectAttempts})`)
              
              reconnectTimeoutRef.current = setTimeout(() => {
                setReconnectAttempts(nextAttempt)
                setIsSubscriptionActive(false)
                setTimeout(() => setIsSubscriptionActive(true), 1000)
              }, delay)
            } else {
              setConnectionStatus('연결 종료')
              isReconnectingRef.current = false
            }
          }
        }
      })

    // 채널 참조 저장
    channelRef.current = channel
    
    // 디버깅용: 채널 정보 출력
    console.log('🔍 생성된 채널 정보:', channel)

    // 컴포넌트 언마운트 시 정리
    return () => {
      console.log('🔇 낙상 감지 구독을 해제합니다.')
      
      // 재연결 타이머 정리
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      
      // 재연결 플래그 해제
      isReconnectingRef.current = false
      
      setConnectionStatus('연결 해제됨')
      
      // 채널 정리
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current)
        channelRef.current = null
      }
    }
  }, [isSubscriptionActive, reconnectAttempts])

  // 알림 취소 핸들러
  const handleAlertCancel = () => {
    console.log('✅ 낙상 알림이 취소되었습니다.')
    setIsFallDetected(false)
    // 재연결 카운터 초기화
    setReconnectAttempts(0)
    isReconnectingRef.current = false
    // 약간의 지연 후 구독 재개 (중복 알림 방지)
    setTimeout(() => {
      setIsSubscriptionActive(true)
    }, 2000)
  }

  // 긴급전화 핸들러
  const handleEmergencyCall = (guardianPhone) => {
    console.log(`📞 긴급전화 연결: ${guardianPhone}`)
    
    try {
      // 전화 연결 시도 (브라우저의 tel: 프로토콜 사용)
      if (guardianPhone) {
        window.location.href = `tel:${guardianPhone}`
      } else {
        console.error('❌ 보호자 전화번호가 설정되지 않았습니다.')
        alert('보호자 전화번호가 설정되지 않았습니다.')
      }
    } catch (error) {
      console.error('❌ 전화 연결 실패:', error)
      alert('전화 연결에 실패했습니다.')
    }
    
    // 알림 종료
    setIsFallDetected(false)
    // 재연결 카운터 초기화
    setReconnectAttempts(0)
    isReconnectingRef.current = false
    setTimeout(() => {
      setIsSubscriptionActive(true)
    }, 2000)
  }

  return {
    isFallDetected,
    isSubscriptionActive,
    connectionStatus,
    reconnectAttempts,
    maxReconnectAttempts,
    onAlertCancel: handleAlertCancel,
    onEmergencyCall: handleEmergencyCall,
  }
} 