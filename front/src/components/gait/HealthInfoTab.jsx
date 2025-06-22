import React from 'react'
import GaitIndicatorAccordion from './GaitIndicatorAccordion'

const HealthInfoTab = ({ indicators }) => {
  // indicators 디버깅
  console.log('📋 HealthInfoTab 받은 indicators:', indicators)
  console.log('📋 indicators 타입:', typeof indicators)
  console.log('📋 indicators 배열인가:', Array.isArray(indicators))
  if (Array.isArray(indicators)) {
    console.log('📋 indicators 길이:', indicators.length)
    indicators.forEach((indicator, index) => {
      console.log(`📋 [${index}] indicator:`, indicator)
    })
  }

  // 안전성 체크
  if (!indicators || !Array.isArray(indicators)) {
    console.warn('⚠️ HealthInfoTab: indicators가 배열이 아닙니다:', indicators)
    return (
      <div className="space-y-2.5">
        <h2 className="text-[#00278C] font-league-spartan font-bold text-lg leading-[0.92] mb-2.5">
          AI 보행 지표 분석
        </h2>
        <div className="text-[#00278C] font-league-spartan font-medium text-base">
          지표 데이터를 불러올 수 없습니다.
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-2.5">
      {/* AI 보행 지표 분석 제목 */}
      <h2 className="text-[#00278C] font-league-spartan font-bold text-lg leading-[0.92] mb-2.5">
        AI 보행 지표 분석
      </h2>

      {/* 지표 개수 정보 표시 */}
      {indicators.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
          <div className="text-blue-800 text-sm">
            📊 총 {indicators.length}개의 보행 지표가 분석되었습니다.
          </div>
        </div>
      )}

      {/* 지표 아코디언 목록 */}
      <div className="space-y-2">
        {indicators.map((indicator) => (
          <GaitIndicatorAccordion
            key={indicator.id}
            indicator={indicator}
          />
        ))}
      </div>
    </div>
  )
}

export default HealthInfoTab 