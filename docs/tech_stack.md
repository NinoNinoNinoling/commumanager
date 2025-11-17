# 기술 스택

## 인프라
- 오라클 클라우드 (Ampere A1 4core/24GB, 춘천, 무료)
- 대안: Hetzner €4.5/월, Contabo €6.99/월
- DuckDNS (무료 도메인) + Let's Encrypt SSL
- SendGrid (무료 SMTP, 월 100통)

## 마스토돈 (휘핑 에디션)
- 마스토돈 v4.2.1 기반
- Ruby 3.2.2, Node.js 16.20.2
- PostgreSQL 12.16+, Redis 5.0.7+

## 경제 봇
- Python 3.9+
- Mastodon.py, psycopg2, sqlite3
- systemd + cron

```
economy_bot/
├── reward_bot.py
├── activity_checker.py
├── command_handler.py
├── game_engine.py
└── database.py
```

## 관리자 웹
- Flask 3.x + Bootstrap 5
- Mastodon OAuth
- Chart.js

## 데이터베이스
- PostgreSQL: 읽기 전용 (마스토돈 유저/답글 데이터)
- SQLite: 경제 시스템 전용 (재화, 거래, 경고, 상점)

## 네트워크
```
Internet → DuckDNS → SSL → Nginx
                              ├─ Mastodon (3000)
                              ├─ Streaming (4000)
                              └─ Admin Web (5000)
```

## 백업
- SQLite: 매일 3시
- PostgreSQL: 주 1회
- 30일 자동 삭제
