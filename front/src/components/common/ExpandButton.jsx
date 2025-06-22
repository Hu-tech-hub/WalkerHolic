import React from 'react'

const ExpandButton = ({ isExpanded, onClick }) => {
  return (
    <div className="text-center">
      <button
        onClick={onClick}
        className="text-[#00278C] font-league-spartan font-medium text-sm hover:opacity-70 transition-opacity inline-flex items-center gap-1"
      >
        {isExpanded ? '접기' : '더보기'}
        <span className="text-xs">
          {isExpanded ? '▲' : '▼'}
        </span>
      </button>
    </div>
  )
}

export default ExpandButton 