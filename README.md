# 펄사봇 (Pulsa Bot)

휘핑 에디션 마스토돈용 활동량 기반 경제 시스템

## 개요
- 30~50명 규모 폐쇄형 커뮤니티
- 답글 기반 재화 지급
- 활동량 자동 체크 및 경고
- 상점 시스템

## 문서
- [프로젝트 개요](docs/project_overview.md)
- [기능 목록](docs/features.md)
- [기술 스택](docs/tech_stack.md)
- [시스템 아키텍처](docs/architecture.md)
- [데이터베이스](docs/database.md)
- [관리자 웹](docs/admin%20web.md)
- [로드맵](docs/로드맵.md)

## 핵심 기능
1. 활동량 체크 (하루 2회, 오전 5시/오후 12시)
2. 재화 지급 (실시간 답글 감지)
3. 상점 시스템 (아이템 구매)
4. 휴식계 (활동량 체크 제외)

## 기술 스택
- 마스토돈: Ruby 3.2.2
- 봇: Python 3.9+
- 웹: Flask 3.x
- DB: PostgreSQL + SQLite
- 인프라: 오라클 클라우드 (무료)

## 예상 개발 기간
14~21일 (서버 준비 완료 후)
