# 마녀봇 관리 페이지 사용 설명서

> **대상**: 웹 관리 페이지를 사용하는 일반 관리자
> **목적**: 웹 브라우저를 통한 시스템 관리 방법

---

## 📋 목차

1. [시스템 접속](#1-시스템-접속)
2. [대시보드 사용법](#2-대시보드-사용법)
3. [로그 뷰어 사용법](#3-로그-뷰어-사용법)
4. [자주 묻는 질문](#4-자주-묻는-질문)

---

## 1. 시스템 접속

### 1.1 관리 페이지 URL

```
http://[서버주소]:5000/
```

- 로컬 서버: `http://localhost:5000/`
- 원격 서버: 개발자에게 주소 문의

### 1.2 로그인

<details>
<summary>📸 로그인 화면 예시 (클릭하여 보기)</summary>

```svg
<svg width="800" height="500" xmlns="http://www.w3.org/2000/svg">
  <!-- 배경 그라데이션 -->
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>

  <rect width="800" height="500" fill="url(#bgGrad)"/>

  <!-- 로그인 카드 -->
  <rect x="250" y="120" width="300" height="260" rx="10" fill="white" filter="drop-shadow(0px 4px 12px rgba(0,0,0,0.15))"/>

  <!-- 아이콘 -->
  <circle cx="400" cy="170" r="25" fill="#667eea"/>
  <text x="400" y="180" font-family="Arial" font-size="24" fill="white" text-anchor="middle">✨</text>

  <!-- 제목 -->
  <text x="400" y="220" font-family="Arial" font-size="20" font-weight="bold" fill="#333" text-anchor="middle">마녀봇 관리</text>
  <text x="400" y="245" font-family="Arial" font-size="14" fill="#666" text-anchor="middle">관리자 로그인</text>

  <!-- 로그인 버튼 -->
  <rect x="290" y="275" width="220" height="45" rx="8" fill="#6364FF"/>
  <text x="400" y="303" font-family="Arial" font-size="15" fill="white" text-anchor="middle" font-weight="500">→ Mastodon으로 로그인</text>

  <!-- 하단 텍스트 -->
  <text x="400" y="360" font-family="Arial" font-size="12" fill="#999" text-anchor="middle">Mastodon OAuth 2.0 인증</text>
</svg>
```

</details>

1. 웹 브라우저에서 관리 페이지 접속
2. "Mastodon으로 로그인" 버튼 클릭
3. Mastodon 계정 인증
   - 관리자 권한이 있는 계정만 접근 가능
   - OAuth 인증 방식 사용

### 1.3 메뉴 구성

로그인 후 상단 메뉴:

- **대시보드**: 시스템 전체 통계 및 현황
- **로그 뷰어**: 관리 활동 기록 조회

---

## 2. 대시보드 사용법

### 2.1 접속 방법

- 상단 메뉴에서 "대시보드" 클릭
- 또는 메인 페이지에서 자동 이동

<details>
<summary>📸 대시보드 화면 예시 (클릭하여 보기)</summary>

```svg
<svg width="1000" height="600" xmlns="http://www.w3.org/2000/svg">
  <!-- 배경 -->
  <rect width="1000" height="600" fill="#f8f9fa"/>

  <!-- 네비게이션 바 -->
  <rect width="1000" height="60" fill="#212529"/>
  <text x="20" y="38" font-family="Arial" font-size="18" fill="white" font-weight="bold">✨ 마녀봇 관리</text>
  <text x="200" y="38" font-family="Arial" font-size="14" fill="#adb5bd">대시보드</text>
  <text x="300" y="38" font-family="Arial" font-size="14" fill="#6c757d">사용자</text>
  <text x="380" y="38" font-family="Arial" font-size="14" fill="#6c757d">이벤트</text>
  <text x="460" y="38" font-family="Arial" font-size="14" fill="#6c757d">로그</text>

  <!-- 제목 -->
  <text x="40" y="110" font-family="Arial" font-size="24" fill="#333" font-weight="bold">대시보드</text>
  <text x="40" y="135" font-family="Arial" font-size="13" fill="#6c757d">시스템 현황을 한눈에 확인하세요</text>

  <!-- 통계 카드 1: 전체 유저 -->
  <rect x="40" y="160" width="220" height="120" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="60" y="190" font-family="Arial" font-size="13" fill="#6c757d">전체 유저</text>
  <text x="60" y="230" font-family="Arial" font-size="32" fill="#333" font-weight="bold">1,247</text>
  <text x="220" y="240" font-family="Arial" font-size="40" fill="#0d6efd">👥</text>

  <!-- 통계 카드 2: 활성 유저 -->
  <rect x="280" y="160" width="220" height="120" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="300" y="190" font-family="Arial" font-size="13" fill="#6c757d">활성 유저 (24시간)</text>
  <text x="300" y="230" font-family="Arial" font-size="32" fill="#333" font-weight="bold">342</text>
  <text x="460" y="240" font-family="Arial" font-size="40" fill="#198754">✓</text>

  <!-- 통계 카드 3: 휴가 중 -->
  <rect x="520" y="160" width="220" height="120" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="540" y="190" font-family="Arial" font-size="13" fill="#6c757d">휴가 중</text>
  <text x="540" y="230" font-family="Arial" font-size="32" fill="#333" font-weight="bold">23</text>
  <text x="700" y="240" font-family="Arial" font-size="40" fill="#0dcaf0">🏖️</text>

  <!-- 통계 카드 4: 경고 발송 -->
  <rect x="760" y="160" width="220" height="120" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="780" y="190" font-family="Arial" font-size="13" fill="#6c757d">경고 발송 (7일)</text>
  <text x="780" y="230" font-family="Arial" font-size="32" fill="#333" font-weight="bold">8</text>
  <text x="940" y="240" font-family="Arial" font-size="40" fill="#ffc107">⚠️</text>

  <!-- 시스템 정보 카드 -->
  <rect x="40" y="310" width="940" height="250" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="60" y="340" font-family="Arial" font-size="16" fill="#333" font-weight="bold">시스템 정보</text>

  <!-- 정보 항목들 -->
  <text x="80" y="380" font-family="Arial" font-size="13" fill="#495057" font-weight="600">활동량 체크 주기</text>
  <text x="80" y="405" font-family="Arial" font-size="13" fill="#6c757d">오전 4시, 오후 4시 (12시간 간격)</text>

  <text x="380" y="380" font-family="Arial" font-size="13" fill="#495057" font-weight="600">최소 답글 기준</text>
  <text x="380" y="405" font-family="Arial" font-size="13" fill="#6c757d">48시간 내 20개</text>

  <text x="680" y="380" font-family="Arial" font-size="13" fill="#495057" font-weight="600">재화 지급 비율</text>
  <text x="680" y="405" font-family="Arial" font-size="13" fill="#6c757d">답글 1개당 10원</text>
</svg>
```

</details>

### 2.2 통계 카드

화면 상단에 4개의 통계 카드가 표시됩니다:

#### 📊 전체 유저
- 시스템에 등록된 전체 사용자 수
- 활성/비활성 포함

#### ✅ 활성 유저 (24시간)
- 최근 24시간 이내 활동한 사용자 수
- 커뮤니티 활성도 지표

#### 🏖️ 휴가 중
- 현재 휴가 상태인 사용자 수
- 휴가 기간 중에는 활동량 체크 면제

#### ⚠️ 경고 발송 (7일)
- 최근 7일간 발송된 경고 수
- 활동량 미달 사용자 추이 파악

### 2.3 시스템 정보

화면 하단에서 시스템 설정 확인:

- **활동량 체크 주기**: 오전 4시, 오후 4시 (12시간 간격)
- **최소 답글 기준**: 48시간 내 20개
- **재화 지급 비율**: 답글 1개당 10원

### 2.4 추가 섹션 (추후 구현)

- **최근 활동 차트**: 사용자 활동 추이 그래프
- **최근 로그**: 주요 관리 활동 요약

---

## 3. 로그 뷰어 사용법

### 3.1 접속 방법

상단 메뉴에서 "로그" 클릭

<details>
<summary>📸 로그 뷰어 화면 예시 (클릭하여 보기)</summary>

```svg
<svg width="1000" height="700" xmlns="http://www.w3.org/2000/svg">
  <!-- 배경 -->
  <rect width="1000" height="700" fill="#f8f9fa"/>

  <!-- 네비게이션 바 -->
  <rect width="1000" height="60" fill="#212529"/>
  <text x="20" y="38" font-family="Arial" font-size="18" fill="white" font-weight="bold">✨ 마녀봇 관리</text>
  <text x="200" y="38" font-family="Arial" font-size="14" fill="#6c757d">대시보드</text>
  <text x="300" y="38" font-family="Arial" font-size="14" fill="#6c757d">사용자</text>
  <text x="380" y="38" font-family="Arial" font-size="14" fill="#adb5bd">로그</text>

  <!-- 제목 -->
  <text x="40" y="110" font-family="Arial" font-size="24" fill="#333" font-weight="bold">관리자 로그</text>
  <text x="40" y="135" font-family="Arial" font-size="13" fill="#6c757d">시스템 관리자 활동 로그를 실시간으로 모니터링합니다</text>

  <!-- 통계 카드들 -->
  <rect x="40" y="160" width="220" height="80" rx="8" fill="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"/>
  <text x="60" y="185" font-family="Arial" font-size="12" fill="white">총 로그</text>
  <text x="60" y="220" font-family="Arial" font-size="28" fill="white" font-weight="bold">1,523</text>

  <rect x="280" y="160" width="220" height="80" rx="8" fill="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"/>
  <text x="300" y="185" font-family="Arial" font-size="12" fill="white">현재 페이지</text>
  <text x="300" y="220" font-family="Arial" font-size="28" fill="white" font-weight="bold">1 / 31</text>

  <!-- 필터 영역 -->
  <rect x="40" y="260" width="940" height="100" rx="8" fill="#e9ecef"/>
  <text x="60" y="285" font-family="Arial" font-size="13" fill="#495057" font-weight="600">관리자 필터</text>
  <rect x="60" y="295" width="200" height="35" rx="4" fill="white" stroke="#ced4da" stroke-width="1"/>
  <text x="70" y="318" font-family="Arial" font-size="13" fill="#495057">전체</text>

  <text x="290" y="285" font-family="Arial" font-size="13" fill="#495057" font-weight="600">액션 타입 필터</text>
  <!-- 체크박스들 -->
  <rect x="290" y="300" width="15" height="15" rx="3" fill="white" stroke="#0d6efd" stroke-width="2"/>
  <text x="312" y="312" font-family="Arial" font-size="12" fill="#495057">재화 조정</text>

  <rect x="410" y="300" width="15" height="15" rx="3" fill="white" stroke="#0d6efd" stroke-width="2"/>
  <text x="432" y="312" font-family="Arial" font-size="12" fill="#495057">경고 발송</text>

  <rect x="530" y="300" width="15" height="15" rx="3" fill="white" stroke="#0d6efd" stroke-width="2"/>
  <text x="552" y="312" font-family="Arial" font-size="12" fill="#495057">휴가 승인</text>

  <!-- 로그 뷰어 (터미널 스타일) -->
  <rect x="40" y="380" width="940" height="270" rx="8" fill="#1e1e1e"/>
  <rect x="40" y="380" width="940" height="40" rx="8" fill="#2d2d30"/>
  <text x="60" y="405" font-family="Courier New" font-size="13" fill="white">🖥️ 로그 뷰어 (라인별)</text>

  <!-- 로그 라인들 -->
  <text x="60" y="440" font-family="Courier New" font-size="11" fill="#569cd6">2025-11-18 14:30:25</text>
  <text x="220" y="440" font-family="Courier New" font-size="11" fill="#4ec9b0">마녀봇</text>
  <text x="310" y="440" font-family="Courier New" font-size="11" fill="#4ec9b0" font-weight="bold">adjust_balance</text>
  <text x="440" y="440" font-family="Courier New" font-size="11" fill="#9cdcfe">→ user_123</text>
  <text x="560" y="440" font-family="Courier New" font-size="11" fill="#ce9178">+1000원 지급</text>

  <text x="60" y="465" font-family="Courier New" font-size="11" fill="#569cd6">2025-11-18 14:15:10</text>
  <text x="220" y="465" font-family="Courier New" font-size="11" fill="#4ec9b0">운영진A</text>
  <text x="310" y="465" font-family="Courier New" font-size="11" fill="#f48771" font-weight="bold">create_warning</text>
  <text x="440" y="465" font-family="Courier New" font-size="11" fill="#9cdcfe">→ user_456</text>
  <text x="560" y="465" font-family="Courier New" font-size="11" fill="#ce9178">활동량 부족 경고</text>

  <text x="60" y="490" font-family="Courier New" font-size="11" fill="#569cd6">2025-11-18 13:45:33</text>
  <text x="220" y="490" font-family="Courier New" font-size="11" fill="#4ec9b0">총괄관리자</text>
  <text x="310" y="490" font-family="Courier New" font-size="11" fill="#4fc1ff" font-weight="bold">create_vacation</text>
  <text x="440" y="490" font-family="Courier New" font-size="11" fill="#9cdcfe">→ user_789</text>
  <text x="560" y="490" font-family="Courier New" font-size="11" fill="#ce9178">휴가 승인 (2025-11-20 ~ 2025-11-27)</text>

  <text x="60" y="515" font-family="Courier New" font-size="11" fill="#569cd6">2025-11-18 13:20:15</text>
  <text x="220" y="515" font-family="Courier New" font-size="11" fill="#4ec9b0">마녀봇</text>
  <text x="310" y="515" font-family="Courier New" font-size="11" fill="#b5cea8" font-weight="bold">create_event</text>
  <text x="440" y="515" font-family="Courier New" font-size="11" fill="#9cdcfe">-</text>
  <text x="560" y="515" font-family="Courier New" font-size="11" fill="#ce9178">신년 이벤트 생성</text>

  <text x="60" y="540" font-family="Courier New" font-size="11" fill="#569cd6">2025-11-18 12:50:42</text>
  <text x="220" y="540" font-family="Courier New" font-size="11" fill="#4ec9b0">운영진B</text>
  <text x="310" y="540" font-family="Courier New" font-size="11" fill="#c586c0" font-weight="bold">update_setting</text>
  <text x="440" y="540" font-family="Courier New" font-size="11" fill="#9cdcfe">-</text>
  <text x="560" y="540" font-family="Courier New" font-size="11" fill="#ce9178">activity_threshold 변경: 20 → 25</text>
</svg>
```

</details>

### 3.2 화면 구성

#### 상단 통계 카드

- **전체 로그 수**: 기록된 모든 관리 활동 수
- **오늘의 로그**: 당일 발생한 활동 수
- **관리자 수**: 활동 중인 관리자 계정 수

#### 필터 영역

**액션 타입 필터** (체크박스)
- ☑️ 재화 조정: 사용자 재화 지급/차감
- ☑️ 경고 발송: 활동량 미달 경고
- ☑️ 권한 변경: 사용자 역할 변경
- ☑️ 휴가 승인: 휴가 신청 승인
- ☑️ 휴가 거부: 휴가 신청 거부
- ☑️ 이벤트 생성: 새 이벤트 등록
- ☑️ 이벤트 수정: 이벤트 정보 변경
- ☑️ 아이템 생성: 상점 아이템 추가
- ☑️ 설정 변경: 시스템 설정 변경
- ☑️ 사용자 차단: 문제 사용자 차단

**관리자 필터** (드롭다운)
- 전체: 모든 관리자 활동 표시
- 특정 관리자: 해당 관리자 활동만 표시

### 3.3 로그 목록

각 로그 라인에는 다음 정보가 표시됩니다:

```
[번호] [날짜 시간] [관리자] [액션타입] 상세 내용
```

**예시:**
```
[42] 2025-11-18 14:30:25 [마녀봇] [재화조정] 김민준에게 +1,000원 조정
[41] 2025-11-18 14:15:10 [운영진A] [경고발송] 이서연에게 활동량 부족 경고 발송
[40] 2025-11-18 13:45:33 [총괄관리자] [휴가승인] 박하준의 휴가 신청 승인
```

### 3.4 필터링 방법

#### 액션 타입으로 필터링

1. 보고 싶은 액션 타입만 체크
2. 자동으로 해당 타입만 표시됨
3. 모든 체크 해제 시 전체 표시

**사용 예시:**
- "재화 조정"만 체크 → 재화 지급/차감 내역만 표시
- "경고 발송" + "휴가 승인" 체크 → 두 타입만 표시

#### 관리자로 필터링

1. 드롭다운에서 관리자 이름 선택
2. "필터 적용" 버튼 클릭
3. 해당 관리자의 활동만 표시

**사용 예시:**
- "마녀봇" 선택 → 자동화 봇의 활동만 표시
- "운영진A" 선택 → 특정 관리자의 활동만 확인

#### 복합 필터링

액션 타입과 관리자 필터를 동시에 사용 가능:

**예시:**
- 관리자: "운영진A" 선택
- 액션: "재화 조정" 체크
- 결과: 운영진A가 수행한 재화 조정만 표시

### 3.5 페이지네이션

- 하단에 페이지 번호 표시
- 한 페이지에 50개 로그 표시
- 페이지 번호 클릭으로 이동

### 3.6 로그 색상

각 액션 타입별로 색상이 다르게 표시됩니다:

- 🟢 **재화 조정**: 초록색
- 🟡 **경고 발송**: 노란색
- 🔵 **권한 변경**: 파란색
- 🟣 **휴가 관련**: 보라색
- 🟠 **이벤트/아이템**: 주황색
- 🔴 **설정 변경**: 빨간색

---

## 4. 자주 묻는 질문

### Q1. 로그인이 안 돼요

**확인 사항:**
1. Mastodon 계정이 관리자 권한이 있나요?
2. 서버가 정상 실행 중인가요?
3. 네트워크 연결은 정상인가요?

**해결 방법:**
- 개발자에게 관리자 권한 요청
- 서버 상태 확인 (EMERGENCY.md 참조)

### Q2. 통계가 업데이트 안 돼요

**원인:**
- 대시보드는 페이지 로드 시점의 데이터를 보여줍니다
- 실시간 업데이트가 아닙니다

**해결 방법:**
- 브라우저 새로고침 (F5 또는 Ctrl+R)

### Q3. 로그가 너무 많아서 찾기 힘들어요

**해결 방법:**
1. 액션 타입 필터 활용
   - 보고 싶은 타입만 체크
2. 관리자 필터 활용
   - 특정 관리자의 활동만 확인
3. 복합 필터링 사용
   - 두 필터를 동시에 적용

**예시:**
- 오늘 "운영진A"가 수행한 "재화 조정"만 보고 싶다면:
  1. 관리자: "운영진A" 선택
  2. 액션: "재화 조정"만 체크
  3. 필터 적용

### Q4. 특정 사용자의 활동 기록을 보고 싶어요

**현재 기능:**
- 로그 뷰어에서는 관리자 활동만 조회 가능
- 사용자별 필터링은 아직 미구현

**대안:**
- 브라우저 검색 기능 (Ctrl+F) 사용
- 사용자 이름으로 검색

**향후 업데이트:**
- 사용자별 필터 추가 예정

### Q5. 로그를 엑셀로 내보낼 수 있나요?

**현재 상태:**
- 웹 UI에서 직접 내보내기는 미구현

**대안:**
1. 브라우저의 "페이지 저장" 기능 사용
2. 또는 개발자에게 데이터베이스 추출 요청

**향후 업데이트:**
- CSV/Excel 내보내기 기능 추가 예정

### Q6. 서버가 다운되었어요!

긴급 상황입니다. **EMERGENCY.md** 문서를 참조하세요.

간단한 재시작 방법:
```bash
# 서버 재시작 (한 줄 명령어)
pkill -9 -f "python.*admin_web" && cd /home/user/commumanager && nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

### Q7. 사용자 재화를 지급하고 싶어요

**현재 상태:**
- 웹 UI에서 직접 재화 지급 기능은 미구현
- 현재는 API 또는 데이터베이스 직접 조작 필요

**대안:**
- 개발자에게 요청
- 또는 EMERGENCY.md의 "데이터베이스 직접 조작" 섹션 참조

**향후 업데이트:**
- 사용자 관리 페이지에서 재화 지급 기능 추가 예정

### Q8. 경고를 발송하고 싶어요

**현재 상태:**
- 웹 UI에서 직접 경고 발송 기능은 미구현
- 자동화 봇이 자동으로 발송하거나, 개발자가 수동 발송

**대안:**
- 개발자에게 요청

**향후 업데이트:**
- 경고 관리 페이지 추가 예정

---

## 📞 추가 지원

### 문제가 해결되지 않을 때

1. **긴급 상황**: EMERGENCY.md 참조
2. **개발자 연락**: [개발자 연락처]
3. **로그 확인**: 서버의 `flask_server.log` 파일 확인

### 문서 업데이트

이 문서는 시스템 업데이트에 따라 계속 갱신됩니다.
마지막 업데이트: 2025-11-18
