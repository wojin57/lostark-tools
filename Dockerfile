# 파이썬 경량 버전 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필수 라이브러리 설치 (InquirerPy 환경 대응)
RUN apt-get update && apt-get install -y \
    locales \
    && rm -rf /var/lib/apt/lists/*

# 한글 출력을 위한 환경 변수 설정
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# streamlit 기본 포트인 8501번을 외부에 알림
EXPOSE 8501

# 컨테이너 실행 시 Bash 셸을 기본으로 실행
CMD ["/bin/bash"]