# WALKerHOLIC 백엔드 API 명세서

## 개요
WALKerHOLIC 앱의 보행 분석 및 사용자 정보 관리를 위한 백엔드 API 명세서입니다.

## 기본 설정

### 서버 정보
- **베이스 URL:** `http://localhost:8000` (개발용)
- **인증:** 없음
- **응답 형식:** JSON
- **Content-Type:** `application/json`

### CORS 설정
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type
```

## API 엔드포인트

### 1. 보행 분석

#### **POST `/gait-analysis/langgraph-diagnosis`**
랭그래프를 통한 맞춤형 보행 진단 요청

**요청 예시:**
```
POST http://localhost:8000/gait-analysis/langgraph-diagnosis
Content-Type: application/json

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
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**응답 구조 (진단 요청 시작):**
```json
{
  "success": true,
  "data": {
    "diagnosisId": "diagnosis_12345",
    "userId": "user123",
    "status": "processing",
    "requestedAt": "2024-01-15T10:30:00Z",
    "estimatedCompletionTime": "2024-01-15T10:35:00Z",
    "message": "랭그래프 진단이 시작되었습니다."
  }
}
```

#### **GET `/gait-analysis/diagnosis/status/{diagnosisId}`**
진단 진행 상태 확인

**요청 예시:**
```
GET http://localhost:8000/gait-analysis/diagnosis/status/diagnosis_12345
Content-Type: application/json
```

**응답 구조 (진행 중):**
```json
{
  "success": true,
  "data": {
    "diagnosisId": "diagnosis_12345",
    "status": "processing",
    "progress": 45,
    "estimatedCompletionTime": "2024-01-15T10:33:00Z",
    "message": "AI가 보행 패턴을 분석하고 있습니다..."
  }
}
```

**응답 구조 (완료 시):**
```json
{
  "success": true,
  "data": {
    "diagnosisId": "diagnosis_12345",
    "status": "completed",
    "progress": 100,
    "estimatedCompletionTime": null,
    "message": "분석이 완료되었습니다!",
    "result": {
      "userId": "user123",
      "userInfo": {
        "name": "홍길동",
        "height": 175,
        "gender": "male"
      },
      "score": 73,
      "status": "보행 매우 안정적",
      "riskLevel": "정상 단계",
      "analyzedAt": "2024-01-15T10:30:00Z",
      "indicators": [
        {
          "id": "stride-time",
          "name": "보폭 시간",
          "value": "1.12초",
          "status": "normal",
          "description": "한쪽 발이 땅에 닿은 후, 같은 발이 다시 닿을 때까지 걸리는 시간입니다.",
          "result": "분석 결과 정상입니다!"
        }
      ],
      "diseases": [
        {
          "id": "parkinson",
          "name": "파킨슨병",
          "probability": -0.55,
          "status": "관찰 유지",
          "trend": "up"
        }
      ],
      "detailedReport": {
        "title": "정상 단계",
        "content": "보행 안정성이 양호한 상태입니다..."
      }
    }
  }
}
```