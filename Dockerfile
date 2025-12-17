FROM python:3.11-slim

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY server.py .
COPY gen_cert.py .
COPY public/ ./public/

# 인증서 생성 (컨테이너 빌드 시 자동 생성)
RUN python gen_cert.py

# 포트 노출
EXPOSE 3000

# 서버 실행
CMD ["python", "server.py"]
