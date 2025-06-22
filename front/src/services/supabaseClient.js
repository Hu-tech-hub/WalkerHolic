/**
 * Supabase 클라이언트 설정
 * 낙상 감지 실시간 알림 기능에 사용됩니다.
 * 
 * @file src/services/supabaseClient.js
 * @description Supabase 클라이언트 초기화 및 설정
 * @version 1.0.0
 * @created 2025-01-15
 */

import { createClient } from '@supabase/supabase-js'

// 환경변수에서 Supabase 설정 가져오기
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// 환경변수 검증
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ Supabase 환경변수가 설정되지 않았습니다!')
  console.error('VITE_SUPABASE_URL:', supabaseUrl)
  console.error('VITE_SUPABASE_ANON_KEY:', supabaseAnonKey ? '설정됨' : '설정되지 않음')
} else {
  console.log('✅ Supabase 환경변수가 정상적으로 설정되었습니다.')
  console.log('🔗 Supabase URL:', supabaseUrl)
}

// Supabase 클라이언트 생성
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  realtime: {
    params: {
      eventsPerSecond: 5, // 더 보수적으로 설정
    },
    // 연결 안정성을 위한 추가 설정
    heartbeatIntervalMs: 30000, // 30초마다 하트비트
    reconnectDelayMs: 2000,     // 재연결 지연 시간 2초
    timeout: 15000,             // 타임아웃 15초로 증가
  },
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
  db: {
    schema: 'public'
  }
})

export default supabase 