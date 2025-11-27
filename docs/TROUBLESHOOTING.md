# 트러블슈팅 가이드

## 목차
- [봇 403 Forbidden 오류](#봇-403-forbidden-오류)
- [컨테이너 재시작 루프](#컨테이너-재시작-루프)
- [환경 변수 설정 문제](#환경-변수-설정-문제)

---

## 봇 403 Forbidden 오류

### 증상
```
2025-11-27 05:15:37 - bot.reward_bot - ERROR - 봇 실행 실패: ('Mastodon API returned error', 403, 'Forbidden', None)
```

봇 컨테이너가 계속 재시작되며 로그에 403 Forbidden 오류가 표시됩니다.

### 원인
1. `MASTODON_INSTANCE_URL` 또는 `INTERNAL_MASTODON_INSTANCE_URL` 환경 변수가 설정되지 않음
2. `BOT_ACCESS_TOKEN` 환경 변수가 설정되지 않음
3. 액세스 토큰이 만료되었거나 권한이 부족함

### 해결 방법

#### 1. 컨테이너 재시작 루프 중단
```bash
# 봇 컨테이너 찾기
sudo docker ps -a | grep bots

# 컨테이너 중지
sudo docker stop mastodon-server-bots-1
```

#### 2. 환경 변수 확인
```bash
# 배포 환경의 .env 파일 확인
cd ~/mastodon-server/manager  # 실제 배포 경로로 이동
cat .env | grep -E "(MASTODON_INSTANCE_URL|BOT_ACCESS_TOKEN)"
```

#### 3. 누락된 환경 변수 추가

`.env` 파일을 편집하여 다음을 추가/수정:

```bash
# 필수: 마스토돈 인스턴스 URL
MASTODON_INSTANCE_URL=https://your-mastodon-instance.com

# 선택: 컨테이너 내부 접근용 URL (Docker Compose 사용 시)
# 설정하지 않으면 MASTODON_INSTANCE_URL을 사용
INTERNAL_MASTODON_INSTANCE_URL=http://mastodon-web:3000

# 필수: 봇 계정의 액세스 토큰
BOT_ACCESS_TOKEN=your_bot_access_token_here
```

#### 4. 컨테이너 재시작
```bash
# Docker Compose 사용 시
sudo docker-compose restart bots

# 또는 개별 컨테이너 시작
sudo docker start mastodon-server-bots-1
```

#### 5. 로그 확인
```bash
# 로그 실시간 확인
sudo docker logs -f mastodon-server-bots-1

# 성공 시 다음 메시지가 표시됩니다:
# 2025-11-27 XX:XX:XX - bot.utils - INFO - Mastodon 클라이언트 생성 - URL: https://..., Token: 설정됨
# 2025-11-27 XX:XX:XX - bot.reward_bot - INFO - 봇 계정: @봇 (봇 이름)
```

---

## 컨테이너 재시작 루프

### 증상
```bash
sudo docker exec mastodon-server-bots-1 printenv
# Error response from daemon: Container xxx is restarting, wait until the container is running
```

컨테이너가 계속 재시작되어 명령어를 실행할 수 없습니다.

### 원인
- 봇 프로세스가 시작 시 오류로 인해 종료
- Docker의 `restart: unless-stopped` 정책으로 인해 자동 재시작
- 환경 변수 누락, 코드 오류 등

### 해결 방법

#### 1. 로그 확인 (재시작 중에도 가능)
```bash
sudo docker logs --tail=50 mastodon-server-bots-1
```

#### 2. 컨테이너 중지
```bash
sudo docker stop mastodon-server-bots-1

# 또는 강제 종료
sudo docker kill mastodon-server-bots-1
```

#### 3. 로그에서 오류 원인 파악
- `ValueError`: 환경 변수 누락
- `403 Forbidden`: 인증 실패 (토큰 문제)
- `ImportError`: 의존성 패키지 누락

#### 4. 문제 해결 후 재시작
```bash
# .env 수정 후
sudo docker-compose up -d bots

# 또는
sudo docker start mastodon-server-bots-1
```

---

## 환경 변수 설정 문제

### Docker Compose 환경 변수 확인

#### 1. 호스트의 .env 파일 확인
```bash
cat .env
```

#### 2. 컨테이너 내부 환경 변수 확인
```bash
# 컨테이너가 실행 중일 때
sudo docker exec mastodon-server-bots-1 printenv | grep MASTODON

# 출력 예시:
# MASTODON_INSTANCE_URL=https://mastodon.social
# INTERNAL_MASTODON_INSTANCE_URL=http://mastodon-web:3000
```

#### 3. docker-compose.yml 확인
```bash
cat docker-compose.yml | grep -A 20 "environment:"
```

`docker-compose.yml`에 환경 변수가 제대로 매핑되어 있는지 확인:
```yaml
environment:
  - MASTODON_INSTANCE_URL=${MASTODON_INSTANCE_URL}
  - INTERNAL_MASTODON_INSTANCE_URL=${INTERNAL_MASTODON_INSTANCE_URL:-${MASTODON_INSTANCE_URL}}
  - BOT_ACCESS_TOKEN=${BOT_ACCESS_TOKEN}
```

### 토큰 생성 방법

마스토돈 액세스 토큰이 없는 경우:

1. 마스토돈 웹 로그인
2. **설정** → **개발** 메뉴로 이동
3. **새 애플리케이션** 클릭
4. 애플리케이션 이름 입력 (예: "커뮤니티 관리 봇")
5. 권한 설정:
   - ✅ `read` (읽기)
   - ✅ `write` (쓰기)
   - ✅ `follow` (팔로우)
6. 생성 후 **Your access token** 복사
7. `.env` 파일의 `BOT_ACCESS_TOKEN`에 붙여넣기

### 토큰 테스트

```bash
# 토큰이 유효한지 테스트
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://your-mastodon-instance.com/api/v1/accounts/verify_credentials

# 성공 시 계정 정보 JSON 반환
# 실패 시 {"error": "..."} 반환
```

---

## 추가 도움말

### 디버그 모드로 실행

더 자세한 로그를 보고 싶다면:

```bash
# docker-compose.yml 수정
environment:
  - LOG_LEVEL=DEBUG  # INFO에서 DEBUG로 변경

# 재시작
sudo docker-compose restart bots
```

### 컨테이너 셸 접속

```bash
# 컨테이너 내부로 들어가기
sudo docker exec -it mastodon-server-bots-1 /bin/bash

# 환경 변수 직접 확인
printenv | grep MASTODON
printenv | grep BOT

# Python 환경 테스트
python3 -c "import os; print(os.getenv('BOT_ACCESS_TOKEN'))"
```

### 문의

위 방법으로 해결되지 않는 경우:
1. 전체 로그 수집: `sudo docker logs mastodon-server-bots-1 > bot-logs.txt`
2. 환경 변수 수집 (토큰 제외): `cat .env | grep -v TOKEN`
3. GitHub Issue에 문의
