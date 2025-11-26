# WalkerHolic FastAPI Backend Dockerfile
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements_core.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_core.txt

# 프로젝트 파일 복사
COPY . .

# ChromaDB 디렉토리 생성 (없는 경우)
RUN mkdir -p chroma_db

# 임시 파일 디렉토리 생성
RUN mkdir -p temp_files

# 포트 노출
EXPOSE 8000

# 환경 변수 설정 (기본값)
ENV PYTHONUNBUFFERED=1
ENV TEMP_DIR=/app/temp_files
ENV PROJECT_ROOT=/app
ENV LOG_LEVEL=INFO

# 서버 실행
CMD ["uvicorn", "fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]

