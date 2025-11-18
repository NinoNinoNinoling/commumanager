# Use Cases

## UC-01: 팔로우 이벤트 기반 유저 등록

**액터**: Mastodon Streaming API, 재화봇
**트리거**: 유저가 관리자 계정 팔로우

**흐름**:
1. Streaming API에서 follow 이벤트 수신
2. 어드민 계정 팔로우인지 확인 (아니면 무시)
3. 중복 체크
   ```sql
   SELECT COUNT(*) FROM users WHERE mastodon_id = ?;
   ```
4. 신규 유저 등록
   ```sql
   INSERT INTO users (mastodon_id, username, display_name, currency, created_at)
   VALUES (?, ?, ?, 0, CURRENT_TIMESTAMP);
   ```
5. Redis 캐시 갱신 (1시간 TTL)
6. 로그 기록

**예외**:
- 중복: username/display_name 업데이트
- DB 실패: 에러 로그 + 관리자 알림 (KakaoTalk 봇 연동 검토 필요), 재시도 큐, Lazy Creation 백업

---

## UC-02: 답글 재화 일괄 정산

**액터**: Celery 스케줄러
**스케줄**: 매일 4시, 16시 (Asia/Seoul)

**흐름**:
1. 마지막 정산 시각 조회
   ```sql
   SELECT value FROM system_config WHERE key = 'last_reward_settlement_time';
   ```
2. PostgreSQL에서 유저별 답글 집계
   ```sql
   SELECT account_id, array_agg(id) as status_ids, COUNT(*) as reply_count
   FROM statuses
   WHERE in_reply_to_id IS NOT NULL
     AND created_at > ? AND created_at <= NOW()
   GROUP BY account_id;
   ```
3. 각 유저별 처리:
   - SQLite에서 이미 지급된 답글 확인 (transactions.related_id)
   - 미지급 답글만 필터링
   - 재화 계산: `(답글 수 / 100) * 10`
   - 재화 지급 + 거래 기록
4. 정산 시각 업데이트
   ```sql
   UPDATE system_config SET value = CURRENT_TIMESTAMP WHERE key = 'last_reward_settlement_time';
   ```

**예외**:
- PostgreSQL 연결 실패: 재시도 3회, 실패 시 다음 정산 시간에 재시도
- Lazy Creation: 유저 미등록 시 즉시 생성 + Redis 캐시

---

## UC-03: 출석 체크 - 자동 트윗 발행

**액터**: Celery 스케줄러, 재화봇
**스케줄**: 매일 10시 (Asia/Seoul)

**흐름**:
1. 전역 휴식기간 체크
   ```sql
   SELECT COUNT(*) FROM calendar_events
   WHERE event_date = DATE('now', 'localtime') AND is_global_vacation = 1;
   ```
   - 결과 > 0이면 종료
2. 최근 정산 시각 조회
   ```sql
   SELECT value FROM system_config WHERE key = 'last_reward_settlement_time';
   ```
3. 출석 트윗 발행
   ```python
   status = mastodon.status_post(
       f"""🌟 오늘의 출석 체크!
이 트윗에 답글 달아주세요!

💰 최근 정산 완료: {settlement_time}
재화 지급이 완료되었습니다.""",
       visibility="public"
   )
   ```
4. attendance_posts 기록
   ```sql
   INSERT INTO attendance_posts (post_id, posted_at, expires_at)
   VALUES (?, CURRENT_TIMESTAMP, DATETIME(CURRENT_TIMESTAMP, '+23 hours 59 minutes'));
   ```

**예외**:
- API 오류: 재시도 3회, 실패 시 로그

---

## UC-04: 출석 체크 - 유저 답글 처리

**액터**: Streaming API, 재화봇
**트리거**: 유저가 출석 트윗에 답글

**흐름**:
1. Streaming API에서 답글 이벤트 수신
2. 출석 트윗 확인
   ```sql
   SELECT post_id FROM attendance_posts
   WHERE post_id = ? AND expires_at > CURRENT_TIMESTAMP;
   ```
   - 결과 없으면 종료 (만료)
3. 트랜잭션 처리
   ```sql
   BEGIN TRANSACTION;
   
   UPDATE users SET currency = currency + 50 WHERE mastodon_id = ?;
   
   INSERT INTO attendances (user_id, attendance_post_id, attended_at, reward_amount)
   VALUES (?, ?, CURRENT_TIMESTAMP, 50);
   
   UPDATE attendance_posts SET total_attendees = total_attendees + 1 WHERE post_id = ?;
   
   COMMIT;
   ```

**예외**:
- 만료: 조용히 무시
- 중복: UNIQUE 제약 위반, ROLLBACK, 조용히 무시

---

## UC-05: 활동량 조회 (관리자 웹 전용)

**액터**: 관리자
**위치**: 개인별 분석 페이지

**흐름**:
1. 48시간 답글 수 조회 (PostgreSQL)
   ```sql
   SELECT COUNT(*) as reply_count FROM statuses
   WHERE account_id = ? AND in_reply_to_id IS NOT NULL
     AND created_at > NOW() - INTERVAL '48 hours';
   ```
2. 휴식 상태 확인 (SQLite)
   ```sql
   SELECT COUNT(*) FROM vacation
   WHERE user_id = ? AND DATE('now', 'localtime') BETWEEN start_date AND end_date;
   ```
3. 결과 표시
   - 🟢 정상: reply_count >= 20
   - 🔴 기준 미달: reply_count < 20
   - 💤 휴식 중

**참고**: 실시간 조회만, DB 저장 안 함, 자동 경고 없음

---

## UC-06: 휴식 관리 (봇 명령어)

**액터**: 일반 유저, 봇

### 흐름 1: 휴식 등록
1. `@봇 휴식 N` 멘션
2. 명령어 파싱
   ```python
   pattern = r'@봇\s+휴식\s+(\d+)'
   days = int(match.group(1))
   ```
3. 날짜 계산
   ```python
   start_date = date.today()
   end_date = start_date + timedelta(days=days-1)
   ```
4. 기존 휴식 체크
   ```sql
   SELECT COUNT(*) FROM vacation
   WHERE user_id = ? AND end_date >= DATE('now', 'localtime');
   ```
   - 이미 휴식 중이면 조용히 무시
5. 최대 일수 검증
   ```python
   max_days = int(get_setting('max_vacation_days'))
   if days <= 0 or days > max_days:
       # DM: "휴식 기간은 1~{max_days}일 사이여야 합니다."
   ```
6. 휴식 등록
   ```sql
   INSERT INTO vacation (user_id, start_date, start_time, end_date, end_time, reason, approved, registered_by)
   VALUES (?, ?, NULL, ?, NULL, '봇 자동 등록', 1, 'bot');
   ```
   - start_time, end_time = NULL (전일 00:00~23:59)
7. 확인 DM 발송
   ```python
   mastodon.status_post(
       f"@{username} 휴식이 등록되었습니다.\n기간: {start_date} ~ {end_date} ({days}일간)",
       visibility='direct'
   )
   ```

### 흐름 2: 휴식 해제
1. `@봇 휴식 해제` 멘션
2. 현재 휴식 조회
   ```sql
   SELECT id FROM vacation
   WHERE user_id = ? AND end_date >= DATE('now', 'localtime')
   ORDER BY end_date DESC LIMIT 1;
   ```
   - 없으면 DM: "현재 휴식 중이 아닙니다."
3. 휴식 종료
   ```sql
   UPDATE vacation SET end_date = DATE('now', 'localtime', '-1 day') WHERE id = ?;
   ```
4. 확인 DM 발송

**예외**:
- 셀프 등록 비활성화: vacation_self_service_enabled = 0, DM 발송

---

## UC-07: 일정/이벤트 관리

**액터**: 관리자
**위치**: 관리자 웹

### 흐름 1: 일반 이벤트 등록
```sql
INSERT INTO calendar_events
(title, description, event_date, start_time, end_date, end_time, event_type, is_global_vacation, created_by)
VALUES ('커뮤니티 모임', '월말 정기 모임', '2025-11-30', '19:00', '2025-11-30', '22:00', 'event', 0, 'admin_user');
```
- end_date = NULL: 단일 날짜
- end_date != NULL: 기간제 (예: 12/20~12/31)
- start_time, end_time = NULL: 전일 (00:00~23:59)
- 예: 2025-11-30 19:00 ~ 22:00 (연말 파티)

### 흐름 2: 전역 휴식기간 설정
```sql
INSERT INTO calendar_events
(title, description, event_date, start_time, end_date, end_time, event_type, is_global_vacation, created_by)
VALUES ('크리스마스 휴식기간', '연말 커뮤니티 휴식', '2025-12-25', NULL, '2025-12-25', NULL, 'holiday', 1, 'admin_user');
```

### 흐름 3: 수정/삭제
- UPDATE: 제목, 설명, 타입 변경
- DELETE: 확인 팝업 후 삭제

---

## UC-08: 일정 조회 (봇 명령어)

**액터**: 일반 유저, 봇

**흐름**:
1. `@봇 일정` 멘션
2. 다음 전역 휴일 조회
   ```sql
   SELECT event_date FROM calendar_events
   WHERE is_global_vacation = 1 AND event_date >= DATE('now', 'localtime')
   ORDER BY event_date ASC LIMIT 1;
   ```
3. 일정 조회 (오늘 ~ 다음 전역 휴일 전까지, 없으면 +30일)
   ```sql
   SELECT title, event_date, end_date, event_type, is_global_vacation
   FROM calendar_events
   WHERE event_date >= DATE('now', 'localtime') AND event_date < ?
   ORDER BY event_date ASC;
   ```
4. DM 응답
   ```
   📅 일정 (~ 12/25 전역 휴식 전까지)

   11/20 (수) 19:00-22:00 🎉 커뮤니티 모임
   12/20-12/24 🎄 연말 이벤트 기간

   다음 전역 휴식: 12/25 크리스마스
   ```
   - start_time, end_time이 NULL이 아니면 시간 표시

---

## UC-09: 관리자 재화 조정

**액터**: 관리자
**위치**: 관리자 웹

**흐름**:
1. 유저 선택
2. 금액 입력 (지급: 양수, 차감: 음수)
3. 사유 입력 (필수)
4. 트랜잭션 처리
   ```sql
   BEGIN TRANSACTION;
   
   UPDATE users SET currency = currency + ?, updated_at = CURRENT_TIMESTAMP WHERE mastodon_id = ?;
   
   INSERT INTO transactions (user_id, amount, balance_after, type, description, created_at)
   VALUES (?, ?, ?, 'admin_add', ?, CURRENT_TIMESTAMP);
   
   INSERT INTO admin_logs (admin_name, action_type, details)
   VALUES (?, 'adjust_currency', ?);
   
   COMMIT;
   ```

**예외**:
- 재화 부족 (차감 시): 잔액 부족 에러

---

## UC-10: 소셜 분석

**액터**: Celery 스케줄러
**스케줄**: 매일 4시 (Asia/Seoul)

**흐름**:
1. PostgreSQL에서 대화 상대 분석
   ```sql
   WITH user_conversations AS (
       SELECT account_id, in_reply_to_account_id as partner_id, COUNT(*) as reply_count
       FROM statuses
       WHERE in_reply_to_id IS NOT NULL AND created_at > NOW() - INTERVAL '48 hours'
       GROUP BY account_id, in_reply_to_account_id
   )
   SELECT user_id, unique_partners, total_replies, top_partner_id, top_partner_count,
          ROUND(top_partner_count::REAL / total_replies, 2) as top_partner_ratio
   FROM ...
   ```
2. 접속률 분석
   ```sql
   SELECT account_id, COUNT(DISTINCT DATE(created_at)) as active_days
   FROM statuses
   WHERE created_at > NOW() - INTERVAL '7 days'
   GROUP BY account_id;
   ```
3. user_stats 저장
   ```sql
   INSERT INTO user_stats
   (user_id, analyzed_at, unique_conversation_partners, total_replies_sent,
    top_partner_id, top_partner_ratio, active_days_7d, login_rate_7d,
    is_isolated, is_inactive, is_biased)
   VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?, ?, ?);
   ```
4. 문제 유저 판정
   ```python
   is_isolated = unique_partners < 7
   is_inactive = login_rate_7d < 0.5
   is_biased = top_partner_ratio > 0.3
   ```

**참고**: 자동 경고 없음, 관리자가 UC-11에서 확인 후 수동 처리

---

## UC-11: 소셜 분석 목록 조회

**액터**: 관리자
**위치**: 관리자 웹 "커뮤니티 건강도"

**흐름**:
1. 대시보드 표시
   - 🔴 대화 편중 (N명)
   - 🟡 고립 위험 (N명)
   - 🟠 비활동 (N명)
   - 🟢 건강한 유저 (N명)
2. 필터 선택 (편중/고립/비활동/전체)
3. 목록 조회
   ```sql
   SELECT us.*, u.username FROM user_stats us
   JOIN users u ON us.user_id = u.mastodon_id
   WHERE us.is_biased = 1 AND DATE(us.analyzed_at) = DATE('now', 'localtime')
   ORDER BY us.top_partner_ratio DESC;
   ```
4. 유저 상세 클릭 → 소셜 통계, 문제 플래그, 경고 이력 표시
5. "수동 경고 발송" 버튼 → UC-12로 이동

---

## UC-12: 수동 경고 발송

**액터**: 관리자
**위치**: 유저 상세 페이지 또는 경고 관리 페이지

**흐름**:
1. 유저 선택
2. 경고 유형 선택 (활동량 미달/고립 위험/비활동/기타)
3. 메시지 작성 (템플릿 제공)
4. 트랜잭션 처리
   ```sql
   BEGIN TRANSACTION;
   
   INSERT INTO warnings (user_id, warning_type, message, dm_sent, admin_name, timestamp)
   VALUES (?, ?, ?, 1, ?, CURRENT_TIMESTAMP);
   
   INSERT INTO admin_logs (admin_name, action_type, details)
   VALUES (?, 'send_warning', ?);
   
   COMMIT;
   ```
5. DM 발송
   ```python
   mastodon.status_post(f"@{username} {message}", visibility='direct')
   ```

**예외**:
- DM 발송 실패: warnings.dm_sent = 0, 재시도 큐

---

## UC-13: 경고 발송 페이지 (통합)

**액터**: 관리자
**위치**: 관리자 웹 "경고 관리"

**기능**:
- 경고 목록 조회 (유저별, 날짜별)
- 경고 템플릿 관리 (CRUD)
- 수동 경고 발송 (UC-12와 동일)

---

## UC-14: 수동 밴 (유저 차단)

**액터**: 관리자
**위치**: 유저 상세 페이지

**흐름**:
1. 유저 선택
2. 밴 사유 입력 (필수)
3. 증거 입력 (선택, JSON)
4. 트랜잭션 처리
   ```sql
   BEGIN TRANSACTION;
   
   INSERT INTO ban_records (user_id, reason, evidence, banned_by, banned_at)
   VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP);
   
   UPDATE users SET is_banned = 1, ban_reason = ? WHERE mastodon_id = ?;
   
   INSERT INTO admin_logs (admin_name, action_type, details)
   VALUES (?, 'ban_user', ?);
   
   COMMIT;
   ```
5. Mastodon API로 차단
   ```python
   mastodon.account_block(user_id)
   ```

---

## UC-15: 밴 목록 및 언밴

**액터**: 관리자
**위치**: 관리자 웹 "밴 관리"

**밴 목록**:
```sql
SELECT br.*, u.username FROM ban_records br
JOIN users u ON br.user_id = u.mastodon_id
WHERE br.unbanned_at IS NULL
ORDER BY br.banned_at DESC;
```

**언밴**:
```sql
BEGIN TRANSACTION;

UPDATE ban_records SET unbanned_at = CURRENT_TIMESTAMP, unbanned_by = ? WHERE id = ?;
UPDATE users SET is_banned = 0, ban_reason = NULL WHERE mastodon_id = ?;
INSERT INTO admin_logs (admin_name, action_type, details) VALUES (?, 'unban_user', ?);

COMMIT;
```

---

## UC-16: 자동 툿 아카이빙

**액터**: 관리자
**위치**: 유저 상세 페이지 또는 아카이빙 페이지

**전제조건**: 경고 3회 이상 누적

**흐름**:
1. 아카이빙 후보 목록 조회
   ```sql
   SELECT u.mastodon_id, u.username, COUNT(w.id) as warning_count
   FROM users u
   JOIN warnings w ON u.mastodon_id = w.user_id
   GROUP BY u.mastodon_id
   HAVING COUNT(w.id) >= ?
   ORDER BY warning_count DESC;
   ```
2. 유저 선택
3. PostgreSQL에서 툿 조회
   ```sql
   SELECT id, content, created_at FROM statuses WHERE account_id = ?;
   ```
4. 툿 다운로드 (JSON)
5. DB 기록
   ```sql
   BEGIN TRANSACTION;
   
   INSERT INTO archived_toots (user_id, mastodon_toot_id, content, archived_at, archived_by)
   VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?);
   
   INSERT INTO admin_logs (admin_name, action_type, details)
   VALUES (?, 'archive_toots', ?);
   
   COMMIT;
   ```
6. Mastodon API로 밴 (UC-14와 동일)

---

## UC-17: 아카이빙된 툿 조회

**액터**: 관리자
**위치**: 관리자 웹 "아카이빙 이력"

**조회**:
```sql
SELECT at.*, u.username FROM archived_toots at
JOIN users u ON at.user_id = u.mastodon_id
WHERE at.user_id = ?
ORDER BY at.created_at DESC;
```

**내보내기**: JSON 파일 다운로드

---

## UC-18: 예약 발송 (스토리/공지)

**액터**: Celery 스케줄러
**스케줄**: 매 1분마다 체크

**흐름**:
1. 예약 발송 대상 조회
   ```sql
   SELECT id, post_type, content, scheduled_at, visibility, mastodon_scheduled_id
   FROM scheduled_posts
   WHERE status = 'pending'
     AND scheduled_at <= DATETIME('now', 'localtime')
   ORDER BY scheduled_at ASC;
   ```
2. 각 예약 건별 처리:
   - post_type에 따라 계정 선택:
     - `story`: settings.story_account
     - `announcement`: settings.announcement_account
     - `admin_notice`: settings.admin_bot_account (visibility='private')
   - 마스토돈 API로 발송:
     ```python
     status = mastodon.status_post(content, visibility=visibility)
     ```
3. 발송 결과 업데이트
   ```sql
   UPDATE scheduled_posts
   SET status = 'published', published_at = CURRENT_TIMESTAMP, mastodon_scheduled_id = ?
   WHERE id = ?;
   ```
4. 로그 기록

**예외**:
- API 오류: status = 'failed', 재시도 큐
- 계정 설정 누락: 에러 로그 + 관리자 알림

**참고**:
- `@봇 공지` 명령어는 is_public=1인 공지만 표시
- 관리자 웹에서 is_public 체크박스로 설정

---

## 추가 검토 필요 사항

### 1. PostgreSQL 답글 수 조회 성능 (UC-02)
- 벌크 쿼리 (GROUP BY account_id)
- 예상 규모: 최대 30명
- 결론: 현재 설계로 충분

### 2. CASCADE 동작 (attendance_posts → attendances)
- 현재: FK만, CASCADE 없음
- CASCADE 추가 시: `ON DELETE CASCADE`
- 결정 보류

### 3. 봇 응답 방식
- 현재: DM
- 검토: 멘션 답글 (공개적 피드백)
- 결정 보류
