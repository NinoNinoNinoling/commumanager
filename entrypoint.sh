#!/bin/bash
set -e

# 데이터베이스 파일이 존재하지 않으면 초기화
if [ ! -f "/app/economy.db" ]; then
    echo "데이터베이스가 존재하지 않습니다. 초기화를 시작합니다..."
    python init_db.py
    echo "데이터베이스 초기화 완료"
else
    echo "기존 데이터베이스를 사용합니다: /app/economy.db"
fi

# 애플리케이션 실행
exec "$@"
