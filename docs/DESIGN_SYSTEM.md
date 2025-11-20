# 마녀봇 관리 시스템 디자인 시스템

> **대상**: 개발자 및 디자이너
> **목적**: 일관된 UI/UX를 위한 디자인 가이드라인

---

## 📌 개요

이 문서는 마녀봇 관리 시스템의 디자인 시스템을 정의합니다. Bootstrap 5를 기반으로 하며, 모든 화면에서 일관된 색상, 타이포그래피, 컴포넌트 스타일을 사용합니다.

**프레임워크:**
- Bootstrap 5.3.0
- Bootstrap Icons 1.11.0

---

## 🎨 색상 팔레트

### Primary Colors

Bootstrap 5의 기본 색상 팔레트를 사용합니다:

| 용도 | 색상 코드 | 설명 |
|------|-----------|------|
| 주요 액션 | `#0d6efd` | 파란색 - 버튼, 링크, 활성 상태 |
| 성공 | `#198754` | 초록색 - 완료, 정상 상태 |
| 경고 | `#ffc107` | 노란색 - 주의, 대기 상태 |
| 위험 | `#dc3545` | 빨간색 - 오류, 삭제, 경고 |
| 정보 | `#0dcaf0` | 청록색 - 안내, 보조 정보 |

### Neutral Colors

| 용도 | 색상 코드 | 설명 |
|------|-----------|------|
| 배경 | `#f8f9fa` | 밝은 회색 - 페이지 배경 |
| 테두리 | `#dee2e6` | 중간 회색 - 카드, 테이블 경계 |
| 텍스트 (진함) | `#495057` | 어두운 회색 - 본문 텍스트 |
| 텍스트 (중간) | `#6c757d` | 회색 - 보조 텍스트 |
| 텍스트 (연함) | `#adb5bd` | 밝은 회색 - 비활성 텍스트 |
| 다크 | `#212529` | 검은색 - 네비게이션 바, 강조 텍스트 |

### 상태 색상

| 상태 | 색상 | 사용 사례 |
|------|------|-----------|
| 정상 | `#198754` | 활성 유저, 완료된 작업 |
| 주의 | `#ffc107` | 경고 대상, 대기 중 작업 |
| 위험 | `#dc3545` | 오류, 실패, 삭제 |
| 휴식 | `#6c757d` | 휴식 중인 유저 |
| 진행 중 | `#0dcaf0` | 처리 중인 작업 |

---

## 📝 타이포그래피

### 폰트 패밀리

- **기본**: Arial, sans-serif
- **코드/로그**: Courier New, monospace

### 크기 및 굵기

| 요소 | 크기 | 굵기 | 사용 사례 |
|------|------|------|-----------|
| h1 제목 | 24px | Bold (700) | 페이지 제목 |
| h2 부제목 | 20px | Bold (700) | 섹션 제목 |
| h5-h6 소제목 | 16px | Bold (600) | 카드 헤더 |
| 본문 | 13px | Regular (400) | 일반 텍스트, 설명 |
| 작은 텍스트 | 11-12px | Regular (400) | 보조 정보, 라벨 |
| 코드/로그 | 13px | Regular (400) | 터미널, 코드 블록 |

### 행간 (Line Height)

- 본문: 1.5
- 제목: 1.2

---

## 🧩 컴포넌트

### 카드 (Card)

```css
border-radius: 8px;
box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
background: #ffffff;
padding: 1rem; /* 16px */
```

**사용 사례:**
- 통계 카드
- 콘텐츠 컨테이너
- 폼 래퍼

### 버튼 (Button)

```css
border-radius: 4px;
height: 35-40px;
padding: 0.5rem 1rem; /* 8px 16px */
font-size: 13px;
```

**버튼 색상 (Bootstrap classes):**
- `.btn-primary` - 주요 액션 (#0d6efd)
- `.btn-success` - 성공, 완료 (#198754)
- `.btn-danger` - 삭제, 위험 (#dc3545)
- `.btn-warning` - 경고 (#ffc107)
- `.btn-info` - 정보 (#0dcaf0)
- `.btn-secondary` - 보조 액션 (#6c757d)

### 뱃지 (Badge)

```css
border-radius: 12px; /* pill shape */
padding: 0.25rem 0.5rem;
font-size: 11px;
```

**상태 뱃지:**
- `.badge.bg-success` - 완료, 정상
- `.badge.bg-warning` - 대기, 주의
- `.badge.bg-danger` - 실패, 위험
- `.badge.bg-info` - 진행 중
- `.badge.bg-secondary` - 기본, 비활성

### 입력 필드 (Input)

```css
border-radius: 4px;
border: 1px solid #dee2e6;
padding: 0.5rem;
font-size: 13px;
```

### 테이블 (Table)

```css
.table {
  border-collapse: collapse;
}

.table thead {
  background: #f8f9fa;
  font-weight: 600;
}

.table tbody tr:hover {
  background: #f8f9fa;
}

.table td {
  padding: 0.75rem;
  vertical-align: middle;
}
```

### 모달 (Modal)

```css
.modal-content {
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.modal-header {
  border-bottom: 1px solid #dee2e6;
  padding: 1rem;
}

.modal-footer {
  border-top: 1px solid #dee2e6;
  padding: 1rem;
}
```

---

## 📱 반응형 디자인

모든 화면은 Bootstrap 5 Grid 시스템을 사용하여 다양한 화면 크기에 대응합니다.

### 브레이크포인트

| 크기 | 해상도 | 그리드 열 | 사용 사례 |
|------|---------|-----------|-----------|
| 모바일 | < 768px | 1열 | 스마트폰 |
| 태블릿 | ≥ 768px | 2열 | 태블릿, 소형 노트북 |
| 데스크톱 | ≥ 1200px | 4열 | 데스크톱, 대형 모니터 |

### 반응형 클래스

```html
<!-- 통계 카드 예시 -->
<div class="row g-4">
  <div class="col-12 col-md-6 col-xl-3">
    <div class="card">...</div>
  </div>
</div>
```

**설명:**
- `col-12`: 모바일에서 전체 너비 (1열)
- `col-md-6`: 태블릿에서 50% 너비 (2열)
- `col-xl-3`: 데스크톱에서 25% 너비 (4열)

---

## 🎯 아이콘

**Bootstrap Icons 1.11.0** 사용

### 주요 아이콘

| 아이콘 | 클래스 | 사용 사례 |
|--------|--------|-----------|
| 📊 | `bi-speedometer2` | 대시보드 |
| 👥 | `bi-people` | 사용자 |
| ⚠️ | `bi-exclamation-triangle` | 활동량, 경고 |
| 📅 | `bi-calendar3` | 콘텐츠, 일정 |
| 📹 | `bi-camera-reels` | 스토리 이벤트 |
| 📢 | `bi-megaphone` | 공지 |
| 🛒 | `bi-shop` | 상점 |
| 📋 | `bi-list-check` | 로그 |
| ⚙️ | `bi-gear` | 설정 |
| ✨ | `bi-magic` | 로고, 브랜드 |

---

## 🔧 네비게이션

### 상단 네비게이션 바

```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <!-- 로고, 메뉴, 사용자 드롭다운 -->
</nav>
```

**색상:**
- 배경: `#2d3748` (다크 그레이)
- 텍스트: `#ffffff` (흰색)
- 활성 메뉴: `#4299e1` (파란색 배경)
- 호버: `#a0aec0` (밝은 회색)

### 드롭다운 메뉴

```html
<li class="nav-item dropdown">
  <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
    콘텐츠
  </a>
  <ul class="dropdown-menu">
    <li><a class="dropdown-item" href="#">일정 관리</a></li>
    <li><a class="dropdown-item" href="#">스토리 이벤트</a></li>
    <li><a class="dropdown-item" href="#">공지 예약</a></li>
  </ul>
</li>
```

---

## 📐 레이아웃 패턴

### 통계 카드 그리드

```html
<div class="row g-4 mb-4">
  <div class="col-12 col-md-6 col-xl-3">
    <div class="card">
      <div class="card-body">
        <h6 class="text-muted mb-2">전체 유저</h6>
        <h2 class="mb-0">28</h2>
      </div>
    </div>
  </div>
  <!-- 반복 -->
</div>
```

### 데이터 테이블

```html
<div class="card">
  <div class="card-header">
    <h5 class="mb-0">목록</h5>
  </div>
  <div class="card-body">
    <div class="table-responsive">
      <table class="table table-hover">
        <thead>...</thead>
        <tbody>...</tbody>
      </table>
    </div>
  </div>
</div>
```

---

## 🔗 관련 문서

- [관리자 가이드](ADMIN_GUIDE.md) - 웹 UI 사용법 (비개발자용)
- [API 설계](api_design.md) - REST API 명세
- [데이터베이스](database.md) - DB 스키마

---

**마지막 업데이트**: 2025-11-20
**문서 버전**: 1.0
