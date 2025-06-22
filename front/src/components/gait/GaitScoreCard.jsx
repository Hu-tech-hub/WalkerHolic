import React from 'react'

const GaitScoreCard = ({ score, status }) => {
  // 점수에 따른 색상 결정
  const getScoreColor = (score) => {
    if (score >= 80) return '#0BE62C' // 정상 (초록)
    if (score >= 60) return '#FFC800' // 주의 (노랑)
    return '#F51A1A' // 위험 (빨강)
  }

  // 점수에 따른 표정 결정
  const getEmotionIcon = (score) => {
    if (score >= 80) {
      return (
        <div className="w-[18px] h-[17px] relative">
          {/* 웃는 얼굴 */}
          <div className="absolute w-[2.5px] h-[2.5px] bg-white rounded-full" style={{ left: '5px', top: '6px' }} />
          <div className="absolute w-[2.5px] h-[2.5px] bg-white rounded-full" style={{ left: '11px', top: '6px' }} />
          <div className="absolute w-[11px] h-[11px] bg-white rounded-full" style={{ left: '4px', top: '10px' }} />
        </div>
      )
    } else {
      return (
        <div className="w-[18px] h-[17px] relative">
          {/* 울상 */}
          <div className="absolute w-[2.5px] h-[2.5px] bg-white rounded-full" style={{ left: '5px', top: '6px' }} />
          <div className="absolute w-[2.5px] h-[2.5px] bg-white rounded-full" style={{ left: '11px', top: '6px' }} />
          <div className="absolute w-[11px] h-[11px] bg-white rounded-full" style={{ left: '4px', top: '10px' }} />
        </div>
      )
    }
  }

  const scoreColor = getScoreColor(score)
  const percentage = Math.min(score, 100)

  return (
    <div 
      className="bg-white border-[1.7px] border-[#00278C] rounded-[23px] p-4 relative"
      style={{ height: '120px' }}
    >
      <div className="flex items-center justify-between h-full">
        {/* 좌측 점수 정보 */}
        <div className="flex flex-col gap-3 w-[126px] ml-3 pt-2">
          <h3 className="text-[#00278C] font-league-spartan font-bold text-base leading-[0.92]">
            보행 점수
          </h3>
          
          <div className="text-[#00278C] font-pretendard font-medium text-2xl leading-[1.193]">
            {score}점
          </div>
          
          <div className="text-[#00278C] font-league-spartan font-medium text-xs leading-[0.92]">
            {status}
          </div>
        </div>

        {/* 우측 그래프 영역 */}
        <div className="relative w-[137px] h-[79px] flex items-center justify-center">
          {/* 배경 원 */}
          <div 
            className="absolute w-[125px] h-[119px] rounded-full bg-[#E9EDF0]"
            style={{ left: '6px', top: '-20px' }}
          />
          
          {/* 점수 원 */}
          <div 
            className="absolute w-[137px] h-[131px] rounded-full"
            style={{ 
              left: '0px', 
              top: '-26px',
              background: `conic-gradient(${scoreColor} 0deg ${percentage * 3.6}deg, transparent ${percentage * 3.6}deg 360deg)`
            }}
          />

          {/* 중앙 표정 아이콘 */}
          <div className="relative z-10 w-[35px] h-[34px] bg-[#ECEAF8] rounded-full flex items-center justify-center">
            <div 
              className="w-[18px] h-[17px] flex items-center justify-center rounded-full"
              style={{ backgroundColor: scoreColor }}
            >
              {getEmotionIcon(score)}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GaitScoreCard 