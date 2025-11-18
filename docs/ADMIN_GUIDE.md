# 마녀봇 관리 시스템 - 관리자 가이드

> **대상**: 비개발자 관리자 (마스토돈 서버 운영자, 커뮤니티 관리자)
> **목적**: 일상적인 관리 작업 수행

---

## 📋 목차

1. [시스템 접속 방법](#시스템-접속-방법)
2. [대시보드 사용법](#대시보드-사용법)
3. [유저 관리](#유저-관리)
4. [재화 관리](#재화-관리)
5. [경고 관리](#경고-관리)
6. [휴가 관리](#휴가-관리)
7. [이벤트/캘린더 관리](#이벤트캘린더-관리)
8. [아이템/상점 관리](#아이템상점-관리)
9. [시스템 설정](#시스템-설정)
10. [로그 확인](#로그-확인)
11. [자주 묻는 질문](#자주-묻는-질문)

---

## 시스템 접속 방법

### 웹 브라우저로 접속

1. 웹 브라우저를 엽니다 (Chrome, Firefox 등)
2. 주소창에 입력: `http://서버주소:5000`
3. 로그인 (OAuth 인증)

**개발 모드에서는 자동 로그인됩니다.**

### 주요 페이지

- **대시보드**: `http://서버주소:5000/dashboard`
  - 전체 통계를 한눈에 확인

- **로그 뷰어**: `http://서버주소:5000/logs`
  - 관리자 활동 기록 확인

---

## 대시보드 사용법

### 통계 카드

대시보드 상단에 4개의 카드가 표시됩니다:

1. **전체 유저**: 시스템에 등록된 총 유저 수
2. **활성 유저 (24시간)**: 최근 24시간 내 활동한 유저 수
3. **휴가 중**: 현재 휴가 중인 유저 수
4. **경고 발송 (7일)**: 최근 7일간 발송된 경고 수

### 재화 통계

- **유통 중인 재화**: 현재 시스템에 유통되는 총 재화
- **총 획득 재화**: 유저들이 획득한 총 재화
- **총 사용 재화**: 유저들이 사용한 총 재화

### 시스템 정보

- 활동량 체크 주기
- 최소 답글 기준
- 재화 지급 비율

---

## 유저 관리

### 유저 목록 조회 (Postman 사용)

**엔드포인트**: `GET /api/v1/users`

**쿼리 파라미터**:
- `page`: 페이지 번호 (기본값: 1)
- `limit`: 페이지당 항목 수 (기본값: 50)
- `search`: 유저명 또는 표시명 검색
- `role`: 역할 필터 (`user` 또는 `admin`)
- `sort`: 정렬 방식
  - `created_desc`: 가입일 내림차순 (최신순)
  - `created_asc`: 가입일 오름차순
  - `balance_desc`: 재화 많은 순
  - `balance_asc`: 재화 적은 순

**예시 요청**:
```
GET http://서버주소:5000/api/v1/users?page=1&limit=50&sort=balance_desc
```

**응답 예시**:
```json
{
  "users": [
    {
      "mastodon_id": "1234567890",
      "username": "user1",
      "display_name": "유저1",
      "role": "user",
      "balance": 5000,
      "total_earned": 10000,
      "total_spent": 5000
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 100,
    "total_pages": 2
  }
}
```

### 유저 상세 조회

**엔드포인트**: `GET /api/v1/users/{mastodon_id}`

**예시**:
```
GET http://서버주소:5000/api/v1/users/1234567890
```

**응답에 포함되는 정보**:
- 기본 정보 (이름, 역할, 기숙사)
- 재화 정보 (잔액, 총 획득, 총 사용)
- 활동 정보 (48시간 내 답글 수)
- 휴가 여부
- 경고 횟수

### 유저 역할 변경

**엔드포인트**: `PATCH /api/v1/users/{mastodon_id}/role`

**용도**: 일반 유저를 관리자로 승격하거나, 관리자를 일반 유저로 강등

**요청 본문**:
```json
{
  "role": "admin"
}
```

**역할 종류**:
- `user`: 일반 유저
- `admin`: 관리자

**예시 (Postman)**:
1. Method: `PATCH`
2. URL: `http://서버주소:5000/api/v1/users/1234567890/role`
3. Body → raw → JSON:
   ```json
   {
     "role": "admin"
   }
   ```
4. Send 클릭

---

## 재화 관리

### 재화 조정 (지급 또는 차감)

**엔드포인트**: `POST /api/v1/transactions/adjust`

**용도**:
- 유저에게 재화를 지급하거나 차감
- 이벤트 보상, 벌금 부과 등

**요청 본문**:
```json
{
  "user_id": "1234567890",
  "amount": 1000,
  "description": "이벤트 참여 보상",
  "admin_name": "관리자이름"
}
```

**주의사항**:
- `amount`가 **양수**면 지급
- `amount`가 **음수**면 차감
- 예: `-500`은 500원 차감

**예시 (지급)**:
```json
{
  "user_id": "1234567890",
  "amount": 2000,
  "description": "월간 우수 회원 보상",
  "admin_name": "홍길동"
}
```

**예시 (차감)**:
```json
{
  "user_id": "1234567890",
  "amount": -500,
  "description": "규정 위반 벌금",
  "admin_name": "홍길동"
}
```

### 유저별 거래 내역 조회

**엔드포인트**: `GET /api/v1/users/{mastodon_id}/transactions`

**쿼리 파라미터**:
- `page`: 페이지 번호
- `limit`: 페이지당 항목 수
- `type`: 거래 타입 필터
  - `earn_reply`: 답글로 획득
  - `earn_attendance`: 출석으로 획득
  - `spend_item`: 아이템 구매로 사용
  - `admin_adjust`: 관리자 조정

**예시**:
```
GET http://서버주소:5000/api/v1/users/1234567890/transactions?page=1&limit=50
```

---

## 경고 관리

### 경고 목록 조회

**엔드포인트**: `GET /api/v1/warnings`

**쿼리 파라미터**:
- `page`: 페이지 번호
- `limit`: 페이지당 항목 수

### 경고 발송

**엔드포인트**: `POST /api/v1/warnings`

**요청 본문**:
```json
{
  "user_id": "1234567890",
  "reason": "활동 부족 (48시간 내 답글 20개 미만)",
  "count": 1,
  "admin_name": "시스템봇"
}
```

**경고 사유 예시**:
- "활동 부족 (48시간 내 답글 20개 미만)"
- "부적절한 언어 사용"
- "규정 위반"
- "스팸 행위"

**경고 횟수**:
- 보통 `count: 1`로 설정
- 중대한 위반 시 `count: 2` 이상 가능

### 유저별 경고 조회

**엔드포인트**: `GET /api/v1/users/{mastodon_id}/warnings`

**예시**:
```
GET http://서버주소:5000/api/v1/users/1234567890/warnings
```

---

## 휴가 관리

### 휴가 목록 조회

**엔드포인트**: `GET /api/v1/vacations`

**응답 예시**:
```json
{
  "vacations": [
    {
      "id": 1,
      "user_id": "1234567890",
      "start_date": "2025-01-15",
      "end_date": "2025-01-22",
      "start_time": "09:00",
      "end_time": "18:00",
      "reason": "개인 사유",
      "created_at": "2025-01-10T10:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 5,
    "total_pages": 1
  }
}
```

### 휴가 등록

**엔드포인트**: `POST /api/v1/vacations`

**요청 본문**:
```json
{
  "user_id": "1234567890",
  "start_date": "2025-01-15",
  "end_date": "2025-01-22",
  "start_time": "09:00",
  "end_time": "18:00",
  "reason": "개인 사유",
  "admin_name": "관리자이름"
}
```

**필드 설명**:
- `start_date`, `end_date`: 필수 (YYYY-MM-DD 형식)
- `start_time`, `end_time`: 선택 (HH:MM 형식)
- `reason`: 휴가 사유 (선택)
- `admin_name`: 휴가를 등록한 관리자 (선택)

### 휴가 삭제

**엔드포인트**: `DELETE /api/v1/vacations/{vacation_id}`

**요청 본문** (선택):
```json
{
  "admin_name": "관리자이름"
}
```

**예시 (Postman)**:
1. Method: `DELETE`
2. URL: `http://서버주소:5000/api/v1/vacations/1`
3. Body → raw → JSON (선택):
   ```json
   {
     "admin_name": "홍길동"
   }
   ```
4. Send 클릭

---

## 이벤트/캘린더 관리

### 이벤트 목록 조회

**엔드포인트**: `GET /api/v1/calendar/events`

**쿼리 파라미터**:
- `type`: 이벤트 타입 필터
  - `general`: 일반 이벤트
  - `holiday`: 공휴일
  - `community`: 커뮤니티 모임

**예시**:
```
GET http://서버주소:5000/api/v1/calendar/events?type=community
```

### 이벤트 생성

**엔드포인트**: `POST /api/v1/calendar/events`

**요청 본문**:
```json
{
  "title": "커뮤니티 월례 모임",
  "description": "매월 첫째 주 토요일 정기 모임",
  "event_type": "community",
  "start_date": "2025-02-01",
  "end_date": "2025-02-01",
  "start_time": "19:00",
  "end_time": "21:00",
  "admin_name": "관리자이름"
}
```

**이벤트 타입**:
- `general`: 일반 이벤트 (기본값)
- `holiday`: 공휴일
- `community`: 커뮤니티 행사

### 이벤트 수정

**엔드포인트**: `PUT /api/v1/calendar/events/{event_id}`

**요청 본문**:
```json
{
  "title": "커뮤니티 월례 모임 (장소 변경)",
  "description": "장소가 A에서 B로 변경되었습니다",
  "event_type": "community",
  "start_date": "2025-02-01",
  "end_date": "2025-02-01",
  "start_time": "19:00",
  "end_time": "22:00",
  "admin_name": "관리자이름"
}
```

### 이벤트 삭제

**엔드포인트**: `DELETE /api/v1/calendar/events/{event_id}`

**요청 본문** (선택):
```json
{
  "admin_name": "관리자이름"
}
```

---

## 아이템/상점 관리

### 아이템 목록 조회

**엔드포인트**: `GET /api/v1/items`

**쿼리 파라미터**:
- `is_active`: 활성화 상태 필터 (`true` 또는 `false`)

**예시**:
```
GET http://서버주소:5000/api/v1/items?is_active=true
```

### 아이템 생성

**엔드포인트**: `POST /api/v1/items`

**요청 본문**:
```json
{
  "name": "프로필 배경 변경권",
  "description": "프로필 배경을 원하는 이미지로 변경할 수 있습니다",
  "price": 1000,
  "is_active": true,
  "admin_name": "관리자이름"
}
```

**필드 설명**:
- `name`: 아이템 이름 (필수)
- `description`: 설명 (선택)
- `price`: 가격 (기본값: 0)
- `is_active`: 판매 활성화 여부 (기본값: true)

### 아이템 수정

**엔드포인트**: `PUT /api/v1/items/{item_id}`

**요청 본문**:
```json
{
  "name": "프로필 배경 변경권",
  "description": "프로필 배경 변경 (할인 이벤트 중!)",
  "price": 800,
  "is_active": true,
  "admin_name": "관리자이름"
}
```

**용도**:
- 가격 변경
- 설명 업데이트
- 판매 중지/재개 (`is_active` 변경)

### 아이템 삭제

**엔드포인트**: `DELETE /api/v1/items/{item_id}`

**주의**: 아이템 삭제 전에 `is_active: false`로 설정하여 판매 중지하는 것을 권장합니다.

---

## 시스템 설정

### 설정 조회

**엔드포인트**: `GET /api/v1/settings`

**응답 예시**:
```json
{
  "settings": [
    {
      "key": "timezone",
      "value": "Asia/Seoul",
      "description": "타임존"
    },
    {
      "key": "check_period_hours",
      "value": "48",
      "description": "조회 기간 (시간)"
    },
    {
      "key": "min_reply_count",
      "value": "20",
      "description": "최소 답글 수"
    },
    {
      "key": "currency_per_reply",
      "value": "10",
      "description": "답글당 재화 지급액"
    }
  ]
}
```

### 설정 업데이트

**엔드포인트**: `PUT /api/v1/settings/{key}`

**요청 본문**:
```json
{
  "value": "24",
  "admin_name": "관리자이름"
}
```

**주요 설정 항목**:

| 키 | 설명 | 기본값 | 예시 값 |
|---|---|---|---|
| `timezone` | 타임존 | `Asia/Seoul` | `UTC`, `Asia/Tokyo` |
| `check_period_hours` | 활동량 체크 주기 (시간) | `48` | `24`, `72` |
| `min_reply_count` | 최소 답글 수 | `20` | `15`, `30` |
| `currency_per_reply` | 답글당 재화 지급액 | `10` | `5`, `20` |
| `attendance_reward` | 출석 보상 재화 | `50` | `30`, `100` |

**예시 (최소 답글 수를 20에서 15로 변경)**:
```
PUT http://서버주소:5000/api/v1/settings/min_reply_count
```
```json
{
  "value": "15",
  "admin_name": "홍길동"
}
```

---

## 로그 확인

### 웹 페이지에서 확인

1. 로그 뷰어 페이지 접속: `http://서버주소:5000/logs`
2. 왼쪽 통계 카드에서 전체 로그 수 확인
3. 필터 옵션:
   - **관리자 필터**: 드롭다운에서 특정 관리자 선택
   - **액션 타입 필터**: 체크박스로 원하는 액션만 표시
     - `create_warning`: 경고 생성
     - `create_vacation`: 휴가 등록
     - `delete_vacation`: 휴가 삭제
     - `adjust_balance`: 재화 조정
     - `change_role`: 역할 변경
     - 등등...

### API로 조회

**엔드포인트**: `GET /api/v1/admin-logs`

**쿼리 파라미터**:
- `page`: 페이지 번호
- `limit`: 페이지당 항목 수 (기본값: 50)
- `admin_name`: 관리자명 필터
- `action`: 액션 타입 필터

**예시 (특정 관리자의 로그만 조회)**:
```
GET http://서버주소:5000/api/v1/admin-logs?admin_name=홍길동&page=1&limit=50
```

**응답 예시**:
```json
{
  "logs": [
    {
      "id": 100,
      "admin_name": "홍길동",
      "action": "adjust_balance",
      "target_user": "1234567890",
      "details": "이벤트 보상 +2000원",
      "timestamp": "2025-01-18T15:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 150,
    "total_pages": 3
  }
}
```

---

## 자주 묻는 질문

### Q1. 유저를 어떻게 찾나요?

A: 유저 목록 API에서 `search` 파라미터를 사용하세요.

```
GET /api/v1/users?search=유저이름
```

---

### Q2. 재화를 잘못 지급했어요. 되돌릴 수 있나요?

A: 네, 재화 조정 API를 다시 사용하여 음수 금액으로 차감하면 됩니다.

**예시 (잘못 지급한 1000원 회수)**:
```json
{
  "user_id": "1234567890",
  "amount": -1000,
  "description": "재화 지급 오류 수정",
  "admin_name": "관리자이름"
}
```

---

### Q3. 경고를 취소할 수 있나요?

A: 현재 버전에서는 경고 삭제 기능이 없습니다. 대신 관리자 로그에 "경고 취소" 메모를 남길 수 있습니다.

---

### Q4. 휴가 기간을 수정하려면?

A: 현재 버전에서는 휴가 수정 기능이 없습니다. 기존 휴가를 삭제하고 새로 등록하세요.

1. 휴가 삭제: `DELETE /api/v1/vacations/{vacation_id}`
2. 새 휴가 등록: `POST /api/v1/vacations`

---

### Q5. 아이템을 일시적으로 판매 중지하려면?

A: 아이템 수정 API에서 `is_active: false`로 설정하세요.

```json
{
  "name": "아이템명",
  "description": "설명",
  "price": 가격,
  "is_active": false,
  "admin_name": "관리자이름"
}
```

---

### Q6. Postman 사용법을 모르겠어요.

A: 간단한 Postman 사용 가이드:

1. **Postman 설치**: https://www.postman.com/downloads/
2. **Collection Import**:
   - File → Import
   - `docs/postman_collection.json` 선택
3. **요청 보내기**:
   - 왼쪽에서 원하는 API 선택
   - Variables에서 `base_url` 확인 (http://서버주소:5000/api/v1)
   - Body 탭에서 JSON 데이터 수정
   - Send 클릭

---

### Q7. 관리자 로그는 누가 볼 수 있나요?

A: 모든 관리자가 볼 수 있습니다. 로그 뷰어 페이지 또는 API로 조회 가능합니다.

---

### Q8. 시스템 설정을 잘못 변경했어요.

A: 설정 조회 API로 기본값을 확인하고, 다시 업데이트하세요.

**기본값**:
- `timezone`: `Asia/Seoul`
- `check_period_hours`: `48`
- `min_reply_count`: `20`
- `currency_per_reply`: `10`
- `attendance_reward`: `50`

---

## 📞 문의

- **기술 문의**: 개발자에게 연락
- **운영 문의**: 총괄 관리자에게 연락
- **긴급 상황**: `docs/EMERGENCY.md` 참고

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-01-18
