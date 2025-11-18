# 사용 시나리오 (Use Cases)

## 목적
시스템의 실제 동작을 구체적으로 정의하여 요구사항 검증 및 구현 가이드로 활용

---

## UC-01: 신규 유저 등록

### 액터
- 봇 시스템

### 전제조건
- 유저가 마스토돈에 답글 작성
- 해당 유저가 DB에 없음

### 기본 흐름
1. 봇이 Streaming API로 답글 이벤트 수신
2. 마스토돈 API에서 유저 정보 조회 (id, username, display_name)
3. users 테이블에 INSERT
   ```sql
   INSERT INTO users (mastodon_id, username, display_name, role, balance)
   VALUES ('115565546282398331', 'user1', '유저1', 'user', 0);
   ```
4. 로그 기록

### 후행조건
- users 테이블에 신규 유저 등록됨
- balance = 0

---

## UC-02: 답글 작성 → 재화 지급

### 액터
- 일반 유저
- 재화봇

### 전제조건
- 유저가 DB에 등록되어 있음
- settings에 `replies_per_reward=1`, `reward_amount=10` 설정됨

### 기본 흐름
1. 유저가 마스토돈에서 답글 작성
2. 재화봇이 Streaming API로 답글 이벤트 수신
   - notification type: mention 또는 답글
3. **중복 체크**: transactions 테이블에서 status_id 조회
   ```sql
   SELECT COUNT(*) FROM transactions WHERE status_id = '115567956961536330';
   ```
   - 결과 > 0이면 중복 → 종료
4. 재화 계산
   - 답글 1개 → 10원
5. 트랜잭션 시작
   ```sql
   BEGIN TRANSACTION;

   -- 재화 지급
   UPDATE users
   SET balance = balance + 10,
       total_earned = total_earned + 10
   WHERE mastodon_id = '115565546282398331';

   -- 거래 기록
   INSERT INTO transactions
   (user_id, transaction_type, amount, status_id, description)
   VALUES
   ('115565546282398331', 'earn_reply', 10, '115567956961536330', '답글 작성 보상');

   COMMIT;
   ```
6. Redis 캐시 무효화 (선택)

### 대안 흐름
**2-1. 중복 답글**
- status_id가 이미 존재하면 지급하지 않음
- 로그만 기록 (중복 시도)

**5-1. 트랜잭션 실패**
- ROLLBACK
- 에러 로그 기록
- 재시도 큐에 등록 (선택)

### 후행조건
- users.balance += 10
- users.total_earned += 10
- transactions 테이블에 기록 추가
- 중복 답글은 처리 안 됨

---

## UC-03: 출석 체크 - 자동 트윗 발행

### 액터
- Celery 스케줄러
- 재화봇

### 전제조건
- 현재 시각: 매일 오전 10시 (Asia/Seoul)
- settings에 `attendance_time=10:00`, `attendance_enabled=true`

### 기본 흐름
1. Celery Beat가 매일 10시(서울 시간)에 태스크 실행
2. **전역 휴식기간 체크**
   ```sql
   SELECT COUNT(*) FROM calendar_events
   WHERE event_date = DATE('now', 'localtime')
   AND is_global_vacation = 1;
   ```
   - 결과 > 0이면 **출석 트윗 발행 안 함** → 종료
3. 출석 트윗 작성
   ```python
   status = mastodon.status_post(
       "🌟 오늘의 출석 체크!\n이 트윗에 답글 달아주세요!",
       visibility="public"
   )
   ```
4. attendance_posts 테이블에 기록
   ```sql
   INSERT INTO attendance_posts (post_id, posted_at, expires_at)
   VALUES (
       '115568000000000001',
       CURRENT_TIMESTAMP,
       DATETIME(CURRENT_TIMESTAMP, '+23 hours 59 minutes')
   );
   ```

### 대안 흐름
**2-1. 전역 휴식기간**
- is_global_vacation=true인 날짜
- 출석 트윗 발행 안 함
- 로그: "전역 휴식기간으로 출석 트윗 발행 건너뜀"

**3-1. 마스토돈 API 오류**
- 재시도 (최대 3회)
- 실패 시 알림 (관리자 DM 또는 로그)

### 후행조건
- attendance_posts 테이블에 금일 출석 트윗 기록
- 마스토돈에 공개 툿 게시됨

---

## UC-04: 출석 체크 - 유저 답글 처리

### 액터
- 일반 유저
- 재화봇

### 전제조건
- 출석 트윗이 발행되어 있음 (UC-03 완료)
- 유저가 DB에 등록되어 있음
- settings에 출석 보상 설정되어 있음
  - `attendance_base_reward=50`
  - `attendance_streak_7=20`
  - `attendance_streak_14=50`
  - `attendance_streak_30=100`

### 기본 흐름
1. 유저가 출석 트윗에 답글 작성
2. 재화봇이 Streaming API로 답글 이벤트 수신
3. **출석 트윗 확인**
   ```sql
   SELECT post_id FROM attendance_posts
   WHERE post_id = '115568000000000001'
   AND expires_at > CURRENT_TIMESTAMP;
   ```
   - 결과 없으면 → 만료된 출석 트윗 → 종료
4. **중복 체크**
   ```sql
   SELECT COUNT(*) FROM attendances
   WHERE user_id = '115565546282398331'
   AND attendance_post_id = '115568000000000001';
   ```
   - 결과 > 0이면 → 이미 출석함 → 종료 (UNIQUE 제약으로도 방지)
5. **연속 출석 계산**
   ```sql
   -- 어제 출석 기록 확인
   SELECT streak_days FROM attendances
   WHERE user_id = '115565546282398331'
   AND DATE(attended_at) = DATE('now', '-1 day', 'localtime')
   ORDER BY attended_at DESC LIMIT 1;
   ```
   - 어제 출석 있으면: `streak_days = 어제_streak + 1`
   - 어제 출석 없으면: `streak_days = 1`
6. **보상 계산**
   - 기본: 50원
   - 연속 7일: +20원
   - 연속 14일: +50원
   - 연속 30일: +100원
   ```python
   reward = 50
   if streak_days >= 30:
       reward += 100
   elif streak_days >= 14:
       reward += 50
   elif streak_days >= 7:
       reward += 20
   ```
7. **트랜잭션 처리**
   ```sql
   BEGIN TRANSACTION;

   -- 재화 지급
   UPDATE users
   SET balance = balance + 70,
       total_earned = total_earned + 70
   WHERE mastodon_id = '115565546282398331';

   -- 출석 기록
   INSERT INTO attendances
   (user_id, attendance_post_id, attended_at, reward_amount, streak_days)
   VALUES
   ('115565546282398331', '115568000000000001', CURRENT_TIMESTAMP, 70, 7);

   -- 출석 인원 증가
   UPDATE attendance_posts
   SET total_attendees = total_attendees + 1
   WHERE post_id = '115568000000000001';

   COMMIT;
   ```

### 대안 흐름
**3-1. 만료된 출석 트윗**
- expires_at < 현재 시각
- 처리 안 함, 유저에게 DM: "출석 시간이 지났습니다"

**4-1. 중복 출석 시도**
- UNIQUE 제약 위반 → SQLite 에러
- 또는 SELECT COUNT 체크에서 걸림
- 유저에게 DM: "이미 출석하셨습니다"

**5-1. 연속 출석 끊김**
- 어제 출석 기록 없음
- streak_days = 1 (초기화)

### 후행조건
- attendances 테이블에 출석 기록 추가
- users.balance 증가
- attendance_posts.total_attendees 증가
- 중복 출석 방지됨 (UNIQUE 제약)

---

## UC-05: 활동량 체크 (자동)

### 액터
- Celery 스케줄러
- 관리자 봇

### 전제조건
- 현재 시각: 오전 4시 또는 오후 4시 (Asia/Seoul)
- settings에 `check_times=04:00,16:00`, `activity_check_enabled=true`
- settings에 `check_period_hours=48`, `min_replies_48h=20`

### 기본 흐름
1. Celery Beat가 4시/16시(서울 시간)에 태스크 실행
2. **전역 휴식기간 체크**
   ```sql
   SELECT COUNT(*) FROM calendar_events
   WHERE event_date = DATE('now', 'localtime')
   AND is_global_vacation = 1;
   ```
   - 결과 > 0이면 **활동량 체크 건너뜀** → 종료
3. **체크 대상 유저 조회** (role=user, 휴식 중 아님)
   ```sql
   SELECT u.mastodon_id, u.username
   FROM users u
   WHERE u.role = 'user'
   AND NOT EXISTS (
       SELECT 1 FROM vacation v
       WHERE v.user_id = u.mastodon_id
       AND DATE('now', 'localtime') BETWEEN v.start_date AND v.end_date
   );
   ```
4. **각 유저별 48시간 답글 수 조회** (PostgreSQL)
   ```sql
   SELECT COUNT(*) as reply_count
   FROM statuses
   WHERE account_id = '115565546282398331'
   AND in_reply_to_id IS NOT NULL
   AND created_at > NOW() - INTERVAL '48 hours';
   ```
5. **기준 미달 유저 처리**
   - reply_count < 20인 유저
   ```sql
   -- 경고 기록
   INSERT INTO warnings
   (user_id, warning_type, check_period_hours, required_replies, actual_replies, message, dm_sent)
   VALUES
   ('115565546282398331', 'auto', 48, 20, 15, '활동량 기준 미달', 1);
   ```
6. **관리자 봇으로 DM 발송**
   ```python
   mastodon.status_post(
       f"@{username} 활동량 체크 결과\n48시간 내 답글: {reply_count}개 (기준: 20개)",
       visibility="direct"
   )
   ```
7. SQLite DB에 체크 시각 기록
   ```sql
   UPDATE users
   SET last_check = CURRENT_TIMESTAMP
   WHERE mastodon_id = '115565546282398331';
   ```

### 대안 흐름
**2-1. 전역 휴식기간**
- 활동량 체크 건너뜀
- 로그: "전역 휴식기간으로 활동량 체크 건너뜀"

**3-1. 휴식 중인 유저**
- vacation 테이블에 해당 날짜 포함된 기록 있음
- 체크 대상에서 제외
- 로그: "휴식 중인 유저 제외: {username}"

**4-1. PostgreSQL 연결 실패**
- 재시도 (최대 3회)
- 실패 시 관리자에게 알림
- 다음 체크 시간까지 대기

**6-1. DM 발송 실패**
- 마스토돈 API 오류
- warnings.dm_sent = 0으로 기록
- 재시도 큐에 등록

### 후행조건
- warnings 테이블에 경고 기록 추가
- 기준 미달 유저에게 DM 발송됨
- users.last_check 업데이트됨
- 휴식 중/전역 휴식기간에는 체크 안 됨

---

## UC-06: 휴식 신청

### 액터
- 일반 유저
- 관리자

### 전제조건
- 유저가 관리자에게 휴식 신청 (마스토돈 DM 또는 웹)

### 기본 흐름 (관리자 웹)
1. 관리자가 관리자 웹 로그인
2. "활동량 관리" → "휴식 신청 목록" 메뉴
3. "새 휴식 등록" 버튼 클릭
4. 폼 입력
   - 유저: 드롭다운에서 선택
   - 시작일: 2025-11-20
   - 종료일: 2025-11-25
   - 사유: 여행
5. "등록" 버튼 클릭
6. DB 저장
   ```sql
   INSERT INTO vacation (user_id, start_date, end_date, reason, registered_by)
   VALUES ('115565546282398331', '2025-11-20', '2025-11-25', '여행', 'admin_user');
   ```
7. 관리 로그 기록
   ```sql
   INSERT INTO admin_logs (admin_name, action_type, target_user, details)
   VALUES ('admin_user', 'register_vacation', '115565546282398331', '2025-11-20 ~ 2025-11-25: 여행');
   ```

### 후행조건
- vacation 테이블에 휴식 기간 등록됨
- 해당 기간 동안 활동량 체크 제외됨 (UC-05의 3-1)

---

## UC-07: 전역 휴식기간 설정

### 액터
- 관리자

### 전제조건
- 관리자 웹에 로그인됨

### 기본 흐름
1. 관리자가 "일정/이벤트 관리" 메뉴 클릭
2. "새 일정 등록" 버튼 클릭
3. 폼 입력
   - 제목: 크리스마스 휴식기간
   - 설명: 연말 커뮤니티 휴식
   - 날짜: 2025-12-25
   - 타입: holiday
   - **전역 휴식기간 체크박스: ✅**
4. "저장" 버튼 클릭
5. DB 저장
   ```sql
   INSERT INTO calendar_events
   (title, description, event_date, event_type, is_global_vacation, created_by)
   VALUES
   ('크리스마스 휴식기간', '연말 커뮤니티 휴식', '2025-12-25', 'holiday', 1, 'admin_user');
   ```
6. 관리 로그 기록
   ```sql
   INSERT INTO admin_logs (admin_name, action_type, details)
   VALUES ('admin_user', 'add_event', '전역 휴식기간 설정: 2025-12-25');
   ```

### 후행조건
- calendar_events 테이블에 휴식기간 등록됨
- 2025-12-25에는:
  - 출석 트윗 발행 안 됨 (UC-03의 2-1)
  - 활동량 체크 안 됨 (UC-05의 2-1)

---

## UC-08: 일정 조회 (봇 명령어)

### 액터
- 일반 유저

### 전제조건
- calendar_events 테이블에 일정이 등록되어 있음

### 기본 흐름
1. 유저가 마스토돈에서 `@봇 일정` 멘션
2. 봇이 멘션 이벤트 수신
3. **이번 주 일정 조회** (오늘 ~ 7일 이내)
   ```sql
   SELECT title, event_date, event_type, is_global_vacation
   FROM calendar_events
   WHERE event_date BETWEEN DATE('now', 'localtime')
                        AND DATE('now', '+7 days', 'localtime')
   ORDER BY event_date ASC;
   ```
4. 응답 메시지 생성
   ```
   📅 이번 주 일정

   11/20 (수) 🎉 커뮤니티 모임
   11/25 (월) 🏖️ 전역 휴식기간

   * 전역 휴식기간에는 출석/활동량 체크가 없습니다.
   ```
5. 유저에게 DM 또는 멘션 답글로 응답

### 대안 흐름
**3-1. 일정 없음**
- 응답: "이번 주 등록된 일정이 없습니다."

**1-1. 다른 명령어**
- `@봇 일정 이번달`: 이번 달 전체 조회
- `@봇 일정 다음주`: 7~14일 이내 조회

### 후행조건
- 유저가 일정을 확인함
- 전역 휴식기간을 인지함

---

## UC-09: 관리자 재화 조정

### 액터
- 관리자

### 전제조건
- 관리자 웹에 로그인됨
- 조정할 유저가 존재함

### 기본 흐름
1. 관리자가 "유저 관리" → "유저 목록" 메뉴
2. 특정 유저 클릭 → "재화 조정" 버튼
3. 폼 입력
   - 조정 금액: +100 (또는 -50)
   - 사유: 이벤트 보상
4. "확인" 버튼 클릭
5. **트랜잭션 처리**
   ```sql
   BEGIN TRANSACTION;

   -- 재화 조정
   UPDATE users
   SET balance = balance + 100,
       total_earned = total_earned + 100  -- 증가 시
   WHERE mastodon_id = '115565546282398331';

   -- 거래 기록
   INSERT INTO transactions
   (user_id, transaction_type, amount, description, admin_name)
   VALUES
   ('115565546282398331', 'admin_add', 100, '이벤트 보상', 'admin_user');

   -- 관리 로그
   INSERT INTO admin_logs
   (admin_name, action_type, target_user, details)
   VALUES
   ('admin_user', 'adjust_balance', '115565546282398331', '+100: 이벤트 보상');

   COMMIT;
   ```
6. 성공 메시지 표시

### 대안 흐름
**3-1. 재화 차감**
- 조정 금액: -50
- `total_spent += 50` (차감 시)
- `transaction_type = 'admin_deduct'`

**5-1. 잔액 부족 (차감 시)**
- balance + 조정금액 < 0
- 에러 메시지: "재화가 부족합니다"
- ROLLBACK

### 후행조건
- users.balance 조정됨
- transactions 테이블에 기록 추가
- admin_logs에 관리 로그 추가

---

## 데이터 흐름 요약

### 재화 증가 경로
1. 답글 작성 (UC-02) → `earn_reply`
2. 출석 체크 (UC-04) → `attendance`
3. 관리자 조정 (UC-09) → `admin_add`

### 재화 감소 경로
1. 상점 구매 (Phase 5+) → `spend_shop`
2. 관리자 조정 (UC-09) → `admin_deduct`

### 활동량 제외 경로
1. 개인 휴식 (UC-06) → vacation 테이블
2. 전역 휴식기간 (UC-07) → calendar_events.is_global_vacation
3. role != 'user' → users.role

---

## 검증 포인트

### 중복 방지
- ✅ 답글 재화 지급: status_id (애플리케이션 레벨)
- ✅ 출석 중복: UNIQUE(user_id, attendance_post_id) (DB 레벨)
- ✅ 출석 트윗: post_id UNIQUE (DB 레벨)

### 타임존
- ✅ 모든 시간 기준: Asia/Seoul
- ✅ Celery Beat 스케줄: 서울 시간
- ✅ SQLite: `DATE('now', 'localtime')`

### 전역 휴식기간
- ✅ 출석 트윗 발행 막음 (UC-03)
- ✅ 활동량 체크 건너뜀 (UC-05)
- ✅ calendar_events.is_global_vacation=1

### 트랜잭션 무결성
- ✅ 재화 조정 시 BEGIN/COMMIT
- ✅ ROLLBACK 처리 (실패 시)
- ✅ FK 제약 (users, attendance_posts)

---

---

## UC-10: 소셜 분석 - 편중/고립 유저 탐지 (새벽 4시)

### 액터
- Celery 스케줄러
- 관리자 봇 (경고 발송)

### 전제조건
- 현재 시각: 새벽 4시 (Asia/Seoul)
- PostgreSQL 연결 가능
- settings에 분석 기준 설정되어 있음

### 기본 흐름

#### 1. 대화 상대 분석 (PostgreSQL)
```sql
-- 유저별 48시간 내 대화 패턴 분석
WITH user_conversations AS (
    SELECT
        s.account_id as user_id,
        s.in_reply_to_account_id as partner_id,
        COUNT(*) as reply_count
    FROM statuses s
    WHERE s.in_reply_to_id IS NOT NULL
      AND s.created_at > NOW() - INTERVAL '48 hours'
    GROUP BY s.account_id, s.in_reply_to_account_id
),
user_totals AS (
    SELECT
        account_id as user_id,
        COUNT(DISTINCT in_reply_to_account_id) as unique_partners,
        COUNT(*) as total_replies
    FROM statuses
    WHERE in_reply_to_id IS NOT NULL
      AND created_at > NOW() - INTERVAL '48 hours'
    GROUP BY account_id
),
top_partners AS (
    SELECT DISTINCT ON (user_id)
        user_id,
        partner_id as top_partner_id,
        reply_count as top_partner_count
    FROM user_conversations
    ORDER BY user_id, reply_count DESC
)
SELECT
    t.user_id,
    t.unique_partners,
    t.total_replies,
    tp.top_partner_id,
    tp.top_partner_count,
    ROUND(tp.top_partner_count::REAL / t.total_replies, 2) as top_partner_ratio
FROM user_totals t
LEFT JOIN top_partners tp ON t.user_id = tp.user_id;
```

#### 2. 접속률 분석 (PostgreSQL)
```sql
SELECT
    account_id as user_id,
    COUNT(DISTINCT DATE(created_at)) as active_days
FROM statuses
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY account_id;
```

#### 3. 마스토돈 username 조회
```sql
SELECT id, username FROM accounts WHERE id IN (...);
```

#### 4. SQLite에 통계 저장
```sql
INSERT INTO user_stats
(user_id, analyzed_at, unique_conversation_partners, total_replies_sent,
 top_partner_id, top_partner_username, top_partner_count, top_partner_ratio,
 active_days_7d, login_rate_7d, is_isolated, is_inactive, is_biased)
VALUES
('115565546282398331', CURRENT_TIMESTAMP, 2, 25,
 '115565546282398332', 'user2', 20, 0.80,
 6, 0.86, 1, 0, 1);
```

#### 5. 문제 유저 판정
```python
is_isolated = unique_partners < 7
is_inactive = login_rate_7d < 0.5
is_biased = top_partner_ratio > 0.3
```

#### 6. 자동 경고 발송 (편중 유저만)
```sql
-- 경고 기록
INSERT INTO warnings
(user_id, warning_type, message, dm_sent, admin_name)
VALUES
('115565546282398331', 'social_bias',
 '특정 계정과의 대화 편중 (40%)', 1, 'system');
```

```python
# 편중 유저에게만 자동 DM 발송
if is_biased:
    mastodon.status_post(
        f"""@{username} 커뮤니티 참여 안내

최근 48시간 대화 분석 결과:
- 전체 답글: {total_replies}개
- 대화 상대: {unique_partners}명
- @{top_partner_username}와의 대화: {top_partner_count}개 ({int(top_partner_ratio*100)}%)

⚠️ 특정 계정과의 대화가 30% 이상입니다.
다양한 커뮤니티 멤버와 소통해보세요!""",
        visibility="direct"
    )
```

**고립/비활동 유저는 자동 DM 발송 안 함:**
- user_stats 테이블에만 기록 (is_isolated, is_inactive)
- 관리자 웹에서 목록 조회 가능
- 관리자가 수동으로 판단 후 경고 발송 (UC-12)

### 대안 흐름

**1-1. PostgreSQL 연결 실패**
- 재시도 (최대 3회)
- 실패 시 관리자에게 알림
- 다음 날까지 대기

**5-1. 전역 휴식기간**
- 분석은 실행하되 경고 발송 안 함
- user_stats에는 저장 (히스토리 유지)

**6-1. 복합 문제 (고립 + 편중)**
- is_isolated=1, is_biased=1
- DM 메시지 조정: "대화 상대가 적고, 특정 계정과만 대화 중"

**6-2. DM 발송 실패**
- warnings.dm_sent = 0
- 재시도 큐에 등록

### 후행조건
- user_stats 테이블에 금일 분석 결과 저장
- 편중 유저에게 경고 DM 발송됨
- warnings 테이블에 경고 기록 추가
- 관리자 웹에서 문제 유저 목록 조회 가능

---

## UC-11: 관리자 웹 - 편중 유저 목록 조회

### 액터
- 관리자

### 전제조건
- 관리자 웹에 로그인됨
- user_stats 데이터가 존재함

### 기본 흐름
1. 관리자가 "커뮤니티 건강도" 메뉴 클릭
2. 대시보드에 요약 표시
   ```
   ┌─────────────────────────────┐
   │ 커뮤니티 건강도             │
   ├─────────────────────────────┤
   │ 🔴 대화 편중 유저: 3명      │
   │ 🟡 고립 위험 유저: 5명      │
   │ 🟢 건강한 유저: 42명        │
   └─────────────────────────────┘
   ```
3. "대화 편중 유저" 클릭
4. 편중 유저 목록 조회 (최근 분석 결과)
   ```sql
   SELECT
       us.user_id,
       u.username,
       us.unique_conversation_partners,
       us.top_partner_username,
       us.top_partner_ratio,
       us.analyzed_at
   FROM user_stats us
   JOIN users u ON us.user_id = u.mastodon_id
   WHERE us.is_biased = 1
     AND DATE(us.analyzed_at) = DATE('now', 'localtime')
   ORDER BY us.top_partner_ratio DESC;
   ```
5. 목록 표시
   ```
   [대화 편중 유저 (5명)]

   @user1  대화 상대: 6명 | @user2와 40% (20/50개)
   @user3  대화 상대: 4명 | @user4와 50% (15/30개) ⚠️
   @user5  대화 상대: 5명 | @user6와 35% (14/40개)
   @user7  대화 상대: 8명 | @user8와 32% (16/50개)
   @user9  대화 상대: 3명 | @user10와 60% (12/20개) 🔴
   ```
6. 특정 유저 클릭 → 상세 페이지
   ```
   [user1 상세]

   소셜 통계 (최근 48시간)
   - 대화 상대: 6명
   - 총 답글: 50개
   - 최다 대화: @user2 (20회, 40%) ⚠️

   접속 패턴 (최근 7일)
   - 활동 일수: 6일
   - 접속률: 85.7%

   경고 이력
   - 2025-11-18 04:00 대화 편중 경고 발송
   ```

### 대안 흐름
**4-1. 편중 유저 없음**
- 메시지: "현재 대화 편중 유저가 없습니다 ✅"

### 후행조건
- 관리자가 문제 유저 현황 파악
- 필요 시 수동 조치 가능 (휴식 등록, 재화 조정 등)

---

## UC-12: 관리자 웹 - 수동 경고 발송

### 액터
- 관리자

### 전제조건
- 관리자 웹에 로그인됨
- 경고 발송 대상 유저 존재

### 기본 흐름 (유저 상세 페이지에서)
1. 관리자가 "커뮤니티 건강도" → "고립 유저 목록" 클릭
2. 특정 유저 클릭 → 상세 페이지
3. 유저 소셜 통계 확인
   - 대화 상대: 5명
   - 총 답글: 18개
   - 접속률: 42%
4. "경고 발송" 버튼 클릭
5. 경고 발송 폼 표시
   - 경고 유형: 드롭다운 (활동량 미달/고립 위험/비활동/기타)
   - 메시지: 텍스트 영역 (기본 템플릿 제공)
   - 발송 방식: 체크박스 (DM 발송/관리자만 기록)
6. 폼 입력
   ```
   경고 유형: 고립 위험
   메시지:
   안녕하세요 @user3님,

   최근 48시간 대화 분석 결과 대화 상대가 5명으로 적습니다.
   다양한 커뮤니티 멤버와 소통해보시는 건 어떨까요?

   - 커뮤니티 이벤트 참여하기
   - 새로운 주제 대화방 둘러보기

   ✅ DM 발송
   ```
7. "발송" 버튼 클릭
8. **트랜잭션 처리**
   ```sql
   BEGIN TRANSACTION;

   -- 경고 기록
   INSERT INTO warnings
   (user_id, warning_type, message, dm_sent, admin_name)
   VALUES
   ('115565546282398333', 'isolation',
    '대화 상대 5명으로 적음. 다양한 소통 권장', 1, 'admin_user');

   -- 관리 로그
   INSERT INTO admin_logs
   (admin_name, action_type, target_user, details)
   VALUES
   ('admin_user', 'send_warning', '115565546282398333',
    '고립 위험 경고 발송 (수동)');

   COMMIT;
   ```
9. 관리자 봇으로 DM 발송
   ```python
   mastodon.status_post(
       f"@{username} {message}",
       visibility="direct"
   )
   ```
10. 성공 메시지 표시: "경고가 발송되었습니다"

### 기본 흐름 (일괄 발송)
1. 관리자가 "고립 유저 목록" 페이지
2. 유저 체크박스 선택 (복수 선택 가능)
3. "일괄 경고 발송" 버튼 클릭
4. 일괄 발송 폼
   - 경고 유형: 고립 위험
   - 메시지 템플릿 (변수 사용 가능: {username}, {unique_partners} 등)
5. "발송" 버튼 클릭
6. 선택된 유저들에게 순차적으로 발송

### 대안 흐름
**6-1. 메시지 템플릿 선택**
- 사전 정의된 템플릿 선택
  - 활동량 미달 템플릿
  - 고립 위험 템플릿
  - 비활동 템플릿
- 커스텀 메시지 작성

**9-1. DM 발송 실패**
- warnings.dm_sent = 0
- 에러 메시지 표시
- 재시도 옵션 제공

**9-2. DM 발송 안 함 (관리자만 기록)**
- DM 체크박스 해제 시
- DB에만 기록 (warnings.dm_sent = 0)
- 관리 로그에 "경고 기록 (DM 미발송)" 표시

### 후행조건
- warnings 테이블에 경고 기록 추가
- admin_logs에 관리 로그 추가
- 선택 시 유저에게 DM 발송됨

---

## UC-13: 관리자 웹 - 경고 발송 페이지 (통합)

### 액터
- 관리자

### 전제조건
- 관리자 웹에 로그인됨

### 기본 흐름
1. 관리자가 "경고 발송" 메뉴 클릭
2. 경고 발송 통합 페이지 표시
   ```
   ┌─────────────────────────────────────┐
   │ 경고 발송                           │
   ├─────────────────────────────────────┤
   │ [유저 검색]                         │
   │ username: ___________  [검색]       │
   │                                     │
   │ 또는 문제 유저 빠른 선택:           │
   │ • 편중 유저 (3명) [보기]            │
   │ • 고립 유저 (5명) [보기]            │
   │ • 비활동 유저 (2명) [보기]          │
   │ • 활동량 미달 (7명) [보기]          │
   └─────────────────────────────────────┘
   ```
3. "고립 유저 (5명)" 클릭
4. 고립 유저 목록 표시 (체크박스 포함)
5. 유저 선택 후 "경고 발송" 버튼
6. 경고 발송 폼 (UC-12와 동일)
7. 발송 처리

### 템플릿 관리
```sql
CREATE TABLE warning_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    warning_type TEXT NOT NULL,
    template TEXT NOT NULL,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 기본 템플릿
INSERT INTO warning_templates (name, warning_type, template) VALUES
('활동량 미달 기본', 'activity',
 '@{username}님, 최근 48시간 답글이 {actual_replies}개로 기준({required_replies}개)에 미달했습니다.'),
('고립 위험 기본', 'isolation',
 '@{username}님, 최근 대화 상대가 {unique_partners}명으로 적습니다. 다양한 멤버와 소통해보세요!'),
('비활동 기본', 'inactive',
 '@{username}님, 최근 7일 접속률이 {login_rate}%입니다. 커뮤니티 활동에 관심 부탁드립니다.');
```

### 후행조건
- 선택된 유저들에게 경고 발송됨
- warnings, admin_logs 기록됨

---

## UC-14: 관리자 웹 - 수동 밴 (유저 차단)

### 액터
- 관리자

### 전제조건
- 관리자 웹에 로그인됨
- 밴 대상 유저가 존재함
- 밴 사유가 명확함

### 기본 흐름
1. 관리자가 "밴 관리" 메뉴 클릭
2. "유저 밴 실행" 버튼 클릭
3. 유저 검색 폼
   - 검색 방식: username 또는 mastodon_id
   - 또는 문제 유저 빠른 선택 (경고 3회 이상 유저 목록 등)
4. 유저 선택 후 유저 정보 확인
   ```
   [선택된 유저]
   username: user1
   display_name: 유저1
   경고 횟수: 3회
   최근 경고: 2025-11-17 (대화 편중)
   ```
5. **증거물 자동 수집** (백그라운드)
   ```python
   # 경고 이력 조회
   warnings_query = """
   SELECT id, warning_type, message, timestamp, dm_sent
   FROM warnings
   WHERE user_id = ?
   ORDER BY timestamp DESC
   """

   # 최신 소셜 통계 조회
   stats_query = """
   SELECT *
   FROM user_stats
   WHERE user_id = ?
   ORDER BY analyzed_at DESC
   LIMIT 1
   """

   # JSON 증거물 생성
   evidence = {
       "user_info": {
           "username": username,
           "mastodon_id": user_id,
           "role": role,
           "banned_at": datetime.now().isoformat()
       },
       "warning_history": warning_records,
       "latest_stats": stats_record
   }
   ```
6. 밴 실행 폼 입력
   - 밴 사유: (필수) 텍스트 영역
     - 예: "반복적인 대화 편중 경고 무시 (3회), 커뮤니티 참여 불성실"
   - 자동 수집된 증거물 요약 표시
     ```
     [자동 수집된 증거물]
     • 경고 이력: 3건
       - 2025-11-15: 대화 편중 (편중률 80%)
       - 2025-11-16: 활동량 미달 (15/20개)
       - 2025-11-17: 대화 편중 (편중률 85%)
     • 최근 통계 (2025-11-18 04:00)
       - 대화 상대: 2명 (고립)
       - 편중률: 80% (편중)
       - 접속률: 42% (비활동)
     ```
7. "밴 실행" 버튼 클릭
8. **확인 팝업**
   ```
   정말로 @user1 유저를 밴하시겠습니까?

   사유: 반복적인 대화 편중 경고 무시 (3회), 커뮤니티 참여 불성실

   • 이 작업은 취소할 수 없습니다 (언밴은 가능)
   • 모든 증거물이 영구 보존됩니다

   [취소] [밴 실행]
   ```
9. "밴 실행" 확인
10. **트랜잭션 처리**
    ```sql
    BEGIN TRANSACTION;

    -- 밴 기록
    INSERT INTO ban_records
    (user_id, banned_at, banned_by, reason, warning_count, evidence_snapshot, is_active)
    VALUES
    ('115565546282398331',
     CURRENT_TIMESTAMP,
     'admin_user',
     '반복적인 대화 편중 경고 무시 (3회), 커뮤니티 참여 불성실',
     3,
     '{"user_info": {...}, "warning_history": [...], "latest_stats": {...}}',
     1);

    -- 관리 로그
    INSERT INTO admin_logs
    (admin_name, action_type, target_user, details)
    VALUES
    ('admin_user', 'ban_user', '115565546282398331',
     '밴 사유: 반복적인 대화 편중 경고 무시 (3회)');

    COMMIT;
    ```
11. **마스토돈에서 계정 차단** (선택 - 관리자 판단)
    ```python
    # 마스토돈 API 호출 (관리자 권한 필요)
    mastodon.account_mute(account_id)  # 또는 account_block()
    ```
12. 성공 메시지 표시
    ```
    ✅ @user1 유저가 밴되었습니다.
    • 밴 ID: 42
    • 증거물이 영구 보존되었습니다.
    • 밴 목록에서 확인할 수 있습니다.
    ```

### 대안 흐름

**3-1. 경고 3회 이상 유저 빠른 선택**
- 경고 횟수 ≥ 3회 유저 목록 표시
- 클릭하면 자동으로 해당 유저 선택

**11-1. 마스토돈 차단 실패**
- DB에는 밴 기록 저장됨
- 관리자에게 알림: "마스토돈 차단 실패, 수동 처리 필요"

**11-2. 마스토돈 차단 안 함**
- DB에만 기록 (경고 목적)
- 실제 차단은 관리자가 수동으로 마스토돈에서 처리

### 후행조건
- ban_records 테이블에 밴 기록 추가
- evidence_snapshot에 증거물 JSON 영구 저장
- admin_logs에 관리 로그 추가
- (선택) 마스토돈에서 계정 차단됨

---

## UC-15: 관리자 웹 - 밴 목록 및 언밴

### 액터
- 관리자

### 전제조건
- 관리자 웹에 로그인됨
- ban_records 데이터가 존재함

### 기본 흐름
1. 관리자가 "밴 관리" → "밴 목록" 클릭
2. 밴 유저 목록 조회
   ```sql
   SELECT
       br.id,
       br.user_id,
       u.username,
       br.banned_at,
       br.banned_by,
       br.reason,
       br.warning_count,
       br.is_active
   FROM ban_records br
   JOIN users u ON br.user_id = u.mastodon_id
   WHERE br.is_active = 1
   ORDER BY br.banned_at DESC;
   ```
3. 목록 표시
   ```
   [밴 유저 목록 (5명)]

   • @user1
     밴 일시: 2025-11-18 10:30
     관리자: admin_user
     사유: 반복적인 대화 편중 경고 무시 (3회)
     경고 횟수: 3회
     [증거물 보기] [언밴]

   • @user2
     밴 일시: 2025-11-17 15:20
     관리자: admin_user2
     사유: 커뮤니티 규칙 위반
     경고 횟수: 5회
     [증거물 보기] [언밴]
   ```
4. 필터 옵션
   - 활성 밴 / 해제된 밴 (is_active)
   - 날짜 범위
   - 관리자별

### 증거물 조회
1. "증거물 보기" 버튼 클릭
2. 모달 팝업에 JSON 포맷팅 표시
   ```json
   {
     "user_info": {
       "username": "user1",
       "mastodon_id": "115565546282398331",
       "role": "user",
       "banned_at": "2025-11-18 10:30:00"
     },
     "warning_history": [
       {
         "id": 1,
         "warning_type": "social_bias",
         "message": "편중 경고",
         "timestamp": "2025-11-15 04:00:00",
         "dm_sent": 0
       },
       {
         "id": 2,
         "warning_type": "activity",
         "message": "활동량 미달",
         "timestamp": "2025-11-16 04:00:00",
         "dm_sent": 0
       },
       {
         "id": 3,
         "warning_type": "social_bias",
         "message": "편중 경고",
         "timestamp": "2025-11-17 04:00:00",
         "dm_sent": 0
       }
     ],
     "latest_stats": {
       "unique_partners": 2,
       "total_replies": 25,
       "top_partner_ratio": 0.8,
       "active_days_7d": 3,
       "login_rate": 0.42,
       "is_isolated": 1,
       "is_biased": 1,
       "is_inactive": 1
     }
   }
   ```
3. 다운로드 버튼 (JSON 파일로 저장 가능)

### 언밴 (밴 해제)
1. "언밴" 버튼 클릭
2. 언밴 폼 표시
   - 언밴 사유: (필수) 텍스트 영역
     - 예: "경고 기간 경과 후 태도 개선 확인, 재기회 부여"
3. "언밴 실행" 버튼 클릭
4. **확인 팝업**
   ```
   @user1 유저를 언밴하시겠습니까?

   사유: 경고 기간 경과 후 태도 개선 확인, 재기회 부여

   • 밴 기록은 영구 보존됩니다
   • 유저는 정상 활동이 가능합니다

   [취소] [언밴]
   ```
5. **트랜잭션 처리**
   ```sql
   BEGIN TRANSACTION;

   -- 밴 해제
   UPDATE ban_records
   SET is_active = 0,
       unbanned_at = CURRENT_TIMESTAMP,
       unbanned_by = 'admin_user',
       unban_reason = '경고 기간 경과 후 태도 개선 확인, 재기회 부여'
   WHERE id = 42;

   -- 관리 로그
   INSERT INTO admin_logs
   (admin_name, action_type, target_user, details)
   VALUES
   ('admin_user', 'unban_user', '115565546282398331',
    '언밴 사유: 경고 기간 경과 후 태도 개선 확인');

   COMMIT;
   ```
6. 성공 메시지: "언밴이 완료되었습니다"

### 후행조건
- ban_records.is_active = 0으로 변경
- unbanned_at, unbanned_by, unban_reason 기록됨
- admin_logs에 언밴 로그 추가
- 밴 기록은 영구 보존됨 (삭제 안 됨)

---

## 추가 검토 필요 사항

### 1. 연속 출석 계산 (UC-04)
- 자정 기준? 출석 트윗 발행 시각 기준?
- 예: 12/1 23:59 출석 → 12/2 00:01 출석 = 연속?
- **현재 설계**: DATE 기준 (자정 기준)

### 2. 만료된 출석 트윗 처리
- 23시간 59분 후 자동 만료
- 만료된 트윗에 답글 달면?
- **현재 설계**: 처리 안 함, DM 안내

### 3. PostgreSQL 답글 수 조회 성능
- 유저 100명 × 매일 2회 = 200 쿼리
- 벌크 조회 필요?
- **현재 설계**: 개별 쿼리 (추후 최적화)

### 4. 휴식 중 출석 가능?
- **현재 설계**: 가능 (활동량 체크와 별개)
- 변경 필요 여부?

### 5. CASCADE 동작
- attendance_posts 삭제 시 attendances도 삭제?
- **현재 설계**: FK 제약만, CASCADE 없음
- 추가 필요?
