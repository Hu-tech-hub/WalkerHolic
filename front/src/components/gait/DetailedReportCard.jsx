import React, { useState } from 'react'
import ExpandButton from '../common/ExpandButton'

const DetailedReportCard = ({ report }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded)
  }

  // 안전성 체크
  if (!report || typeof report !== 'object') {
    console.warn('⚠️ DetailedReportCard: 잘못된 report 객체:', report)
    return (
      <div className="bg-gray-100 rounded-[23px] p-4 shadow-[2px_2px_3px_rgba(48,48,48,0.07)]">
        <div className="text-[#00278C] font-league-spartan font-medium text-base">
          리포트 데이터를 불러올 수 없습니다.
        </div>
      </div>
    )
  }
  
  // report 객체 내용 디버깅
  console.log('📊 DetailedReportCard 받은 report:', report)
  console.log('📊 report.title:', typeof report.title, report.title)
  console.log('📊 report.content:', typeof report.content, report.content)

  // content를 안전하게 문자열로 변환 (백엔드는 이미 완벽한 문자열을 보냄)
  let safeContent = '내용을 불러올 수 없습니다.'
  
  if (typeof report.content === 'string') {
    // 백엔드에서 보낸 완벽한 진단 텍스트를 그대로 사용
    safeContent = report.content
    console.log('📊 문자열 content 사용 (길이:', report.content.length, ')')
  } else if (typeof report.content === 'object' && report.content !== null) {
    // 혹시 객체인 경우에만 처리 (일반적으로는 발생하지 않음)
    console.log('📊 content 객체 키들:', Object.keys(report.content))
    
    // content 객체에서 텍스트 추출 시도
    if (report.content.text) {
      safeContent = report.content.text
    } else if (report.content.content) {
      safeContent = report.content.content
    } else if (report.content.message) {
      safeContent = report.content.message
    } else if (report.content.description) {
      safeContent = report.content.description
    } else {
      // 마지막 수단: JSON.stringify로 가독성 있게 변환
      try {
        safeContent = JSON.stringify(report.content, null, 2)
          .replace(/[{}"]/g, '')
          .replace(/,\s*/g, '\n')
          .trim()
      } catch (e) {
        safeContent = '분석 결과를 표시할 수 없습니다.'
      }
    }
  } else {
    console.warn('📊 예상치 못한 content 타입:', typeof report.content, report.content)
  }
  
  console.log('📊 최종 safeContent:', safeContent)

  return (
    <div 
      className="bg-gray-100 rounded-[23px] p-4 shadow-[2px_2px_3px_rgba(48,48,48,0.07)]"
    >
      <div className="space-y-3">
        {/* 리포트 제목 */}
        <h3 className="text-[#00278C] font-league-spartan font-bold text-base leading-[0.92]">
          {typeof report.title === 'string' ? report.title : '제목 없음'}
        </h3>

        {/* 리포트 내용 컨테이너 */}
        <div className="relative">
          {/* 리포트 내용 - 조건부 높이 제한 */}
          <div 
            className={`
              ${isExpanded ? 'max-h-none' : 'max-h-[200px]'} 
              overflow-hidden pr-2 transition-all duration-300 ease-in-out
            `}
          >
            <div className="text-[#00278C] font-league-spartan font-medium text-base leading-[1.3] whitespace-pre-line">
              {safeContent}
            </div>
          </div>

          {/* 그라데이션 오버레이 - 축소 상태일 때만 표시 */}
          {!isExpanded && (
            <div 
              className="absolute bottom-0 left-0 right-2 h-12 pointer-events-none"
              style={{
                background: 'linear-gradient(transparent, #f3f4f6 80%)'
              }}
            />
          )}
        </div>

        {/* 더보기 버튼 - 그라데이션 영향 받지 않도록 별도 영역 */}
        <div className="relative z-10 mt-2">
          <ExpandButton 
            isExpanded={isExpanded} 
            onClick={toggleExpanded} 
          />
        </div>
      </div>
    </div>
  )
}

export default DetailedReportCard 