import api from './index.js'

/**
 * 보행 분석 API 서비스
 * 백엔드와의 보행 데이터 통신을 담당
 */

// 사용자의 보행 분석 데이터 조회
export const getGaitAnalysis = async (diagnosisId) => {
  try {
    const response = await api.get(`/gait-analysis/diagnosis/status/${diagnosisId}`)
    return response
  } catch (error) {
    console.error('보행 분석 데이터 조회 실패:', error)
    throw error
  }
}

// 보행 분석 요청 (새로운 분석 시작)
export const requestGaitAnalysis = async (userId, gaitData) => {
  try {
    const response = await api.post(`/gait-analysis/${userId}`, {
      gaitData: gaitData,
      timestamp: new Date().toISOString()
    })
    return response
  } catch (error) {
    console.error('보행 분석 요청 실패:', error)
    throw error
  }
}

// 랭그래프를 통한 진단 요청 (사용자 정보 포함)
export const requestLangGraphAnalysis = async (userInfo, gaitData) => {
  try {
    const response = await api.post('/gait-analysis/langgraph-diagnosis', {
      userInfo: {
        name: userInfo.name,
        height: userInfo.height,
        gender: userInfo.gender
      },
      gaitData: gaitData,
      timestamp: new Date().toISOString()
    })
    return response
  } catch (error) {
    console.error('랭그래프 진단 요청 실패:', error)
    throw error
  }
}

// 진단 상태 확인 (랭그래프 분석 진행 상황 체크)
export const checkDiagnosisStatus = async (diagnosisId) => {
  try {
    const response = await api.get(`/gait-analysis/diagnosis/status/${diagnosisId}`)
    return response
  } catch (error) {
    console.error('진단 상태 확인 실패:', error)
    throw error
  }
}

// 보행 분석 상태 확인 (분석 진행 상황 체크)
export const checkAnalysisStatus = async (analysisId) => {
  try {
    const response = await api.get(`/gait-analysis/status/${analysisId}`)
    return response
  } catch (error) {
    console.error('보행 분석 상태 확인 실패:', error)
    throw error
  }
}

// 보행 분석 히스토리 조회
export const getGaitAnalysisHistory = async (userId, limit = 10) => {
  try {
    const response = await api.get(`/gait-analysis/${userId}/history`, {
      params: { limit }
    })
    return response
  } catch (error) {
    console.error('보행 분석 히스토리 조회 실패:', error)
    throw error
  }
} 