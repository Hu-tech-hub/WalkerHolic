import React from 'react'

const TabButton = ({ activeTab, onTabChange }) => {
  return (
    <div 
      className="bg-[#BACAF5] rounded-2xl p-1 flex items-center"
      style={{ height: 'auto' }}
    >
      {/* 건강 정보 탭 */}
      <button
        onClick={() => onTabChange('health')}
        className={`flex-1 py-2.5 px-3 rounded-xl font-pretendard font-semibold text-sm transition-all ${
          activeTab === 'health'
            ? 'bg-white text-[#00278C] shadow-[2px_2px_4px_rgba(0,0,0,0.35)]'
            : 'text-[#3C4D79]'
        }`}
        style={{
          fontSize: '15px',
          lineHeight: '1.4em',
          letterSpacing: '-2.5%'
        }}
      >
        건강 정보
      </button>

      {/* 상세 통계 탭 */}
      <button
        onClick={() => onTabChange('statistics')}
        className={`flex-1 py-2.5 px-3 rounded-xl font-pretendard font-semibold text-sm transition-all ${
          activeTab === 'statistics'
            ? 'bg-white text-[#00278C] shadow-[2px_2px_4px_rgba(0,0,0,0.35)]'
            : 'text-[#3C4D79]'
        }`}
        style={{
          fontSize: '15px',
          lineHeight: '1.4em',
          letterSpacing: '-2.5%'
        }}
      >
        상세 통계
      </button>
    </div>
  )
}

export default TabButton 