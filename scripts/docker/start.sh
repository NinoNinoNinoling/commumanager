#!/bin/bash
# ============================================================================
# Docker 컨테이너 시작 스크립트
# ============================================================================

set -e

echo "=========================================="
echo "마녀봇 Docker 시작"
echo "=========================================="

# .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo "📝 .env.docker를 .env로 복사하고 설정을 입력해주세요."
    echo ""
    echo "  cp .env.docker .env"
    echo "  nano .env"
    echo ""
    exit 1
fi

# data 디렉토리 생성
if [ ! -d data ]; then
    echo "📁 data 디렉토리 생성 중..."
    mkdir -p data
fi

# economy.db 초기화 (없을 경우)
if [ ! -f data/economy.db ]; then
    echo "📦 economy.db 초기화 중..."
    python init_db.py data/economy.db
fi

# Docker Compose 빌드 및 시작
echo "🐳 Docker 컨테이너 빌드 및 시작 중..."
docker-compose up -d --build

echo ""
echo "=========================================="
echo "✅ 마녀봇 시작 완료!"
echo "=========================================="
echo ""
echo "📊 서비스 상태:"
docker-compose ps
echo ""
echo "🌐 관리자 웹: http://localhost:5000"
echo ""
echo "📝 로그 확인: ./scripts/docker/logs.sh"
echo "🛑 중지: ./scripts/docker/stop.sh"
echo ""
