import React from 'react'

const DiseasePredictionCard = ({ disease }) => {
  // 확률에 따른 그래프 색상 결정
  const getGraphColor = (id, probability) => {
    if (id === 'parkinson') {
      return {
        fill: 'linear-gradient(to bottom, #49A677 0%, transparent 100%)',
        stroke: '#5DB48A'
      }
    } else {
      return {
        fill: 'linear-gradient(to bottom, #EB94A2 0%, transparent 100%)',
        stroke: '#EB7487'
      }
    }
  }

  // 트렌드 아이콘 색상
  const getTrendColor = (trend) => {
    return trend === 'up' ? '#0BE62C' : '#F51A1A'
  }

  const graphColor = getGraphColor(disease.id, disease.probability)
  const trendColor = getTrendColor(disease.trend)
  const absoluteProbability = Math.abs(disease.probability)

  return (
    <div className="flex items-center justify-end gap-12 py-2.5 px-2.5 border-b border-[rgba(151,151,151,0.5)]">
      {/* 좌측 질병 정보 */}
      <div className="flex items-center gap-6 w-[290px]">
        {/* 질병명과 상태 */}
        <div className="flex flex-col items-center gap-0.5 w-[73.43px]">
          <span className="font-inter font-bold text-base text-[#2E2E30] leading-[1.21] w-full">
            {disease.name}
          </span>
          <span className="font-inter font-medium text-xs text-[#2E2E30] leading-[1.21] w-full">
            {disease.status}
          </span>
        </div>

        {/* 그래프 */}
        <div className="relative w-[56.35px] h-[18.1px]">
          {/* 배경 그라데이션 */}
          <div 
            className="absolute inset-0 rounded-sm"
            style={{
              background: graphColor.fill,
              border: `1px solid ${graphColor.stroke}`
            }}
          />
        </div>

        {/* 확률 수치 */}
        <div className="w-[51px]">
          <span className="font-inter font-bold text-sm text-[#2E2E30] leading-[1.21] text-center block">
            {disease.probability > 0 ? '+' : ''}{disease.probability.toFixed(2)}%
          </span>
        </div>

        {/* 트렌드 아이콘 */}
        <div className="w-6 h-6 flex items-center justify-center">
          {disease.trend === 'up' ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 0L12 19" stroke={trendColor} strokeWidth="2"/>
              <path d="M5 12L12 5L19 12" stroke={trendColor} strokeWidth="2"/>
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 5L12 24" stroke={trendColor} strokeWidth="2"/>
              <path d="M5 12L12 19L19 12" stroke={trendColor} strokeWidth="2"/>
            </svg>
          )}
        </div>
      </div>
    </div>
  )
}

export default DiseasePredictionCard 