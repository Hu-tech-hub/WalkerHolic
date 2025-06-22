import React, { useState } from 'react'

const GaitIndicatorAccordion = ({ indicator }) => {
  const [isOpen, setIsOpen] = useState(false)

  // 상태에 따른 색상 결정
  const getStatusColor = (status) => {
    switch (status) {
      case 'normal':
        return '#0BE62C' // 초록
      case 'warning':
        return '#FFC800' // 노랑
      case 'danger':
        return '#F51A1A' // 빨강
      default:
        return '#0BE62C'
    }
  }

  const statusColor = getStatusColor(indicator.status)

  return (
    <div className="border border-[#979797] rounded-2xl p-4 space-y-3">
      {/* 토글 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-5">
          {/* 좌측 정보 */}
          <div className="flex items-center gap-3 w-40">
            {/* 토글 아이콘 */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="w-5 h-5 flex items-center justify-center"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                className={`transform transition-transform ${isOpen ? 'rotate-90' : ''}`}
              >
                <rect width="20" height="20" stroke="#000000" strokeWidth="2" fill="none"/>
                <path
                  d="M7 2L13 10L7 18"
                  stroke="#000000"
                  strokeWidth="2"
                  fill="none"
                />
              </svg>
            </button>

            {/* 지표명 */}
            <span className="font-mulish font-semibold text-lg text-black leading-[1.255]">
              {indicator.name}
            </span>
          </div>

          {/* 수치 */}
          <span className="font-noto-sans font-semibold text-lg text-black leading-[1.362] w-14">
            {indicator.value}
          </span>
        </div>

        {/* 상태 아이콘 */}
        <div 
          className="w-[26px] h-[25.5px] rounded-full shadow-[2px_2px_4px_rgba(0,0,0,0.25)]"
          style={{ backgroundColor: statusColor }}
        />
      </div>

      {/* 펼쳐지는 내용 */}
      {isOpen && (
        <div className="w-[295px] space-y-1.5">
          {/* 설명 */}
          <p className="font-mulish font-medium text-[14.5px] text-[#353535] leading-[1.255] tracking-[-4%]">
            {indicator.description}
          </p>

          {/* 분석 결과 */}
          <p 
            className={`font-mulish text-base leading-[1.255] ${
              indicator.status === 'normal' 
                ? 'font-medium' 
                : 'font-semibold'
            } text-black`}
          >
            {indicator.result}
          </p>
        </div>
      )}
    </div>
  )
}

export default GaitIndicatorAccordion 