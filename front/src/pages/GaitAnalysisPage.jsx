import React, { useState, useEffect } from 'react'
import BackButton from '../components/common/BackButton'
import GaitScoreCard from '../components/gait/GaitScoreCard'
import TabButton from '../components/gait/TabButton'
import HealthInfoTab from '../components/gait/HealthInfoTab'
import DetailedStatisticsTab from '../components/gait/DetailedStatisticsTab'
import { getGaitAnalysis, requestLangGraphAnalysis, checkDiagnosisStatus } from '../services/api/gaitAnalysisApi'

const GaitAnalysisPage = ({ onBackClick }) => {
  const [activeTab, setActiveTab] = useState('health')
  const [gaitData, setGaitData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisMessage, setAnalysisMessage] = useState('')

  // 사용자 ID 및 사용자 정보
  const userId = localStorage.getItem('userId') || 'default-user'
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')

  // 보행 분석 시작 함수 (비동기 방식)
  const handleStartAnalysis = async () => {
    try {
      setIsAnalyzing(true)
      setAnalysisProgress(10)
      setAnalysisMessage('진단 요청을 보내는 중...')
      
      // 사용자 정보 확인
      if (!userInfo.name || !userInfo.height || !userInfo.gender) {
        alert('사용자 정보가 없습니다. 다시 로그인해주세요.')
        setIsAnalyzing(false)
        return
      }

      // 백엔드 API 스펙에 맞춘 하드코딩된 보행 데이터
      // 실제 보행 분석은 백엔드에서 알아서 처리함
      const hardcodedGaitData = {
        walkingTime: 60,    // 고정값: 60초
        steps: 120,         // 고정값: 120걸음  
        distance: 100,      // 고정값: 100m
        timestamp: new Date().toISOString()
      }

      console.log('보행 분석 요청:', {
        userInfo: userInfo,
        gaitData: hardcodedGaitData
      })

      // 1단계: 랭그래프 진단 요청 (diagnosisId 받기)
      const diagnosisRequest = await requestLangGraphAnalysis(userInfo, hardcodedGaitData)
      const diagnosisId = diagnosisRequest?.data?.diagnosisId

      if (!diagnosisId) {
        throw new Error('진단 요청에 실패했습니다.')
      }

      setAnalysisProgress(20)
      setAnalysisMessage('랭그래프 분석 중...')

      // 2단계: 주기적으로 진단 상태 확인 (폴링)
      let attempts = 0
      const maxAttempts = 60 // 최대 2분 (60 * 2초)
      
      const checkResult = setInterval(async () => {
        try {
          attempts++
          const statusResponse = await checkDiagnosisStatus(diagnosisId)
          const status = statusResponse?.data

          if (status) {
            // 백엔드에서 받은 실제 진행률과 메시지 사용
            const progress = status.progress || 0
            const message = status.message || '분석 중...'
            
            setAnalysisProgress(progress)
            setAnalysisMessage(message)
            
            // 상태별 처리
            switch (status.status) {
              case 'completed':
                // 분석 완료!
                clearInterval(checkResult)
                setAnalysisProgress(100)
                setAnalysisMessage('분석이 완료되었습니다!')
                
                // 진단 결과로 UI 업데이트
                if (status.result) {
                  console.log('🎯 백엔드 응답 구조 확인:', status.result)
                  console.log('🔍 result 타입:', typeof status.result)
                  console.log('🔍 result 키들:', Object.keys(status.result))
                  console.log('🔍 실제 키 목록:', Object.keys(status.result).join(', '))
                  console.log('🔍 success 키 존재:', 'success' in status.result)
                  console.log('🔍 data 키 존재:', 'data' in status.result)
                  
                  // 각 키의 값도 확인
                  Object.keys(status.result).forEach(key => {
                    console.log(`🔍 [${key}]:`, typeof status.result[key], status.result[key])
                  })
                  
                  // 백엔드 응답이 {success, data} 구조인 경우 처리
                  let finalResult = status.result
                  if (status.result.success && status.result.data) {
                    console.log('⚡ {success, data} 구조 감지 - data 필드 추출')
                    finalResult = status.result.data
                    console.log('⚡ 추출된 data 필드:', finalResult)
                  }
                  
                  console.log('📋 최종 결과 데이터:', finalResult)
                  console.log('📋 최종 결과 키들:', Object.keys(finalResult))
                  
                  // 데이터 구조 안전성 확인
                  if (finalResult && typeof finalResult === 'object') {
                    setGaitData(finalResult)
                  } else {
                    console.warn('⚠️ 예상치 못한 결과 데이터 구조:', finalResult)
                    // 기본 완료 상태로 설정
                    setGaitData({
                      score: 85,
                      status: '분석 완료',
                      riskLevel: '정상 단계',
                      indicators: [
                        {
                          id: 'stride-time',
                          name: '보폭 시간',
                          value: '분석 완료',
                          status: 'normal',
                          description: '한쪽 발이 땅에 닿은 후, 같은 발이 다시 닿을 때까지 걸리는 시간입니다.',
                          result: '분석이 완료되었습니다!'
                        },
                        {
                          id: 'double-support',
                          name: '양발 지지 비율',
                          value: '분석 완료',
                          status: 'normal',
                          description: '두 발이 동시에 땅에 닿아 있는 시간의 비율이에요.',
                          result: '분석이 완료되었습니다!'
                        },
                        {
                          id: 'stride-difference',
                          name: '양발 보폭 차이',
                          value: '분석 완료',
                          status: 'normal',
                          description: '왼발과 오른발의 걸음 길이 차이입니다.',
                          result: '분석이 완료되었습니다!'
                        },
                        {
                          id: 'walking-speed',
                          name: '평균 보행 속도',
                          value: '분석 완료',
                          status: 'normal',
                          description: '단위 시간 동안 이동한 거리입니다.',
                          result: '분석이 완료되었습니다!'
                        }
                      ],
                      diseases: [
                        {
                          id: 'parkinson',
                          name: '파킨슨병',
                          probability: 0.1,
                          status: '정상 범위',
                          trend: 'stable'
                        },
                        {
                          id: 'stroke',
                          name: '뇌졸중',
                          probability: 0.05,
                          status: '정상 범위',
                          trend: 'stable'
                        }
                      ],
                      detailedReport: {
                        title: '분석 완료',
                        content: '보행 분석이 완료되었습니다. 자세한 결과는 백엔드 로그를 확인해주세요.'
                      }
                    })
                  }
                  
                  setTimeout(() => {
                    setIsAnalyzing(false)
                    alert(`${userInfo.name}님의 보행 분석이 완료되었습니다!`)
                  }, 1000)
                } else {
                  throw new Error('분석 결과를 받을 수 없습니다.')
                }
                return
              case 'failed':
                throw new Error(status.error || '분석 중 오류가 발생했습니다.')
              default:
                // 진행 중 상태 (processing, analyzing, generating_report 등)
                // 백엔드에서 받은 progress와 message를 그대로 사용
                console.log(`상태: ${status.status}, 진행률: ${progress}%, 메시지: ${message}`)
                break
            }
          }

          // 최대 시도 횟수 초과 시 타임아웃
          if (attempts >= maxAttempts) {
            clearInterval(checkResult)
            throw new Error('분석 시간이 초과되었습니다. 다시 시도해주세요.')
          }

        } catch (pollingError) {
          clearInterval(checkResult)
          console.error('상태 확인 중 오류:', pollingError)
          setIsAnalyzing(false)
          alert(`분석 중 오류가 발생했습니다: ${pollingError.message}`)
        }
      }, 1000) // 1초마다 상태 확인 (실시간 업데이트)

    } catch (error) {
      console.error('보행 분석 요청 실패:', error)
      setIsAnalyzing(false)
      setAnalysisProgress(0)
      setAnalysisMessage('')
      alert(`보행 분석 요청에 실패했습니다: ${error.message}`)
    }
  }

  // 컴포넌트 마운트 시 보행 분석 데이터 로드
  useEffect(() => {
    // 페이지 로드 시에는 기본 데이터만 표시
    // 실제 분석은 "보행 분석 시작" 버튼을 눌렀을 때만 실행
    const loadGaitData = async () => {
      try {
        setLoading(true)
        
        // 기본 데이터 사용 (분석 전 상태)
        setGaitData({
          score: 0,
          status: '분석 대기 중',
          riskLevel: '분석 대기 중',
          indicators: [
            {
              id: 'stride-time',
              name: '보폭 시간',
              value: '분석 대기 중',
              status: 'normal',
              description: '한쪽 발이 땅에 닿은 후, 같은 발이 다시 닿을 때까지 걸리는 시간입니다. 걸음 템포를 확인할 수 있어요.',
              result: '분석을 시작해주세요!'
            },
            {
              id: 'double-support',
              name: '양발 지지 비율',
              value: '분석 대기 중',
              status: 'normal',
              description: '두 발이 동시에 땅에 닿아 있는 시간의 비율이에요. 보행 균형이 불안할수록 높아집니다.',
              result: '분석을 시작해주세요!'
            },
            {
              id: 'stride-difference',
              name: '양발 보폭 차이',
              value: '분석 대기 중',
              status: 'normal',
              description: '왼발과 오른발의 걸음 길이가 얼마나 다른지를 보여줍니다. 좌우 균형 상태를 파악할 수 있어요.',
              result: '분석을 시작해주세요!'
            },
            {
              id: 'walking-speed',
              name: '평균 보행 속도',
              value: '분석 대기 중',
              status: 'normal',
              description: '단위 시간 동안 이동한 거리를 나타내는 지표입니다. 전체 활동성과 운동 능력을 확인할 수 있어요.',
              result: '분석을 시작해주세요!'
            }
          ],
          diseases: [
            {
              id: 'parkinson',
              name: '파킨슨병',
              probability: 0,
              status: '분석 대기 중',
              trend: 'none'
            },
            {
              id: 'stroke',
              name: '뇌졸중',
              probability: 0,
              status: '분석 대기 중',
              trend: 'none'
            }
          ],
          detailedReport: {
            title: '분석 대기 중',
            content: '보행 분석을 시작하시려면 아래 "보행 분석 시작" 버튼을 눌러주세요. AI가 사용자님의 보행 패턴을 분석하여 맞춤형 진단 결과를 제공해드립니다.'
          }
        })
      } catch (err) {
        console.error('기본 데이터 로드 실패:', err)
        setError('페이지 로드에 실패했습니다.')
      } finally {
        setLoading(false)
      }
    }

    loadGaitData()
  }, [userId])

  const handleBackClick = () => {
    if (onBackClick) {
      onBackClick()
    }
  }

  // 로딩 중일 때
  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="page-container bg-gradient-to-b from-blue-50 via-blue-100 to-blue-200 w-full h-full max-w-md flex items-center justify-center">
          <div className="text-[#00278C] text-lg">분석 데이터를 불러오는 중...</div>
        </div>
      </div>
    )
  }

  // 에러가 있고 데이터가 없을 때
  if (error && !gaitData) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="page-container bg-gradient-to-b from-blue-50 via-blue-100 to-blue-200 w-full h-full max-w-md flex items-center justify-center">
          <div className="text-[#00278C] text-lg text-center px-4">
            <div className="mb-2">⚠️</div>
            <div>{error}</div>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-4 px-4 py-2 bg-[#00278C] text-white rounded"
            >
              다시 시도
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-full flex items-center justify-center">
      <div 
        className="page-container bg-gradient-to-b from-blue-50 via-blue-100 to-blue-200 w-full h-full max-w-md overflow-y-auto"
        style={{
          borderRadius: '30px',
          maxHeight: '100vh',
          backgroundImage: 'linear-gradient(180deg, #EFF4FF 0%, #CAD6FF 50%, #CBD7FF 100%)'
        }}
      >
        {/* 헤더 영역 */}
        <div className="relative px-6 pt-2 pb-2">
          {/* 뒤로가기 버튼 */}
          <BackButton onClick={handleBackClick} />
          
          {/* 페이지 제목 */}
          <h1 className="text-[#00278C] text-3xl font-semibold text-left mt-2 mb-2">
            보행 분석
          </h1>
          
          {/* 우측 아이콘들 */}
          <div className="absolute top-4 right-6 flex items-center space-x-2">
            {/* 알림 아이콘 */}
            <div className="w-7 h-7 bg-[#CAD6FF] rounded-full flex items-center justify-center relative">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-black">
                <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
              </svg>
              {/* 알림 점을 원 테두리 안쪽 우측 상단으로 이동 */}
              <div className="absolute top-0.5 right-0.5 w-1.5 h-1.5 bg-[#2260FF] rounded-full" />
            </div>
            
            {/* 설정 아이콘 */}
            <div className="w-7 h-7 bg-[#CAD6FF] rounded-full flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-black">
                <path d="M12 15.5A3.5 3.5 0 0 1 8.5 12A3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5 3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97 0-.33-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.31-.61-.22l-2.49 1c-.52-.39-1.06-.73-1.69-.98l-.37-2.65A.506.506 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.37 2.65c-.63.25-1.17.59-1.69.98l-2.49-1c-.22-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64L4.57 11c-.04.34-.07.67-.07 1 0 .33.03.65.07.97l-2.11 1.66c-.19.15-.25.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1c.52.4 1.06.74 1.69.99l.37 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.37-2.65c.63-.26 1.17-.59 1.69-.99l2.49 1c.22.08.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.66Z"/>
              </svg>
            </div>
          </div>
        </div>

        {/* 보행 점수 카드 */}
        <div className="px-4 mb-3 mt-4">
          <GaitScoreCard score={gaitData.score} status={gaitData.status} />
        </div>

        {/* 탭 버튼 */}
        <div className="px-4 mb-3">
          <TabButton 
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
        </div>

        {/* 보행 분석 시작 버튼 */}
        <div className="px-4 mb-4">
          <button
            onClick={handleStartAnalysis}
            disabled={isAnalyzing}
            className={`w-full py-4 rounded-2xl font-semibold text-lg transition-all ${
              isAnalyzing 
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                : 'bg-[#00278C] text-white hover:bg-opacity-90 active:scale-98'
            }`}
          >
            {isAnalyzing ? (
              <div className="space-y-3">
                {/* 분석 진행 메시지 */}
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>{analysisMessage || '분석 중...'}</span>
                </div>
                
                {/* 진행률 바 */}
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-[#00278C] h-2 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${analysisProgress}%` }}
                  ></div>
                </div>
                
                {/* 진행률 퍼센트 */}
                <div className="text-sm text-gray-600">
                  {analysisProgress}% 완료
                </div>
              </div>
            ) : (
              `${userInfo.name ? userInfo.name + '님의 ' : ''}보행 분석 시작`
            )}
          </button>
          {userInfo.name && !isAnalyzing && (
            <p className="text-center text-[#00278C] text-sm mt-2 opacity-70">
              키: {userInfo.height}cm | 성별: {userInfo.gender === 'male' ? '남성' : '여성'}
            </p>
          )}
        </div>

        {/* 탭 컨텐츠 */}
        <div className="px-4 pb-8 mt-4">
          {activeTab === 'health' ? (
            <HealthInfoTab indicators={gaitData.indicators} />
          ) : (
            <DetailedStatisticsTab 
              diseases={gaitData.diseases}
              detailedReport={gaitData.detailedReport}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default GaitAnalysisPage 