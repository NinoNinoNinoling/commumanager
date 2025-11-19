# Part 3: 시스템 아키텍처

---

## 1. 전체 시스템 구조

```
┌─────────────────────────────────────────────────────┐
│        Whipping Edition Mastodon Server             │
│                                                      │
│  • 사용자 답글 작성                                   │
│  • OAuth 인증 제공                                   │
│  • 폐쇄형 운영 (외부 차단)                            │
│  • PostgreSQL (마스토돈 데이터) ← 읽기 전용 참조     │
└──────────────┬──────────────────────────────────────┘
               │ Mastodon API (HTTP/WebSocket)
               ↓
┌─────────────────────────────────────────────────────┐
│           Economy Bot (Python, systemd)             │
│                                                      │
│  [실시간 감시 모듈] - 24시간 구동                     │
│   • stream_local()로 로컬 타임라인 감시              │
│   • 답글 감지 → 즉시 재화 지급                       │
│   • status_id로 중복 방지                            │
│   • 별표(⭐) 감지:                                   │
│     - 상점 아이템 게시물 별표 → 자동 구매            │
│     - 양도 요청 게시물 별표 → 양도 수락              │
│   • 멘션 명령어 처리:                                │
│     - @봇 내재화 → DM 응답                           │
│     - @봇 상점 → 상점 링크 DM                        │
│     - @봇 내아이템 → 보유 아이템 목록 DM             │
│     - @봇 휴식 [날짜]까지 → 휴식 등록                │
│     - @봇 양도 @유저 [아이템] → 양도 요청 게시물     │
│     - @봇 게임 [종류] [금액] → 게임 시작             │
│                                                      │
│  [활동량 체크 모듈] - 하루 2회 (벌크)                │
│   • 오전 5시: 48시간 벌크 체크 (무거운 작업)         │
│   • 오후 12시: 중간 체크 (가벼운 확인)               │
│   • PostgreSQL에서 유저+답글 벌크 조회               │
│   • 역할 필터링 (시스템/스토리 계정 제외)            │
│   • 휴식계 유저 제외                                 │
│   • 기준 미달 시:                                    │
│     - 관리자 봇 계정으로 비공개 툿 발송              │
│     - DB에 경고 로그 저장                            │
└──────────────┬──────────────────────────────────────┘
               │ 공유 DB (SQLite)
               ↓
┌─────────────────────────────────────────────────────┐
│              SQLite Database (economy.db)           │
│                                                      │
│  • users (유저별 재화, 역할, 기숙사)                 │
│  • transactions (거래 기록)                          │
│  • warnings (경고 로그)                              │
│  • settings (시스템 설정)                            │
│  • vacation (휴식 기간)                              │
│  • items (상점 아이템)                               │
│  • inventory (보유 아이템)                           │
│  • admin_logs (관리자 작업 기록)                     │
│  • [추후] game_sessions (게임 기록)                 │
└──────────────┬──────────────────────────────────────┘
               │ 읽기/쓰기
               ↓
┌─────────────────────────────────────────────────────┐
│          Admin Web (Flask + Nginx)                  │
│                                                      │
│  [관리자 전용 - OAuth로 권한 체크]                    │
│   • 홈: 대시보드 (활동 현황, 봇 상태)                │
│   • 활동량 관리: 경고 내역 + 수동 경고 + 휴식 관리   │
│   • 재화 관리: 유저 목록 + 재화 지급/차감            │
│   • 상점 관리: 아이템 등록/수정/삭제                 │
│   • 시스템 설정: 봇 기준 변경 (DB 직접 수정)        │
│   • 관리 로그: 모든 관리 작업 기록                   │
│                                                      │
│  [선택] Google Sheets 연동 (Python API)             │
│   • 유저 재화 현황 실시간 동기화                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│          Admin Bot Account (마스토돈)                │
│                                                      │
│  • 관리자 전용 비공개 봇 계정                        │
│  • 활동량 경고 알림을 비공개 툿으로 발송             │
│  • 관리자들만 팔로우 → 실시간 알림                   │
│  • 브라우저 알림보다 마스토돈 네이티브 알림 활용     │
└─────────────────────────────────────────────────────┘
```

---

## 2. 데이터 흐름

### 2.1 재화 지급 흐름

```
1. 유저가 답글 작성
   ↓
2. 마스토돈 Streaming API 이벤트 발생
   (WebSocket 실시간 푸시)
   ↓
3. Economy Bot 실시간 감지
   stream_local() 리스너
   ↓
4. 답글 여부 확인
   if status['in_reply_to_id'] is not None
   ↓
5. 중복 체크
   status_id가 이미 처리되었는가?
   ↓ NO (새 답글)
6. 재화 지급 계산
   settings에서 replies_per_reward, reward_amount 조회
   예: 1개당 10원 or 100개당 1000원
   ↓
7. SQLite 업데이트
   a. users.balance += amount
   b. users.reply_count += 1
   c. users.total_earned += amount
   d. transactions 테이블에 기록
   ↓
8. 로그 출력 및 완료
   "[재화 지급] @user1: +10원 (답글 1개)"
```

**예외 처리**:
- 봇 자신의 답글: 무시
- 시스템 계정 답글: 무시
- 네트워크 오류: 재시도 3회

---

### 2.2 활동량 체크 흐름 (벌크)

```
[오전 5시 크론 실행]
   ↓
1. 설정 로드 (SQLite settings)
   - check_period_hours = 48
   - min_replies_48h = 20
   ↓
2. PostgreSQL 벌크 쿼리 (한 번에)
   SELECT u.id, u.username, COUNT(s.id) as replies
   FROM accounts u
   LEFT JOIN statuses s ON s.account_id = u.id
       AND s.in_reply_to_id IS NOT NULL
       AND s.created_at > NOW() - INTERVAL '48 hours'
   WHERE u.suspended = false
   GROUP BY u.id
   ↓
3. SQLite users와 매칭
   각 유저의 role, vacation 확인
   ↓
4. 각 유저별 판정
   for user in results:
       if user.role in ['admin', 'system', 'story']:
           continue  # 체크 제외
       
       if is_on_vacation(user):
           continue  # 휴식 중
       
       if user.replies < 20:
           create_warning(user)
           send_admin_notification(user)
   ↓
5. 경고 처리
   a. warnings 테이블에 기록
   b. 관리자 봇으로 비공개 툿 발송
      "⚠️ @user3님이 48시간 내 12개 답글로 기준 미달입니다."
   ↓
6. SQLite 통계 업데이트
   a. users.last_check = NOW()
   b. settings.last_check = NOW()
   ↓
7. 완료 로그
   "[활동량 체크] 완료: 28명 중 3명 경고"
```

---

### 2.3 별표 기반 구매 흐름 (신규)

```
1. 관리자가 웹에서 아이템 등록
   ↓
2. 봇이 상점 게시물 자동 생성/업데이트
   "🏪 빨강 염색약 - 100원
    ✨ 이 게시물에 별표를 누르면 자동 구매됩니다!"
   ↓
3. 유저가 게시물에 별표(⭐) 클릭
   ↓
4. Mastodon Streaming API 감지
   notification_type = 'favourite'
   ↓
5. 봇이 별표 이벤트 처리
   status_id 확인 → 상점 아이템 게시물인가?
   ↓ YES
6. 구매 처리
   a. SQLite에서 아이템 정보 조회
   b. 유저 재화 확인 (balance >= price?)
   ↓ YES
7. 구매 완료
   a. users.balance -= price
   b. inventory에 아이템 추가
   c. transactions 기록
   d. DM 발송
      "✅ 빨강 염색약 구매 완료! (-100원)
       💰 남은 재화: 1,150원"
   ↓ NO (재화 부족)
8. 구매 실패
   a. 별표 자동 취소 (선택)
   b. DM 발송
      "❌ 재화가 부족합니다!
       필요: 100원 / 보유: 80원"
```

**장점**:
- 마스토돈 네이티브 UX (별표는 익숙한 기능)
- 명령어 오타 걱정 없음
- 시각적으로 직관적
- 게시물에 아이템 이미지 첨부 가능

---

### 2.4 봇 명령어 처리 흐름

```
1. 유저가 멘션으로 명령어 입력
   "@봇 내재화"
   ↓
2. Streaming API 감지
   notification_type = 'mention'
   ↓
3. 명령어 파싱
   command = extract_command(mention.content)
   # "내재화"
   ↓
4. 명령어별 분기

   [내재화]
   ├→ SQLite에서 users 조회
   ├→ balance, total_earned 가져오기
   └→ DM 발송
      "💰 보유 재화: 1,250원
       📈 누적 획득: 3,420원"

   [상점]
   ├→ 봇의 상점 게시물 링크 조회
   └→ DM 발송
      "🏪 상점 바로가기:
       https://yourserver.com/@bot/123456
       원하는 아이템에 별표를 눌러주세요!"

   [내아이템]
   ├→ inventory에서 보유 아이템 조회
   └→ DM 발송 (아이템 목록)

   [양도 @유저 아이템명]
   ├→ 보유 아이템 확인
   ├→ 양도 요청 게시물 생성
   │  "@user2님께 금테두리를 양도하시겠습니까? 🎁
   │   받으시려면 이 게시물에 별표를 눌러주세요!"
   └→ DM 발송 (양도 요청 생성 완료)

   [휴식 날짜]
   ├→ 날짜 파싱 (2024-11-25까지)
   ├→ vacation 테이블에 추가
   └→ DM 발송 (등록 완료)

   [게임 종류 금액]
   ├→ 재화 확인
   ├→ game_sessions 생성
   ├→ DM으로 게임 진행
   └→ 결과에 따라 재화 증감
```

---

### 2.5 관리자 웹 작업 흐름

```
1. 관리자 로그인
   Mastodon OAuth
   ↓
2. 권한 확인
   account.role in ['Owner', 'Admin']
   ↓ YES
3. 대시보드 로드
   SQLite 쿼리:
   - 전체 유저 수
   - 총 재화
   - 최근 48h 답글 수
   - 경고 대상 유저
   - 봇 상태
   ↓
4. 관리 작업
   
   [재화 조정]
   ├→ 금액, 사유 입력
   ├→ 확인 팝업
   ├→ users.balance 업데이트
   ├→ transactions 기록
   ├→ admin_logs 기록
   └→ 성공 메시지
   
   [수동 경고]
   ├→ 유저 선택, 메시지 작성
   ├→ 확인 팝업
   ├→ 마스토돈 API로 DM 발송
   ├→ warnings 기록
   ├→ admin_logs 기록
   └→ 성공 메시지
   
   [설정 변경]
   ├→ settings 테이블 업데이트
   ├→ admin_logs 기록
   └→ 봇 재시작 (필요시)
```

---

## 3. 컴포넌트 상세

### 3.1 실시간 감시 봇 (reward_bot.py)

**역할**: 24시간 답글 감지 및 재화 지급

**주요 로직**:
```python
class RewardListener(StreamListener):
    def on_update(self, status):
        # 답글만 처리
        if not status['in_reply_to_id']:
            return
        
        # 중복 체크
        if status_id in processed:
            return
        
        # 재화 지급
        give_reward(user_id, amount)
```

**실행**: systemd 서비스로 24시간 구동

---

### 3.2 활동량 체크 봇 (activity_checker.py)

**역할**: 하루 2회 벌크 체크

**실행 시간**:
- 오전 5시: 메인 체크 (벌크)
- 오후 12시: 중간 체크

**주요 로직**:
```python
def bulk_check():
    # PostgreSQL 벌크 쿼리
    query = """
    SELECT u.id, COUNT(s.id) as cnt
    FROM accounts u
    LEFT JOIN statuses s ...
    WHERE s.created_at > NOW() - INTERVAL '48 hours'
    """
    
    for user, count in results:
        if count < threshold:
            warn(user)
```

---

### 3.3 명령어 핸들러 (command_handler.py)

**역할**: 봇 멘션 및 별표 처리

**멘션 명령어**:
```
@봇 내재화          - 보유 재화 조회
@봇 상점            - 상점 게시물 링크
@봇 내아이템        - 보유 아이템 목록
@봇 양도 @유저 아이템 - 양도 요청 게시물 생성
@봇 휴식 [날짜]까지  - 휴식 등록
@봇 게임 [종류] [금액] - 게임 시작
@봇 도움말          - 명령어 안내
```

**별표(⭐) 이벤트**:
```
상점 아이템 게시물 별표 → 자동 구매
양도 요청 게시물 별표 → 양도 수락
```

---

### 3.4 관리자 웹 (Flask)

**라우트 구조**:
```
/                   → 홈 (대시보드)
/login              → OAuth 로그인
/logout             → 로그아웃
/activity           → 활동량 관리
/activity/warn      → 수동 경고
/balance            → 재화 관리
/balance/adjust     → 재화 조정
/shop               → 상점 관리
/shop/items         → 아이템 CRUD
/settings           → 시스템 설정
/logs               → 관리 로그
```

---

## 4. 성능 고려사항

### 4.1 병목 지점

**PostgreSQL 쿼리**:
- 문제: 매시간 30명 조회 시 부하
- 해결: 하루 2회 벌크 조회 (360배 감소)

**SQLite 동시 쓰기**:
- 문제: 다중 프로세스 동시 쓰기
- 해결: WAL 모드 + 재시도 로직

**Streaming API 연결**:
- 문제: 네트워크 끊김
- 해결: 자동 재연결 + systemd 재시작

---

### 4.2 확장성

**50명 → 100명**:
- SQLite 충분
- 봇 성능 문제 없음
- 마스토돈 RAM 여유 있음

**100명 → 500명**:
- SQLite → PostgreSQL 마이그레이션
- 봇 멀티 프로세스
- 서버 업그레이드 필요

---

## 다음 문서

→ [Part 4: 데이터베이스 설계](04-database.md)
