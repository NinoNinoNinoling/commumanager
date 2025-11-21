# Flask 관리자 웹 API 설계

## 개요
REST API 기반 관리자 웹 백엔드

**Base URL**: `/api/v1`
**인증**: Session-based (OAuth)
**응답 형식**: JSON
**통화 단위**: 갈레온(Galleon) - 모든 금액은 갈레온 단위로 표기

## 인증 (Authentication)

### POST /auth/login
마스토돈 OAuth 로그인 시작

**Response**:
```json
{
  "redirect_url": "https://mastodon.instance/oauth/authorize?..."
}
```

### GET /auth/callback
OAuth 콜백 처리

**Query Params**:
- `code`: OAuth authorization code

**Response**: Redirect to `/dashboard` or 403

### POST /auth/logout
로그아웃

**Response**: 204 No Content

### GET /auth/me
현재 로그인된 사용자 정보

**Response**:
```json
{
  "mastodon_id": "123456",
  "username": "admin",
  "role": "admin",
  "is_super_admin": true
}
```

## 대시보드 (Dashboard)

### GET /api/v1/dashboard/stats
전체 통계

**Response**:
```json
{
  "users": {
    "total": 150,
    "active_24h": 45,
    "on_vacation": 5
  },
  "currency": {
    "total_circulating": 50000,
    "total_earned": 120000,
    "total_spent": 70000
  },
  "activity": {
    "replies_48h": 1250,
    "users_below_threshold": 8
  },
  "warnings": {
    "total": 23,
    "this_week": 3
  },
  "scheduled_content": {
    "pending_story_events": 3,
    "pending_announcements": 5
  }
}
```

## 유저 관리 (Users)

### GET /api/v1/users
유저 목록

**Query Params**:
- `page`: int (default: 1)
- `limit`: int (default: 50)
- `search`: string (username, display_name)
- `role`: string (user, admin)
- `status`: string (active, below_threshold, on_vacation)
- `sort`: string (balance_desc, balance_asc, created_desc)

**Response**:
```json
{
  "users": [
    {
      "mastodon_id": "123456",
      "username": "user1",
      "display_name": "유저1",
      "role": "user",
      "dormitory": "A동",
      "balance": 1500,
      "total_earned": 3000,
      "total_spent": 1500,
      "last_active": "2025-11-18T10:30:00Z",
      "status": "active",
      "warning_count": 0,
      "is_key_member": false
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

### GET /api/v1/users/{mastodon_id}
유저 상세 정보

**Response**:
```json
{
  "mastodon_id": "123456",
  "username": "user1",
  "display_name": "유저1",
  "role": "user",
  "dormitory": "A동",
  "balance": 1500,
  "total_earned": 3000,
  "total_spent": 1500,
  "reply_count": 250,
  "last_active": "2025-11-18T10:30:00Z",
  "created_at": "2025-01-01T00:00:00Z",
  "activity_48h": 25,
  "is_on_vacation": false,
  "warning_count": 0,
  "is_key_member": false
}
```

### PATCH /api/v1/users/{mastodon_id}/role
역할 변경 (총괄계정만 가능)

**Request**:
```json
{
  "role": "admin"
}
```

**Response**: 200 OK

### PATCH /api/v1/users/{mastodon_id}/key-member
주요 멤버 설정 (회피 패턴 감지용)

**Request**:
```json
{
  "is_key_member": true
}
```

**Response**: 200 OK

### GET /api/v1/users/{mastodon_id}/transactions
유저 거래 내역

**Query Params**:
- `page`, `limit`, `type` (earn_reply, earn_attendance, spend_item, admin_adjust)

**Response**:
```json
{
  "transactions": [
    {
      "id": 1,
      "transaction_type": "earn_reply",
      "category": "활동량 정산",
      "amount": 10,
      "description": "답글 작성",
      "timestamp": "2025-11-18T10:00:00Z"
    }
  ],
  "pagination": {...}
}
```

### GET /api/v1/users/{mastodon_id}/warnings
유저 경고 내역

**Response**:
```json
{
  "warnings": [
    {
      "id": 1,
      "warning_type": "low_activity",
      "risk_details": {
        "required_replies": 20,
        "actual_replies": 15,
        "period_hours": 48
      },
      "message": "활동량 미달 경고: 48시간 내 답글이 15개로 기준(20개)에 미달했습니다.",
      "dm_sent": true,
      "admin_name": "admin",
      "timestamp": "2025-11-18T04:00:00Z"
    },
    {
      "id": 2,
      "warning_type": "bias",
      "risk_details": {
        "target_user_id": "789012",
        "target_username": "user2",
        "conversation_ratio": 0.15,
        "threshold": 0.10
      },
      "message": "편향 경고: @user2와의 대화가 15%입니다.",
      "dm_sent": true,
      "admin_name": "admin",
      "timestamp": "2025-11-17T04:00:00Z"
    }
  ]
}
```

### GET /api/v1/users/{mastodon_id}/activity
활동량 상세 (PostgreSQL 실시간 조회)

**Response**:
```json
{
  "period_hours": 48,
  "reply_count": 25,
  "threshold": 20,
  "status": "normal",
  "hourly_distribution": [
    {"hour": "2025-11-17 00:00", "count": 2},
    {"hour": "2025-11-17 01:00", "count": 0}
  ]
}
```

## 재화 관리 (Transactions)

### GET /api/v1/transactions
전체 거래 내역

**Query Params**:
- `page`, `limit`, `user_id`, `type`, `start_date`, `end_date`

**Response**: 거래 내역 목록

### POST /api/v1/transactions/adjust
재화 조정 (관리자)

**Request**:
```json
{
  "user_id": "123456",
  "amount": 100,
  "category": "이벤트 보상",
  "description": "출석 이벤트 참여"
}
```

**참고**: 카테고리 옵션 - [이벤트 보상], [상점 구매], [활동량 정산], [오류 수정]

**Response**: 201 Created

## 활동량 관리 (Activity)

### GET /api/v1/activity/check
활동량 체크 실행

**Query Params**:
- `period_hours`: int (default: 48)
- `min_replies`: int (default: 5)
- `risk_types`: array (isolation, bias, avoidance, low_activity) - 필터링할 위험 유형

**Response**:
```json
{
  "checked_at": "2025-11-18T04:00:00Z",
  "total_users": 150,
  "below_threshold": [
    {
      "mastodon_id": "123456",
      "username": "user1",
      "reply_count": 15,
      "threshold": 20,
      "on_vacation": false
    }
  ]
}
```

### GET /api/v1/users/at-risk
위험 감지 유저 목록 조회

**Query Params**:
- `risk_types`: array (isolation, bias, avoidance, low_activity) - 조회할 위험 유형 (기본: 전체)

**Response**:
```json
{
  "total_at_risk": 8,
  "by_risk_type": {
    "isolation": 2,
    "bias": 3,
    "avoidance": 1,
    "low_activity": 5
  },
  "users": [
    {
      "mastodon_id": "123456",
      "username": "user1",
      "display_name": "유저1",
      "risk_types": ["bias", "low_activity"],
      "risk_details": {
        "bias": {
          "target_user_id": "789012",
          "target_username": "user2",
          "conversation_ratio": 0.15,
          "threshold": 0.10
        },
        "low_activity": {
          "reply_count": 3,
          "threshold": 5,
          "period_hours": 48
        }
      },
      "warning_count": 1
    }
  ]
}
```

### GET /api/v1/users/{mastodon_id}/social-analysis
소셜 네트워크 분석 (대화 상대, 편향도, 회피 패턴)

**Query Params**:
- `period_hours`: int (default: 48)

**Response**:
```json
{
  "analyzed_at": "2025-11-18T04:00:00Z",
  "period_hours": 48,
  "conversation_partners": [
    {
      "user_id": "789012",
      "username": "user2",
      "interaction_count": 15,
      "ratio": 0.15
    },
    {
      "user_id": "345678",
      "username": "user3",
      "interaction_count": 10,
      "ratio": 0.10
    }
  ],
  "total_interactions": 100,
  "unique_partners": 5,
  "active_users_in_period": 12,
  "isolation_risk": {
    "detected": true,
    "partner_count": 5,
    "active_users": 12,
    "threshold_ratio": 0.5
  },
  "bias_risk": {
    "detected": true,
    "target_user_id": "789012",
    "target_username": "user2",
    "ratio": 0.15,
    "threshold": 0.10
  },
  "avoidance_risk": {
    "detected": false,
    "avoided_key_members": []
  }
}
```

### GET /api/v1/users/{mastodon_id}/avoidance-detection
회피 패턴 감지

**Response**:
```json
{
  "detected_at": "2025-11-18T04:00:00Z",
  "user_activity": {
    "is_active": true,
    "reply_count_48h": 25
  },
  "key_members": [
    {
      "user_id": "111222",
      "username": "key_member1",
      "is_key_member": true,
      "was_active_in_period": true,
      "interactions_with_target": 0,
      "avoidance_detected": true
    },
    {
      "user_id": "333444",
      "username": "key_member2",
      "is_key_member": true,
      "was_active_in_period": false,
      "interactions_with_target": 0,
      "avoidance_detected": false
    }
  ],
  "avoided_key_members": ["111222"],
  "avoidance_detected": true
}
```

### GET /api/v1/warnings
경고 내역 조회

**Query Params**:
- `page`, `limit`, `user_id`, `warning_type`, `start_date`, `end_date`

**Response**: 경고 내역 목록

### POST /api/v1/warnings
경고 발송 (수동)

**Request**:
```json
{
  "user_id": "123456",
  "warning_type": "low_activity",
  "message": "활동량 미달 경고",
  "send_dm": true
}
```

**참고**: warning_type 옵션 - isolation (고립 위험), bias (편향 위험), avoidance (회피 패턴), low_activity (답글 미달), manual (기타)

**Response**: 201 Created

### POST /api/v1/warnings/bulk
경고 일괄 발송

**Request**:
```json
{
  "user_ids": ["123456", "789012", "345678"],
  "warning_type": "low_activity",
  "send_dm": true,
  "admin_name": "admin"
}
```

**Response**:
```json
{
  "sent": ["123456", "789012"],
  "failed": [
    {
      "user_id": "345678",
      "reason": "DM 발송 실패"
    }
  ],
  "total": 3,
  "success": 2,
  "failed_count": 1
}
```

## 휴식 관리 (Vacation)

### GET /api/v1/vacations
휴식 내역

**Query Params**:
- `page`, `limit`, `user_id`, `status` (active, past)

**Response**:
```json
{
  "vacations": [
    {
      "id": 1,
      "user_id": "123456",
      "username": "user1",
      "start_date": "2025-11-18",
      "start_time": null,
      "end_date": "2025-11-20",
      "end_time": null,
      "reason": "개인 사정",
      "description": "가족 행사로 인한 휴식",
      "registered_by": "user",
      "created_at": "2025-11-17T10:00:00Z"
    }
  ]
}
```

### POST /api/v1/vacations
휴식 등록

**Request**:
```json
{
  "user_id": "123456",
  "start_date": "2025-11-18",
  "start_time": "14:00",
  "end_date": "2025-11-20",
  "end_time": "18:00",
  "reason": "병가",
  "description": "병원 치료 및 회복 기간"
}
```

**Response**: 201 Created

### DELETE /api/v1/vacations/{id}
휴식 해제

**Response**: 204 No Content

## 일정 관리 (Calendar)

### GET /api/v1/calendar/events
일정 목록

**Query Params**:
- `start_date`, `end_date`, `event_type` (general, holiday, community), `is_global_vacation`

**Response**:
```json
{
  "events": [
    {
      "id": 1,
      "title": "크리스마스",
      "description": "메리 크리스마스!",
      "event_date": "2025-12-25",
      "start_time": null,
      "end_date": null,
      "end_time": null,
      "event_type": "holiday",
      "is_global_vacation": true,
      "created_by": "admin",
      "created_at": "2025-11-01T00:00:00Z"
    }
  ]
}
```

### POST /api/v1/calendar/events
일정 등록

**Request**:
```json
{
  "title": "커뮤니티 모임",
  "description": "오프라인 모임",
  "event_date": "2025-12-01",
  "start_time": "19:00",
  "end_date": "2025-12-01",
  "end_time": "22:00",
  "event_type": "general",
  "is_global_vacation": false
}
```

**Response**: 201 Created

### PUT /api/v1/calendar/events/{id}
일정 수정

**Request**: 동일

**Response**: 200 OK

### DELETE /api/v1/calendar/events/{id}
일정 삭제

**Response**: 204 No Content

## 아이템 관리 (Items)

### GET /api/v1/items
아이템 목록

**Query Params**:
- `category`, `is_active`

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "배지",
      "description": "커뮤니티 배지",
      "price": 100,
      "category": "collectible",
      "image_url": "https://...",
      "is_active": true,
      "initial_stock": 100,
      "current_stock": 85,
      "sold_count": 15,
      "is_unlimited_stock": false,
      "max_purchase_per_user": 1,
      "total_sales": 1500,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### POST /api/v1/items
아이템 등록

**Request**:
```json
{
  "name": "배지",
  "description": "한정판 배지",
  "price": 100,
  "category": "collectible",
  "image_url": "https://...",
  "initial_stock": 100,
  "is_unlimited_stock": false,
  "max_purchase_per_user": 1
}
```

**Response**: 201 Created

### PUT /api/v1/items/{id}
아이템 수정

**Request**: 동일

**Response**: 200 OK

### DELETE /api/v1/items/{id}
아이템 삭제 (비활성화)

**Response**: 204 No Content

## 시스템 설정 (Settings)

### GET /api/v1/settings
전체 설정 조회

**Response**:
```json
{
  "settings": [
    {
      "key": "check_period_hours",
      "value": "48",
      "description": "조회 기간 (시간)",
      "updated_at": "2025-01-01T00:00:00Z",
      "updated_by": "admin"
    }
  ]
}
```

### PUT /api/v1/settings/{key}
설정 값 변경

**Request**:
```json
{
  "value": "50"
}
```

**Response**: 200 OK

## 관리자 로그 (Admin Logs)

### GET /api/v1/admin-logs
관리자 액션 로그

**Query Params**:
- `page`, `limit`, `admin_name`, `action_type`, `start_date`, `end_date`

**Response**:
```json
{
  "logs": [
    {
      "id": 1,
      "admin_name": "admin",
      "action_type": "adjust_balance",
      "target_user": "user1",
      "details": "재화 100갈레온 지급 (이벤트 보상)",
      "timestamp": "2025-11-18T10:00:00Z"
    }
  ],
  "pagination": {...}
}
```

## 스토리 예약 (Story Events)

### GET /api/v1/story-events
스토리 이벤트 목록 조회

**Query Params**:
- `page`, `limit`, `status` (pending, in_progress, completed, failed)

**Response**:
```json
{
  "events": [
    {
      "id": 1,
      "title": "새해 인사 시리즈",
      "description": "2025년 새해 맞이 스토리",
      "calendar_event_id": 5,
      "start_time": "2025-01-01T00:00:00",
      "interval_minutes": 10,
      "status": "pending",
      "post_count": 3,
      "created_by": "admin",
      "created_at": "2024-12-30T10:00:00"
    }
  ],
  "pagination": {...}
}
```

### GET /api/v1/story-events/:id
스토리 이벤트 상세 조회 (포스트 포함)

**Response**:
```json
{
  "id": 1,
  "title": "새해 인사 시리즈",
  "start_time": "2025-01-01T00:00:00",
  "interval_minutes": 10,
  "status": "pending",
  "posts": [
    {
      "id": 1,
      "sequence": 1,
      "content": "새해 복 많이 받으세요! 🎉",
      "media_urls": ["https://example.com/img1.jpg"],
      "status": "pending",
      "scheduled_at": "2025-01-01T00:00:00"
    },
    {
      "id": 2,
      "sequence": 2,
      "content": "2025년도 즐거운 한 해 되세요!",
      "media_urls": null,
      "status": "pending",
      "scheduled_at": "2025-01-01T00:10:00"
    }
  ]
}
```

### POST /api/v1/story-events
스토리 이벤트 생성

**Request**:
```json
{
  "title": "새해 인사 시리즈",
  "description": "2025년 새해 맞이 스토리",
  "start_time": "2025-01-01T00:00:00",
  "interval_minutes": 10,
  "calendar_event_id": 5,
  "admin_name": "admin"
}
```

**Response**: 201 Created

### POST /api/v1/story-events/:id/posts
스토리 포스트 추가

**Request**:
```json
{
  "posts": [
    {
      "sequence": 1,
      "content": "새해 복 많이 받으세요! 🎉",
      "media_urls": ["https://example.com/img1.jpg"]
    },
    {
      "sequence": 2,
      "content": "2025년도 즐거운 한 해 되세요!",
      "media_urls": null
    }
  ],
  "admin_name": "admin"
}
```

**Response**: 201 Created

### POST /api/v1/story-events/bulk-upload
스토리 이벤트 엑셀 일괄 업로드

**Request**: multipart/form-data
- `file`: Excel file (.xlsx)
- `admin_name`: string

**Response**:
```json
{
  "created": [
    {
      "id": 1,
      "title": "새해 이벤트",
      "post_count": 2
    }
  ],
  "failed": [],
  "summary": {
    "total_events": 1,
    "success": 1,
    "failed": 0
  }
}
```

### PUT /api/v1/story-events/:id
스토리 이벤트 수정

### DELETE /api/v1/story-events/:id
스토리 이벤트 삭제 (포스트도 함께 삭제)

### PUT /api/v1/story-posts/:id
스토리 포스트 수정

### DELETE /api/v1/story-posts/:id
스토리 포스트 삭제

---

## 공지 예약 (Announcements)

### GET /api/v1/announcements
공지 목록 조회

**Query Params**:
- `page`, `limit`, `status` (pending, published, failed), `type` (announcement 등)

**Response**:
```json
{
  "announcements": [
    {
      "id": 1,
      "post_type": "announcement",
      "content": "내일 오전 10시부터 서버 점검이 있습니다.",
      "scheduled_at": "2025-01-20T09:00:00",
      "visibility": "public",
      "is_public": true,
      "status": "pending",
      "created_by": "admin",
      "created_at": "2025-01-19T15:00:00"
    }
  ],
  "pagination": {...}
}
```

### GET /api/v1/announcements/:id
공지 상세 조회

### POST /api/v1/announcements
공지 생성

**Request**:
```json
{
  "post_type": "announcement",
  "content": "내일 오전 10시부터 서버 점검이 있습니다.",
  "scheduled_at": "2025-01-20T09:00:00",
  "visibility": "public",
  "is_public": true,
  "admin_name": "admin"
}
```

**Response**: 201 Created

### PUT /api/v1/announcements/:id
공지 수정

### DELETE /api/v1/announcements/:id
공지 삭제

---

## 에러 응답

### 4xx 클라이언트 에러
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "재화는 0 이상이어야 합니다",
    "field": "amount"
  }
}
```

### 5xx 서버 에러
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "서버 오류가 발생했습니다"
  }
}
```

## 권한 체계

- **총괄계정**: 모든 API 접근 가능
- **role='admin'**: 역할 변경 제외 모든 API 접근 가능
- **일반 유저**: API 접근 불가

## Rate Limiting
- 일반 요청: 100 req/min
- 통계 조회: 20 req/min
- 인증: 5 req/min
