# WalkerHolic Frontend Dockerfile
FROM node:18

WORKDIR /app

# package.json만 복사 (package-lock.json 제외)
COPY package.json ./

# 에러 메시지 제안: package-lock.json과 node_modules 삭제 후 재설치
RUN rm -rf node_modules package-lock.json && \
    npm install

# 프로젝트 파일 복사
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]