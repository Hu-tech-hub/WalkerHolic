# 백엔드 랭그래프 데이터 래핑 가이드

## 개요
프론트엔드의 비동기 진단 요청 구조에 맞춰 랭그래프 데이터를 래핑하는 방법을 설명합니다.

## 현재 랭그래프 응답 구조
```json
{
  "data": {
    "score": 87,
    "status": "보행 매우 안정적",
    "userId": "user_001",
    "diseases": [...],
    "riskLevel": "정상 단계",
    "analyzedAt": "2025-06-18T09:13:12.009125",
    "indicators": [...],
    "detailedReport": {...}
  },
  "success": true
}
```

## 필요한 API 엔드포인트 및 응답 구조

### 1단계: 진단 요청 시작
**엔드포인트**: `POST /gait-analysis/langgraph-diagnosis`

**요청 데이터**:
```json
{
  "userInfo": {
    "name": "홍길동",
    "height": 175,
    "gender": "male"
  },
  "gaitData": {
    "walkingTime": 60,
    "steps": 120,
    "distance": 100
  },
  "timestamp": "2025-06-18T09:13:12.009125"
}
```

**응답 구조**:
```json
{
  "success": true,
  "data": {
    "diagnosisId": "diagnosis_67890",
    "userId": "user_001",
    "status": "processing",
    "requestedAt": "2025-06-18T09:13:12.009125",
    "estimatedCompletionTime": "2025-06-18T09:18:12.009125",
    "message": "랭그래프 진단이 시작되었습니다."
  }
}
```

### 2단계: 상태 확인 - 진행 중
**엔드포인트**: `GET /gait-analysis/diagnosis/status/{diagnosisId}`

**응답 구조 (진행 중)**:
```json
{
  "success": true,
  "data": {
    "diagnosisId": "diagnosis_67890",
    "status": "processing",
    "progress": 65,
    "estimatedCompletionTime": "2025-06-18T09:16:12.009125",
    "message": "AI가 보행 패턴을 분석하고 있습니다..."
  }
}
```

**가능한 status 값**:
- `"processing"` - 처리 중
- `"analyzing"` - 분석 중  
- `"generating_report"` - 리포트 생성 중
- `"completed"` - 완료
- `"failed"` - 실패

**단계별 message 예시**:
- `"진단 요청을 보내는 중..."`
- `"랭그래프 분석 중..."`
- `"AI가 보행 패턴을 분석하고 있습니다..."`
- `"질병 위험도를 계산하고 있습니다..."`
- `"맞춤형 보고서를 생성하고 있습니다..."`

### 3단계: 상태 확인 - 완료 시 (핵심!)
**엔드포인트**: `GET /gait-analysis/diagnosis/status/{diagnosisId}`

**응답 구조 (완료 시)**:
```json
{
  "success": true,
  "data": {
    "diagnosisId": "diagnosis_67890",
    "status": "completed",
    "progress": 100,
    "estimatedCompletionTime": null,
    "message": "분석이 완료되었습니다!",
    "result": {
      "score": 87,
      "status": "보행 매우 안정적",
      "userId": "user_001",
      "diseases": [
        {
          "id": "parkinson",
          "name": "파킨슨병",
          "trend": "down",
          "status": "정상 범위",
          "probability": -2.5
        },
        {
          "id": "stroke",
          "name": "뇌졸중",
          "trend": "down",
          "status": "정상 범위",
          "probability": -4
        }
      ],
      "riskLevel": "정상 단계",
      "analyzedAt": "2025-06-18T09:13:12.009125",
      "indicators": [
        {
          "id": "stride-time",
          "name": "보폭 시간",
          "value": "0.87초",
          "result": "분석 결과 주의입니다!",
          "status": "warning",
          "description": "한쪽 발이 땅에 닿은 후, 같은 발이 다시 닿을 때까지 걸리는 시간입니다. 걸음 템포를 확인할 수 있어요."
        },
        {
          "id": "double-support",
          "name": "양발 지지 비율",
          "value": "30.4%",
          "result": "분석 결과 위험입니다!",
          "status": "danger",
          "description": "두 발이 동시에 땅에 닿아 있는 시간의 비율이에요. 보행 균형이 불안할수록 높아집니다."
        },
        {
          "id": "stride-difference",
          "name": "양발 보폭 차이",
          "value": "0.01m",
          "result": "분석 결과 정상입니다!",
          "status": "normal",
          "description": "왼발과 오른발의 걸음 길이가 얼마나 다른지를 보여줍니다. 좌우 균형 상태를 파악할 수 있어요."
        },
        {
          "id": "walking-speed",
          "name": "평균 보행 속도",
          "value": "1.2m/s",
          "result": "분석 결과 주의입니다!",
          "status": "warning",
          "description": "단위 시간 동안 이동한 거리를 나타내는 지표입니다. 전체 활동성과 운동 능력을 확인할 수 있어요."
        }
      ],
      "detailedReport": {
        "title": "비정상",
        "content": "임상 평가: 비정상\n\n주요 소견: 환자의 보행 속도(1.18 m/s)는 정상 범위(1.0-1.4 m/s)에 속하지만, 보폭 시간(0.87초)은 정상보다 짧고, 보폭 길이(1.00m)도 정상보다 짧으며, 보행률(138걸음/분)은 높아지고 있습니다. 또한, 보행 지표의 변동성(보폭 시간 17.4%, 보행 속도 17.0%)이 매우 높아 비대칭성과 불안정성을 시사합니다. 참조문헌 1에 따르면, \"보행 속도와 관련된 지표들이 정상 범위 내에 있더라도, 보폭 시간과 변동성은 비정상적일 수 있으며, 특히 변동성이 높을 경우 보행의 불안정성을 의미할 수 있다.\"\n\n문헌 근거:\n- 참조문헌 1 (gait_characteristics_of_post_stroke_hemiparetic.11.pdf): \"보폭 시간 변동성: 17.4% (정상: <5%)\"는 비정상적이며, 보행의 불안정성을 시사한다.\n- 참조문헌 2 (gait_characteristics_of_post_stroke_hemiparetic.11...."
      }
    }
  }
}
```

## 래핑 방법 요약

### 🔄 변경 전후 비교

**변경 전 (기존 랭그래프 응답)**:
```json
{
  "data": { 랭그래프 데이터 },
  "success": true
}
```

**변경 후 (래핑된 응답)**:
```json
{
  "success": true,
  "data": {
    "diagnosisId": "diagnosis_67890",
    "status": "completed",
    "progress": 100,
    "message": "분석이 완료되었습니다!",
    "result": { 기존 랭그래프 데이터를 여기에 }
  }
}
```

### 🎯 핵심 포인트

1. **기존 랭그래프 `data` 내용** → **새로운 `data.result`로 이동**
2. **`data.status: "completed"` 추가 필수**
3. **`data.progress: 100` 추가 필수**
4. **`data.diagnosisId` 고유 ID 생성 필수**

## 백엔드 구현 의사코드

```python
def get_diagnosis_status(diagnosis_id):
    """진단 상태 확인 API"""
    diagnosis = get_diagnosis_from_db(diagnosis_id)
    
    if diagnosis.status == "completed":
        # 랭그래프 결과 가져오기
        langgraph_result = get_langgraph_result(diagnosis_id)
        
        return {
            "success": True,
            "data": {
                "diagnosisId": diagnosis_id,
                "status": "completed",
                "progress": 100,
                "estimatedCompletionTime": None,
                "message": "분석이 완료되었습니다!",
                "result": langgraph_result["data"]  # 🎯 기존 랭그래프 data를 여기에!
            }
        }
    
    elif diagnosis.status == "failed":
        return {
            "success": False,
            "error": {
                "code": "DIAGNOSIS_FAILED",
                "message": diagnosis.error_message
            }
        }
    
    else:
        # 진행 중
        return {
            "success": True,
            "data": {
                "diagnosisId": diagnosis_id,
                "status": diagnosis.status,
                "progress": diagnosis.progress,
                "estimatedCompletionTime": diagnosis.estimated_completion,
                "message": get_progress_message(diagnosis.status)
            }
        }

def get_progress_message(status):
    """진행 상태별 메시지 반환"""
    messages = {
        "processing": "AI가 보행 패턴을 분석하고 있습니다...",
        "analyzing": "질병 위험도를 계산하고 있습니다...",
        "generating_report": "맞춤형 보고서를 생성하고 있습니다..."
    }
    return messages.get(status, "분석 중...")
```

## 테스트 시나리오

### 1. 정상 플로우
1. `POST /gait-analysis/langgraph-diagnosis` → `diagnosisId` 받기
2. `GET /gait-analysis/diagnosis/status/{diagnosisId}` 주기적 호출
3. `status: "processing"` → `status: "analyzing"` → `status: "completed"`
4. 완료 시 `result`에서 랭그래프 데이터 확인

### 2. 에러 처리
- 잘못된 `diagnosisId`: 404 응답
- 분석 실패: `status: "failed"` + 에러 메시지
- 타임아웃: 클라이언트에서 2분 후 자동 종료

## 주의사항

1. **diagnosisId는 고유해야 함** (UUID 권장)
2. **progress는 0-100 사이 정수**
3. **estimatedCompletionTime은 ISO 8601 형식**
4. **랭그래프 데이터 구조는 절대 변경하지 말 것**
5. **완료 시 result 필드에 기존 data 내용을 그대로 복사**

---

> 💡 **요약**: 기존 랭그래프 응답의 `data` 내용을 `data.result`로 옮기고, 진단 상태 관리용 메타데이터를 추가하면 됩니다! 