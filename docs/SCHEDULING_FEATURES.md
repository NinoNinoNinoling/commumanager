# 예약 발송 기능

## 개요

마스토돈 봇 관리 시스템에서 스토리와 공지를 예약해서 자동으로 발송할 수 있는 기능입니다.

## 기능

### 1. 스토리 이벤트 예약

스토리 이벤트는 **여러 개의 포스트를 일정 간격으로 발송**하는 단위입니다.

#### 구조

```
스토리 이벤트 (Story Event)
├── 제목, 설명
├── 시작 시간
├── 포스트 간 간격 (분 단위)
├── 연결된 일정 (calendar_event_id, 선택)
└── 포스트 목록 (Story Posts)
    ├── 포스트 1 (순서 1)
    │   ├── 내용
    │   ├── 미디어 URL
    │   └── 발송 시간 (자동 계산)
    ├── 포스트 2 (순서 2)
    └── ...
```

#### API 엔드포인트

**이벤트 관리**
- `GET /api/v1/story-events` - 이벤트 목록 조회
- `GET /api/v1/story-events/:id` - 이벤트 상세 조회 (포스트 포함)
- `POST /api/v1/story-events` - 이벤트 생성
- `PUT /api/v1/story-events/:id` - 이벤트 수정
- `DELETE /api/v1/story-events/:id` - 이벤트 삭제 (포스트도 함께 삭제)

**포스트 관리**
- `POST /api/v1/story-events/:id/posts` - 이벤트에 포스트 추가
- `PUT /api/v1/story-posts/:id` - 포스트 수정
- `DELETE /api/v1/story-posts/:id` - 포스트 삭제

**일괄 업로드**
- `POST /api/v1/story-events/bulk-upload` - 엑셀 파일로 일괄 업로드

#### 예제: 이벤트 생성

```bash
curl -X POST http://localhost:5000/api/v1/story-events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "새해 이벤트 스토리",
    "description": "2025년 새해 맞이 스토리 시리즈",
    "start_time": "2025-01-01T00:00:00",
    "interval_minutes": 10,
    "calendar_event_id": 5,
    "admin_name": "admin"
  }'
```

#### 예제: 포스트 추가

```bash
curl -X POST http://localhost:5000/api/v1/story-events/1/posts \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [
      {
        "sequence": 1,
        "content": "새해 복 많이 받으세요! 🎉",
        "media_urls": ["https://example.com/newyear1.jpg"]
      },
      {
        "sequence": 2,
        "content": "2025년도 즐거운 한 해 되세요!",
        "media_urls": ["https://example.com/newyear2.jpg"]
      },
      {
        "sequence": 3,
        "content": "올해는 더 많은 이벤트를 준비했어요!",
        "media_urls": null
      }
    ],
    "admin_name": "admin"
  }'
```

위 예제에서:
- 첫 번째 포스트: 2025-01-01 00:00:00 발송
- 두 번째 포스트: 2025-01-01 00:10:00 발송 (10분 후)
- 세 번째 포스트: 2025-01-01 00:20:00 발송 (20분 후)

#### 엑셀 일괄 업로드

**엑셀 파일 형식:**

| event_title | start_time | interval_minutes | post_content | post_media_urls |
|-------------|------------|------------------|--------------|-----------------|
| 새해 이벤트 | 2025-01-01T00:00:00 | 10 | 새해 복 많이 받으세요! | https://example.com/img1.jpg |
| 새해 이벤트 | 2025-01-01T00:00:00 | 10 | 즐거운 한 해 되세요! | https://example.com/img2.jpg |
| 생일 축하 | 2025-02-14T12:00:00 | 5 | 생일 축하합니다! | |

**업로드:**

```bash
curl -X POST http://localhost:5000/api/v1/story-events/bulk-upload \
  -F "file=@story_events.xlsx" \
  -F "admin_name=admin"
```

**응답:**

```json
{
  "created": [
    {
      "id": 1,
      "title": "새해 이벤트",
      "post_count": 2,
      ...
    },
    {
      "id": 2,
      "title": "생일 축하",
      "post_count": 1,
      ...
    }
  ],
  "failed": [],
  "summary": {
    "total_events": 2,
    "success": 2,
    "failed": 0
  }
}
```

### 2. 공지 예약

단일 공지를 특정 시간에 예약 발송합니다.

#### API 엔드포인트

- `GET /api/v1/announcements` - 공지 목록 조회
- `GET /api/v1/announcements/:id` - 공지 상세 조회
- `POST /api/v1/announcements` - 공지 생성
- `PUT /api/v1/announcements/:id` - 공지 수정
- `DELETE /api/v1/announcements/:id` - 공지 삭제

#### 예제: 공지 생성

```bash
curl -X POST http://localhost:5000/api/v1/announcements \
  -H "Content-Type: application/json" \
  -d '{
    "post_type": "announcement",
    "content": "내일 오전 10시부터 서버 점검이 있습니다.",
    "scheduled_at": "2025-01-20T09:00:00",
    "visibility": "public",
    "is_public": true,
    "admin_name": "admin"
  }'
```

## Web UI

### 스토리 이벤트 관리
- URL: `/story-events`
- 기능: 이벤트 목록 조회, 통계 확인
- 현재: API 중심으로 관리 (UI는 간략 버전)

### 공지 예약 관리
- URL: `/announcements`
- 기능: 공지 목록 조회, 통계 확인
- 현재: API 중심으로 관리 (UI는 간략 버전)

## 데이터베이스 스키마

### story_events

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 |
| title | TEXT | 이벤트 제목 |
| description | TEXT | 설명 |
| calendar_event_id | INTEGER | 연결된 일정 (FK, 선택) |
| start_time | TIMESTAMP | 시작 시간 |
| interval_minutes | INTEGER | 포스트 간 간격 (분) |
| status | TEXT | pending, in_progress, completed, failed |
| created_by | TEXT | 생성자 |
| created_at | TIMESTAMP | 생성 시간 |
| published_at | TIMESTAMP | 발행 시간 |

### story_posts

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 |
| event_id | INTEGER | 이벤트 ID (FK) |
| sequence | INTEGER | 순서 (1, 2, 3, ...) |
| content | TEXT | 포스트 내용 |
| media_urls | TEXT | 미디어 URL (JSON 배열) |
| status | TEXT | pending, published, failed |
| mastodon_post_id | TEXT | 마스토돈 포스트 ID |
| scheduled_at | TIMESTAMP | 예약 시간 |
| published_at | TIMESTAMP | 발행 시간 |
| error_message | TEXT | 오류 메시지 |

### scheduled_posts (공지)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 |
| post_type | TEXT | announcement 등 |
| content | TEXT | 내용 |
| scheduled_at | TIMESTAMP | 예약 시간 |
| visibility | TEXT | public, unlisted, private |
| is_public | BOOLEAN | 공개 여부 |
| status | TEXT | pending, published, failed |
| mastodon_scheduled_id | TEXT | 마스토돈 예약 ID |
| created_by | TEXT | 생성자 |
| created_at | TIMESTAMP | 생성 시간 |
| published_at | TIMESTAMP | 발행 시간 |

## TODO: Celery 예약 발송 태스크

현재 예약 기능은 DB에 저장되지만, 실제 발송은 아직 구현되지 않았습니다.

**구현 필요:**
- `bot/tasks.py`에 Celery 태스크 추가
- 매분 실행되는 스케줄러로 pending 상태 확인
- 예약 시간이 지난 포스트/공지 자동 발송
- 상태 업데이트 (pending → published/failed)

**참고 코드 위치:**
- `bot/tasks.py` - 기존 Celery 태스크 참고
- `bot/reward_bot.py` - Mastodon API 발송 참고

## 예약 발송 플로우 (예정)

```
1. 관리자가 스토리/공지 예약 생성 (Web UI 또는 API)
   ↓
2. DB에 저장 (status: pending)
   ↓
3. Celery Beat가 매분 실행
   ↓
4. 예약 시간이 지난 항목 확인
   ↓
5. Mastodon API로 발송
   ↓
6. 성공 시: status = published, published_at 기록
   실패 시: status = failed, error_message 기록
```

## 연결된 일정 (Calendar Event)

스토리 이벤트는 `calendar_events` 테이블과 연결할 수 있습니다 (FK: calendar_event_id).

**장점:**
- 일정 페이지에서 스토리 이벤트 함께 관리
- 일정 삭제 시 스토리 이벤트는 유지 (ON DELETE SET NULL)

**예시:**
```sql
-- 생일 일정 생성
INSERT INTO calendar_events (title, event_date, event_type)
VALUES ('철수 생일', '2025-02-14', 'birthday');

-- 생일 스토리 이벤트 생성 (일정과 연결)
INSERT INTO story_events (title, calendar_event_id, start_time, interval_minutes)
VALUES ('철수 생일 축하 스토리', 1, '2025-02-14T12:00:00', 5);
```

## 라이브러리 추가

엑셀 업로드를 위해 `openpyxl` 라이브러리가 추가되었습니다.

```bash
pip install openpyxl==3.1.2
```
