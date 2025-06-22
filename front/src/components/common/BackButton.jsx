import React from 'react'

const BackButton = ({ onClick }) => {
  return (
    <button 
      onClick={onClick}
      className="flex items-center gap-2 text-[#2260FF] hover:opacity-80 transition-opacity"
    >
      {/* 화살표 아이콘 */}
      <svg
        width="6"
        height="10"
        viewBox="0 0 6 10"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M5 1L1 5L5 9"
          stroke="#2260FF"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      
      {/* 텍스트 */}
      <span 
        className="text-sm font-league-spartan"
        style={{
          fontSize: '12.3px',
          fontWeight: 400,
          lineHeight: '1.789em',
          letterSpacing: '-3.33%'
        }}
      >
        뒤로가기
      </span>
    </button>
  )
}

export default BackButton 