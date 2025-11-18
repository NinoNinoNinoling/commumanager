# 마녀봇 관리 페이지 화면 예시

> 관리자 웹 인터페이스의 주요 화면 모습입니다.

---

## 📱 주요 화면

### 1. 사용자 목록 페이지

<details open>
<summary>📸 화면 보기</summary>


<svg width="1000" height="700" xmlns="http://www.w3.org/2000/svg">
  <!-- 배경 -->
  <rect width="1000" height="700" fill="#f8f9fa"/>

  <!-- 네비게이션 바 -->
  <rect width="1000" height="60" fill="#212529"/>
  <text x="20" y="38" font-family="Arial" font-size="18" fill="white" font-weight="bold">✨ 마녀봇 관리</text>
  <text x="200" y="38" font-family="Arial" font-size="14" fill="#6c757d">대시보드</text>
  <text x="300" y="38" font-family="Arial" font-size="14" fill="#adb5bd">사용자</text>
  <text x="400" y="38" font-family="Arial" font-size="14" fill="#6c757d">이벤트</text>

  <!-- 제목 -->
  <text x="40" y="110" font-family="Arial" font-size="24" fill="#333" font-weight="bold">사용자 관리</text>
  <text x="40" y="135" font-family="Arial" font-size="13" fill="#6c757d">커뮤니티 사용자를 관리하고 조회합니다</text>

  <!-- 검색 필터 카드 -->
  <rect x="40" y="160" width="940" height="80" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="60" y="185" font-family="Arial" font-size="13" fill="#495057" font-weight="600">검색</text>
  <rect x="60" y="195" width="300" height="35" rx="4" fill="white" stroke="#ced4da" stroke-width="1"/>
  <text x="70" y="218" font-family="Arial" font-size="13" fill="#adb5bd">사용자명 또는 ID 검색</text>

  <text x="390" y="185" font-family="Arial" font-size="13" fill="#495057" font-weight="600">역할</text>
  <rect x="390" y="195" width="150" height="35" rx="4" fill="white" stroke="#ced4da" stroke-width="1"/>
  <text x="400" y="218" font-family="Arial" font-size="13" fill="#495057">전체</text>

  <rect x="880" y="195" width="80" height="35" rx="4" fill="#0d6efd"/>
  <text x="920" y="218" font-family="Arial" font-size="13" fill="white" text-anchor="middle" font-weight="500">검색</text>

  <!-- 테이블 -->
  <rect x="40" y="260" width="940" height="400" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>

  <!-- 테이블 헤더 -->
  <rect x="40" y="260" width="940" height="40" rx="8" fill="#f8f9fa"/>
  <text x="60" y="285" font-family="Arial" font-size="12" fill="#495057" font-weight="600">사용자명</text>
  <text x="200" y="285" font-family="Arial" font-size="12" fill="#495057" font-weight="600">표시명</text>
  <text x="340" y="285" font-family="Arial" font-size="12" fill="#495057" font-weight="600">역할</text>
  <text x="460" y="285" font-family="Arial" font-size="12" fill="#495057" font-weight="600">잔액</text>
  <text x="560" y="285" font-family="Arial" font-size="12" fill="#495057" font-weight="600">경고</text>
  <text x="660" y="285" font-family="Arial" font-size="12" fill="#495057" font-weight="600">휴가 상태</text>
  <text x="780" y="285" font-family="Arial" font-size="12" fill="#495057" font-weight="600">최종 활동</text>
  <text x="910" y="285" font-family="Arial" font-size="12" fill="#495057" font-weight="600">액션</text>

  <!-- 테이블 행 1 -->
  <line x1="40" y1="300" x2="980" y2="300" stroke="#dee2e6" stroke-width="1"/>
  <text x="60" y="330" font-family="Arial" font-size="13" fill="#0d6efd">@user123</text>
  <text x="200" y="330" font-family="Arial" font-size="13" fill="#495057">김민준</text>
  <rect x="340" y="318" width="80" height="22" rx="4" fill="#6c757d"/>
  <text x="380" y="333" font-family="Arial" font-size="11" fill="white" text-anchor="middle">사용자</text>
  <text x="460" y="330" font-family="Arial" font-size="13" fill="#495057">15,420원</text>
  <text x="560" y="330" font-family="Arial" font-size="13" fill="#6c757d">없음</text>
  <text x="660" y="330" font-family="Arial" font-size="13" fill="#198754">활동 중</text>
  <text x="780" y="330" font-family="Arial" font-size="12" fill="#6c757d">2025-11-18</text>
  <rect x="910" y="318" width="50" height="24" rx="4" fill="white" stroke="#0d6efd" stroke-width="1"/>
  <text x="935" y="333" font-family="Arial" font-size="11" fill="#0d6efd" text-anchor="middle">상세</text>

  <!-- 테이블 행 2 -->
  <line x1="40" y1="350" x2="980" y2="350" stroke="#dee2e6" stroke-width="1"/>
  <text x="60" y="380" font-family="Arial" font-size="13" fill="#0d6efd">@user456</text>
  <text x="200" y="380" font-family="Arial" font-size="13" fill="#495057">이서연</text>
  <rect x="340" y="368" width="80" height="22" rx="4" fill="#ffc107"/>
  <text x="380" y="383" font-family="Arial" font-size="11" fill="#212529" text-anchor="middle" font-weight="600">관리자</text>
  <text x="460" y="380" font-family="Arial" font-size="13" fill="#495057">8,750원</text>
  <rect x="560" y="368" width="55" height="22" rx="4" fill="#dc3545"/>
  <text x="587" y="383" font-family="Arial" font-size="11" fill="white" text-anchor="middle">2회</text>
  <text x="660" y="380" font-family="Arial" font-size="13" fill="#198754">활동 중</text>
  <text x="780" y="380" font-family="Arial" font-size="12" fill="#6c757d">2025-11-17</text>
  <rect x="910" y="368" width="50" height="24" rx="4" fill="white" stroke="#0d6efd" stroke-width="1"/>
  <text x="935" y="383" font-family="Arial" font-size="11" fill="#0d6efd" text-anchor="middle">상세</text>

  <!-- 테이블 행 3 -->
  <line x1="40" y1="400" x2="980" y2="400" stroke="#dee2e6" stroke-width="1"/>
  <text x="60" y="430" font-family="Arial" font-size="13" fill="#0d6efd">@user789</text>
  <text x="200" y="430" font-family="Arial" font-size="13" fill="#495057">박하준</text>
  <rect x="340" y="418" width="80" height="22" rx="4" fill="#6c757d"/>
  <text x="380" y="433" font-family="Arial" font-size="11" fill="white" text-anchor="middle">사용자</text>
  <text x="460" y="430" font-family="Arial" font-size="13" fill="#495057">22,100원</text>
  <text x="560" y="430" font-family="Arial" font-size="13" fill="#6c757d">없음</text>
  <rect x="660" y="418" width="70" height="22" rx="4" fill="#0dcaf0"/>
  <text x="695" y="433" font-family="Arial" font-size="11" fill="#212529" text-anchor="middle">휴가 중</text>
  <text x="780" y="430" font-family="Arial" font-size="12" fill="#6c757d">2025-11-15</text>
  <rect x="910" y="418" width="50" height="24" rx="4" fill="white" stroke="#0d6efd" stroke-width="1"/>
  <text x="935" y="433" font-family="Arial" font-size="11" fill="#0d6efd" text-anchor="middle">상세</text>

  <!-- 배지 -->
  <rect x="900" y="268" width="70" height="24" rx="12" fill="#6c757d"/>
  <text x="935" y="285" font-family="Arial" font-size="11" fill="white" text-anchor="middle">총 1,247명</text>
</svg>

</details>

---

### 2. 이벤트 관리 페이지

<details>
<summary>📸 화면 보기</summary>


<svg width="1000" height="700" xmlns="http://www.w3.org/2000/svg">
  <!-- 배경 -->
  <rect width="1000" height="700" fill="#f8f9fa"/>

  <!-- 네비게이션 바 -->
  <rect width="1000" height="60" fill="#212529"/>
  <text x="20" y="38" font-family="Arial" font-size="18" fill="white" font-weight="bold">✨ 마녀봇 관리</text>
  <text x="200" y="38" font-family="Arial" font-size="14" fill="#6c757d">대시보드</text>
  <text x="300" y="38" font-family="Arial" font-size="14" fill="#6c757d">사용자</text>
  <text x="400" y="38" font-family="Arial" font-size="14" fill="#adb5bd">이벤트</text>

  <!-- 제목 -->
  <text x="40" y="110" font-family="Arial" font-size="24" fill="#333" font-weight="bold">이벤트 관리</text>
  <text x="40" y="135" font-family="Arial" font-size="13" fill="#6c757d">커뮤니티 이벤트를 조회하고 관리합니다</text>

  <!-- 통계 카드들 -->
  <rect x="40" y="160" width="220" height="100" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="60" y="190" font-family="Arial" font-size="13" fill="#6c757d">전체 이벤트</text>
  <text x="60" y="225" font-family="Arial" font-size="32" fill="#333" font-weight="bold">42</text>
  <text x="190" y="235" font-family="Arial" font-size="36" fill="#0d6efd">📅</text>

  <rect x="280" y="160" width="220" height="100" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="300" y="190" font-family="Arial" font-size="13" fill="#6c757d">진행 중</text>
  <text x="300" y="225" font-family="Arial" font-size="32" fill="#333" font-weight="bold">8</text>
  <text x="450" y="235" font-family="Arial" font-size="36" fill="#198754">▶️</text>

  <rect x="520" y="160" width="220" height="100" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="540" y="190" font-family="Arial" font-size="13" fill="#6c757d">예정</text>
  <text x="540" y="225" font-family="Arial" font-size="32" fill="#333" font-weight="bold">12</text>
  <text x="690" y="235" font-family="Arial" font-size="36" fill="#ffc107">⏳</text>

  <rect x="760" y="160" width="220" height="100" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="780" y="190" font-family="Arial" font-size="13" fill="#6c757d">종료</text>
  <text x="780" y="225" font-family="Arial" font-size="32" fill="#333" font-weight="bold">22</text>
  <text x="930" y="235" font-family="Arial" font-size="36" fill="#6c757d">✓</text>

  <!-- 이벤트 카드 1 -->
  <rect x="40" y="280" width="460" height="160" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="60" y="310" font-family="Arial" font-size="16" fill="#333" font-weight="bold">🎉 신년 맞이 특별 이벤트</text>
  <text x="60" y="335" font-family="Arial" font-size="13" fill="#6c757d">새해를 맞이하여 전체 회원에게 특별 보상 지급</text>

  <rect x="60" y="350" width="60" height="22" rx="4" fill="#dc3545"/>
  <text x="90" y="365" font-family="Arial" font-size="11" fill="white" text-anchor="middle">특별</text>

  <rect x="130" y="350" width="70" height="22" rx="4" fill="#198754"/>
  <text x="165" y="365" font-family="Arial" font-size="11" fill="white" text-anchor="middle">진행 중</text>

  <rect x="210" y="350" width="15" height="22" fill="transparent"/>
  <text x="215" y="365" font-family="Arial" font-size="20" fill="#198754">✓</text>
  <text x="230" y="365" font-family="Arial" font-size="11" fill="#6c757d">공개</text>

  <text x="60" y="395" font-family="Arial" font-size="12" fill="#495057" font-weight="600">시작:</text>
  <text x="100" y="395" font-family="Arial" font-size="12" fill="#6c757d">2025-01-01 00:00</text>
  <text x="250" y="395" font-family="Arial" font-size="12" fill="#495057" font-weight="600">종료:</text>
  <text x="290" y="395" font-family="Arial" font-size="12" fill="#6c757d">2025-01-07 23:59</text>

  <text x="60" y="415" font-family="Arial" font-size="11" fill="#adb5bd">생성일: 2024-12-20 | 관리자: 마녀봇</text>

  <!-- 이벤트 카드 2 -->
  <rect x="520" y="280" width="460" height="160" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="540" y="310" font-family="Arial" font-size="16" fill="#333" font-weight="bold">🎂 회원 생일 축하 이벤트</text>
  <text x="540" y="335" font-family="Arial" font-size="13" fill="#6c757d">생일 맞은 회원에게 특별 선물 증정</text>

  <rect x="540" y="350" width="60" height="22" rx="4" fill="#0dcaf0"/>
  <text x="570" y="365" font-family="Arial" font-size="11" fill="#212529" text-anchor="middle">생일</text>

  <rect x="610" y="350" width="70" height="22" rx="4" fill="#ffc107"/>
  <text x="645" y="365" font-family="Arial" font-size="11" fill="#212529" text-anchor="middle">예정</text>

  <rect x="690" y="350" width="15" height="22" fill="transparent"/>
  <text x="695" y="365" font-family="Arial" font-size="20" fill="#198754">✓</text>
  <text x="710" y="365" font-family="Arial" font-size="11" fill="#6c757d">공개</text>

  <text x="540" y="395" font-family="Arial" font-size="12" fill="#495057" font-weight="600">시작:</text>
  <text x="580" y="395" font-family="Arial" font-size="12" fill="#6c757d">2025-02-01 00:00</text>
  <text x="730" y="395" font-family="Arial" font-size="12" fill="#495057" font-weight="600">종료:</text>
  <text x="770" y="395" font-family="Arial" font-size="12" fill="#6c757d">2025-02-28 23:59</text>

  <text x="540" y="415" font-family="Arial" font-size="11" fill="#adb5bd">생성일: 2025-01-15 | 관리자: 운영진A</text>
</svg>

</details>

---

### 3. 상점 관리 페이지

<details>
<summary>📸 화면 보기</summary>


<svg width="1000" height="700" xmlns="http://www.w3.org/2000/svg">
  <!-- 배경 -->
  <rect width="1000" height="700" fill="#f8f9fa"/>

  <!-- 네비게이션 바 -->
  <rect width="1000" height="60" fill="#212529"/>
  <text x="20" y="38" font-family="Arial" font-size="18" fill="white" font-weight="bold">✨ 마녀봇 관리</text>
  <text x="200" y="38" font-family="Arial" font-size="14" fill="#6c757d">대시보드</text>
  <text x="300" y="38" font-family="Arial" font-size="14" fill="#adb5bd">상점</text>

  <!-- 제목 -->
  <text x="40" y="110" font-family="Arial" font-size="24" fill="#333" font-weight="bold">상점 관리</text>
  <text x="40" y="135" font-family="Arial" font-size="13" fill="#6c757d">상점 아이템을 조회하고 관리합니다</text>

  <!-- 통계 카드들 -->
  <rect x="40" y="160" width="300" height="100" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="60" y="190" font-family="Arial" font-size="13" fill="#6c757d">전체 아이템</text>
  <text x="60" y="225" font-family="Arial" font-size="32" fill="#333" font-weight="bold">18</text>
  <text x="290" y="235" font-family="Arial" font-size="36" fill="#0d6efd">📦</text>

  <rect x="360" y="160" width="300" height="100" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="380" y="190" font-family="Arial" font-size="13" fill="#6c757d">활성 아이템</text>
  <text x="380" y="225" font-family="Arial" font-size="32" fill="#333" font-weight="bold">14</text>
  <text x="610" y="235" font-family="Arial" font-size="36" fill="#198754">✓</text>

  <rect x="680" y="160" width="300" height="100" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="700" y="190" font-family="Arial" font-size="13" fill="#6c757d">비활성 아이템</text>
  <text x="700" y="225" font-family="Arial" font-size="32" fill="#333" font-weight="bold">4</text>
  <text x="930" y="235" font-family="Arial" font-size="36" fill="#6c757d">✕</text>

  <!-- 아이템 카드 1 -->
  <rect x="40" y="280" width="300" height="200" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="60" y="310" font-family="Arial" font-size="16" fill="#333" font-weight="bold">🎁 행운의 상자</text>
  <text x="60" y="335" font-family="Arial" font-size="12" fill="#6c757d">랜덤 보상이 들어있는 신비한</text>
  <text x="60" y="350" font-family="Arial" font-size="12" fill="#6c757d">상자입니다</text>

  <rect x="280" y="295" width="50" height="22" rx="4" fill="#198754"/>
  <text x="305" y="310" font-family="Arial" font-size="11" fill="white" text-anchor="middle">활성</text>

  <rect x="60" y="375" width="120" height="50" rx="6" fill="#f8f9fa"/>
  <text x="120" y="395" font-family="Arial" font-size="11" fill="#6c757d" text-anchor="middle">가격</text>
  <text x="120" y="415" font-family="Arial" font-size="16" fill="#0d6efd" text-anchor="middle" font-weight="bold">5,000원</text>

  <rect x="190" y="375" width="120" height="50" rx="6" fill="#f8f9fa"/>
  <text x="250" y="395" font-family="Arial" font-size="11" fill="#6c757d" text-anchor="middle">ID</text>
  <text x="250" y="415" font-family="Arial" font-size="16" fill="#495057" text-anchor="middle" font-weight="bold">1</text>

  <line x1="60" y1="440" x2="310" y2="440" stroke="#dee2e6" stroke-width="1"/>
  <text x="60" y="460" font-family="Arial" font-size="11" fill="#adb5bd">생성: 2025-01-10 | 마녀봇</text>

  <!-- 아이템 카드 2 -->
  <rect x="360" y="280" width="300" height="200" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))"/>
  <text x="380" y="310" font-family="Arial" font-size="16" fill="#333" font-weight="bold">⭐ 특별 칭호</text>
  <text x="380" y="335" font-family="Arial" font-size="12" fill="#6c757d">프로필에 표시되는 특별한</text>
  <text x="380" y="350" font-family="Arial" font-size="12" fill="#6c757d">칭호를 획득합니다</text>

  <rect x="600" y="295" width="50" height="22" rx="4" fill="#198754"/>
  <text x="625" y="310" font-family="Arial" font-size="11" fill="white" text-anchor="middle">활성</text>

  <rect x="380" y="375" width="120" height="50" rx="6" fill="#f8f9fa"/>
  <text x="440" y="395" font-family="Arial" font-size="11" fill="#6c757d" text-anchor="middle">가격</text>
  <text x="440" y="415" font-family="Arial" font-size="16" fill="#0d6efd" text-anchor="middle" font-weight="bold">10,000원</text>

  <rect x="510" y="375" width="120" height="50" rx="6" fill="#f8f9fa"/>
  <text x="570" y="395" font-family="Arial" font-size="11" fill="#6c757d" text-anchor="middle">ID</text>
  <text x="570" y="415" font-family="Arial" font-size="16" fill="#495057" text-anchor="middle" font-weight="bold">2</text>

  <line x1="380" y1="440" x2="630" y2="440" stroke="#dee2e6" stroke-width="1"/>
  <text x="380" y="460" font-family="Arial" font-size="11" fill="#adb5bd">생성: 2025-01-08 | 운영진A</text>

  <!-- 아이템 카드 3 (비활성) -->
  <rect x="680" y="280" width="300" height="200" rx="8" fill="white" filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.1))" opacity="0.7"/>
  <text x="700" y="310" font-family="Arial" font-size="16" fill="#333" font-weight="bold">🎨 프로필 배경</text>
  <text x="700" y="335" font-family="Arial" font-size="12" fill="#6c757d">프로필 배경을 변경할 수</text>
  <text x="700" y="350" font-family="Arial" font-size="12" fill="#6c757d">있습니다</text>

  <rect x="920" y="295" width="50" height="22" rx="4" fill="#6c757d"/>
  <text x="945" y="310" font-family="Arial" font-size="11" fill="white" text-anchor="middle">비활성</text>

  <rect x="700" y="375" width="120" height="50" rx="6" fill="#f8f9fa"/>
  <text x="760" y="395" font-family="Arial" font-size="11" fill="#6c757d" text-anchor="middle">가격</text>
  <text x="760" y="415" font-family="Arial" font-size="16" fill="#0d6efd" text-anchor="middle" font-weight="bold">8,000원</text>

  <rect x="830" y="375" width="120" height="50" rx="6" fill="#f8f9fa"/>
  <text x="890" y="395" font-family="Arial" font-size="11" fill="#6c757d" text-anchor="middle">ID</text>
  <text x="890" y="415" font-family="Arial" font-size="16" fill="#495057" text-anchor="middle" font-weight="bold">3</text>

  <line x1="700" y1="440" x2="950" y2="440" stroke="#dee2e6" stroke-width="1"/>
  <text x="700" y="460" font-family="Arial" font-size="11" fill="#adb5bd">수정: 2025-01-12 | 운영진B</text>
</svg>

</details>

---

## 💡 사용 팁

- 모든 페이지는 반응형 디자인으로 태블릿과 모바일에서도 사용 가능합니다
- Bootstrap 5 기반의 깔끔한 UI로 직관적으로 사용할 수 있습니다
- 각 페이지에는 검색, 필터링, 페이지네이션 기능이 제공됩니다
