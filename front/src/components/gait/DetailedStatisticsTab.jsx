import React from 'react'
import DiseasePredictionCard from './DiseasePredictionCard'
import DetailedReportCard from './DetailedReportCard'

const DetailedStatisticsTab = ({ diseases, detailedReport }) => {
  return (
    <div className="space-y-8">
      {/* 질병 예측 분석 섹션 */}
      <div className="space-y-2">
        {/* 제목과 구분선 */}
        <div className="w-full space-y-1">
          <h2 className="text-[#00278C] font-league-spartan font-bold text-lg leading-[0.92] text-left">
            질병 예측 분석
          </h2>
          <div className="w-full h-px bg-[#C7C8CA]" />
        </div>

        {/* 질병 예측 카드들 */}
        <div className="space-y-1.5 w-[310px] mx-auto">
          {diseases.map((disease) => (
            <DiseasePredictionCard
              key={disease.id}
              disease={disease}
            />
          ))}
        </div>
      </div>

      {/* 상세 분석 리포트 섹션 */}
      <div className="space-y-3">
        {/* 제목과 구분선 */}
        <div className="w-full space-y-1">
          <h2 className="text-[#00278C] font-league-spartan font-bold text-lg leading-[0.92] text-left">
            상세 분석 리포트
          </h2>
          <div className="w-full h-px bg-[#C7C8CA]" />
        </div>

        {/* 리포트 카드 */}
        <DetailedReportCard report={detailedReport} />
      </div>

      {/* 하단 스크롤 여백 */}
      <div className="h-4" />
    </div>
  )
}

export default DetailedStatisticsTab 