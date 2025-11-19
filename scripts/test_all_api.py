#!/usr/bin/env python3
"""
API 자동 테스트 스크립트
모든 REST API 엔드포인트를 자동으로 테스트하고 결과를 보고합니다.
"""
import os
import sys
import json
import time
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

# 프로젝트 루트 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 설정
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api/v1')
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'economy.db')
TIMEOUT = 5  # API 요청 타임아웃 (초)

# ANSI 색상 코드
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ============================================================================
# 유틸리티 함수
# ============================================================================

def print_header(text: str):
    """헤더 출력"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}")
    print(f"{text}")
    print(f"{'=' * 70}{Colors.ENDC}")


def print_success(text: str):
    """성공 메시지 출력"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_failure(text: str):
    """실패 메시지 출력"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """정보 메시지 출력"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text: str):
    """경고 메시지 출력"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def check_server():
    """Flask 서버 동작 확인"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats", timeout=2)
        return True
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False


def get_test_user_ids(limit=5) -> List[str]:
    """테스트용 사용자 ID 목록 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT mastodon_id FROM users LIMIT {limit}")
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return user_ids


def get_test_item_ids(limit=3) -> List[int]:
    """테스트용 아이템 ID 목록 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM items LIMIT {limit}")
    item_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return item_ids


def get_test_event_ids(limit=3) -> List[int]:
    """테스트용 이벤트 ID 목록 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM calendar_events LIMIT {limit}")
    event_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return event_ids


# ============================================================================
# 테스트 케이스
# ============================================================================

class APITester:
    """API 테스트 클래스"""

    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = []
        self.user_ids = []
        self.item_ids = []
        self.event_ids = []

    def test(self, name: str, method: str, endpoint: str, data: Dict = None,
             params: Dict = None, expected_status: int = 200) -> bool:
        """API 엔드포인트 테스트"""
        self.total += 1
        url = f"{BASE_URL}{endpoint}"

        try:
            print(f"\n{Colors.BOLD}[{self.total}] {name}{Colors.ENDC}")
            print(f"   {method.upper()} {endpoint}")

            # 요청 실행
            if method.lower() == 'get':
                response = requests.get(url, params=params, timeout=TIMEOUT)
            elif method.lower() == 'post':
                response = requests.post(url, json=data, timeout=TIMEOUT)
            elif method.lower() == 'put':
                response = requests.put(url, json=data, timeout=TIMEOUT)
            elif method.lower() == 'delete':
                response = requests.delete(url, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # 상태 코드 확인
            if response.status_code != expected_status:
                print_failure(f"상태 코드 불일치: {response.status_code} (expected: {expected_status})")
                print(f"   응답: {response.text[:200]}")
                self.failed += 1
                self.results.append({
                    'name': name,
                    'status': 'FAIL',
                    'reason': f'Status {response.status_code} != {expected_status}'
                })
                return False

            # JSON 응답 확인
            try:
                json_data = response.json()
                print(f"   응답: {json.dumps(json_data, ensure_ascii=False, indent=2)[:300]}...")
            except json.JSONDecodeError:
                if expected_status != 204:  # 204 No Content는 JSON이 없어도 OK
                    print_warning("JSON 파싱 실패")

            print_success(f"성공 (Status {response.status_code})")
            self.passed += 1
            self.results.append({
                'name': name,
                'status': 'PASS',
                'reason': ''
            })
            return True

        except requests.exceptions.Timeout:
            print_failure(f"타임아웃 ({TIMEOUT}초)")
            self.failed += 1
            self.results.append({
                'name': name,
                'status': 'FAIL',
                'reason': 'Timeout'
            })
            return False

        except requests.exceptions.ConnectionError:
            print_failure("서버 연결 실패")
            self.failed += 1
            self.results.append({
                'name': name,
                'status': 'FAIL',
                'reason': 'Connection Error'
            })
            return False

        except Exception as e:
            print_failure(f"오류 발생: {e}")
            self.failed += 1
            self.results.append({
                'name': name,
                'status': 'FAIL',
                'reason': str(e)
            })
            return False

    def run_all_tests(self):
        """모든 API 테스트 실행"""
        print_header("🧪 API 자동 테스트 시작")
        print_info(f"Base URL: {BASE_URL}")
        print_info(f"Timeout: {TIMEOUT}초")

        # 테스트 데이터 로드
        print_info("테스트 데이터 로드 중...")
        self.user_ids = get_test_user_ids(5)
        self.item_ids = get_test_item_ids(3)
        self.event_ids = get_test_event_ids(3)

        if not self.user_ids:
            print_failure("사용자 데이터가 없습니다. seed_test_data.py를 먼저 실행하세요.")
            return

        print_success(f"테스트 데이터 준비 완료: {len(self.user_ids)}명 사용자, {len(self.item_ids)}개 아이템, {len(self.event_ids)}개 이벤트")

        # ====================================================================
        # Dashboard API 테스트
        # ====================================================================
        print_header("📊 Dashboard API")

        self.test(
            "대시보드 통계 조회",
            "GET",
            "/dashboard/stats"
        )

        # ====================================================================
        # Users API 테스트
        # ====================================================================
        print_header("👥 Users API")

        self.test(
            "전체 사용자 목록 조회",
            "GET",
            "/users"
        )

        self.test(
            "사용자 목록 조회 (페이지네이션)",
            "GET",
            "/users",
            params={'page': 1, 'per_page': 10}
        )

        self.test(
            "사용자 목록 조회 (역할 필터)",
            "GET",
            "/users",
            params={'role': 'normal'}
        )

        self.test(
            "사용자 목록 조회 (검색)",
            "GET",
            "/users",
            params={'search': '김'}
        )

        if self.user_ids:
            self.test(
                "특정 사용자 상세 조회",
                "GET",
                f"/users/{self.user_ids[0]}"
            )

        # ====================================================================
        # Transactions API 테스트
        # ====================================================================
        print_header("💰 Transactions API")

        if self.user_ids:
            self.test(
                "사용자 거래 내역 조회",
                "GET",
                f"/users/{self.user_ids[0]}/transactions"
            )

            self.test(
                "사용자 거래 내역 조회 (타입 필터)",
                "GET",
                f"/users/{self.user_ids[0]}/transactions",
                params={'transaction_type': 'earn'}
            )

            self.test(
                "재화 조정 (지급)",
                "POST",
                "/transactions/adjust",
                data={
                    'user_id': self.user_ids[0],
                    'amount': 1000,
                    'description': 'API 테스트 지급',
                    'admin_name': '테스트관리자'
                },
                expected_status=201
            )

            self.test(
                "재화 조정 (차감)",
                "POST",
                "/transactions/adjust",
                data={
                    'user_id': self.user_ids[0],
                    'amount': -500,
                    'description': 'API 테스트 차감',
                    'admin_name': '테스트관리자'
                },
                expected_status=201
            )

        # ====================================================================
        # Warnings API 테스트
        # ====================================================================
        print_header("⚠️  Warnings API")

        if self.user_ids:
            self.test(
                "사용자 경고 내역 조회",
                "GET",
                f"/users/{self.user_ids[0]}/warnings"
            )

            self.test(
                "경고 발송",
                "POST",
                "/warnings",
                data={
                    'user_id': self.user_ids[0],
                    'warning_type': 'activity_low',
                    'message': 'API 테스트 경고',
                    'admin_name': '테스트관리자'
                },
                expected_status=201
            )

        # ====================================================================
        # Vacations API 테스트
        # ====================================================================
        print_header("🏖️  Vacations API")

        self.test(
            "휴가 목록 조회",
            "GET",
            "/vacations"
        )

        self.test(
            "활성 휴가 목록 조회",
            "GET",
            "/vacations",
            params={'active_only': 'true'}
        )

        if self.user_ids:
            self.test(
                "사용자 휴가 내역 조회",
                "GET",
                f"/users/{self.user_ids[0]}/vacations"
            )

            # 휴가 생성
            tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
            week_later = (datetime.now() + timedelta(days=8)).date().isoformat()

            vacation_created = self.test(
                "휴가 생성",
                "POST",
                "/vacations",
                data={
                    'user_id': self.user_ids[0],
                    'start_date': tomorrow,
                    'end_date': week_later,
                    'reason': 'API 테스트 휴가',
                    'admin_name': '테스트관리자'
                },
                expected_status=201
            )

            # 휴가 삭제는 생성 성공 시에만 테스트
            # (실제 ID를 알 수 없으므로 스킵)

        # ====================================================================
        # Calendar API 테스트
        # ====================================================================
        print_header("📅 Calendar API")

        self.test(
            "이벤트 목록 조회",
            "GET",
            "/calendar/events"
        )

        self.test(
            "이벤트 목록 조회 (날짜 범위)",
            "GET",
            "/calendar/events",
            params={
                'start_date': (datetime.now() - timedelta(days=30)).date().isoformat(),
                'end_date': (datetime.now() + timedelta(days=30)).date().isoformat()
            }
        )

        if self.event_ids:
            self.test(
                "특정 이벤트 조회",
                "GET",
                f"/calendar/events/{self.event_ids[0]}"
            )

        # 이벤트 생성
        event_date = (datetime.now() + timedelta(days=10)).date().isoformat()

        self.test(
            "이벤트 생성",
            "POST",
            "/calendar/events",
            data={
                'title': 'API 테스트 이벤트',
                'description': '자동 테스트로 생성된 이벤트',
                'event_date': event_date,
                'event_type': 'general',
                'admin_name': '테스트관리자'
            },
            expected_status=201
        )

        # ====================================================================
        # Items API 테스트
        # ====================================================================
        print_header("🛍️  Items API")

        self.test(
            "아이템 목록 조회",
            "GET",
            "/items"
        )

        self.test(
            "아이템 목록 조회 (카테고리 필터)",
            "GET",
            "/items",
            params={'category': 'cosmetic'}
        )

        self.test(
            "활성 아이템만 조회",
            "GET",
            "/items",
            params={'active_only': 'true'}
        )

        if self.item_ids:
            self.test(
                "특정 아이템 조회",
                "GET",
                f"/items/{self.item_ids[0]}"
            )

        # 아이템 생성
        self.test(
            "아이템 생성",
            "POST",
            "/items",
            data={
                'name': 'API 테스트 아이템',
                'description': '자동 테스트로 생성된 아이템',
                'price': 1000,
                'category': 'test',
                'admin_name': '테스트관리자'
            },
            expected_status=201
        )

        # ====================================================================
        # Settings API 테스트
        # ====================================================================
        print_header("⚙️  Settings API")

        self.test(
            "전체 설정 조회",
            "GET",
            "/settings"
        )

        self.test(
            "특정 설정 조회",
            "GET",
            "/settings/min_replies_48h"
        )

        self.test(
            "설정 업데이트",
            "PUT",
            "/settings/min_replies_48h",
            data={
                'value': '20',
                'admin_name': '테스트관리자'
            }
        )

        # ====================================================================
        # Admin Logs API 테스트
        # ====================================================================
        print_header("📋 Admin Logs API")

        self.test(
            "관리자 로그 목록 조회",
            "GET",
            "/admin-logs"
        )

        self.test(
            "관리자 로그 조회 (페이지네이션)",
            "GET",
            "/admin-logs",
            params={'page': 1, 'per_page': 20}
        )

        self.test(
            "관리자 로그 조회 (액션 타입 필터)",
            "GET",
            "/admin-logs",
            params={'action_type': 'currency_adjust'}
        )

        self.test(
            "관리자 로그 조회 (관리자 이름 필터)",
            "GET",
            "/admin-logs",
            params={'admin_name': '마녀봇'}
        )

    def print_report(self):
        """테스트 결과 리포트 출력"""
        print_header("📊 테스트 결과")

        print(f"\n{Colors.BOLD}총 테스트: {self.total}개{Colors.ENDC}")
        print(f"{Colors.OKGREEN}성공: {self.passed}개{Colors.ENDC}")
        print(f"{Colors.FAIL}실패: {self.failed}개{Colors.ENDC}")

        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"\n{Colors.BOLD}성공률: {success_rate:.1f}%{Colors.ENDC}")

        # 실패한 테스트 목록
        if self.failed > 0:
            print(f"\n{Colors.FAIL}{Colors.BOLD}실패한 테스트:{Colors.ENDC}")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   ❌ {result['name']} - {result['reason']}")

        # 최종 결과
        print("\n" + "=" * 70)
        if self.failed == 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 모든 테스트 통과!{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠️  일부 테스트 실패{Colors.ENDC}")
        print("=" * 70 + "\n")


# ============================================================================
# 메인 실행
# ============================================================================

def main():
    """메인 함수"""
    print_header("🌟 마녀봇 API 자동 테스트 스크립트")

    # 서버 상태 확인
    print_info("Flask 서버 확인 중...")
    if not check_server():
        print_failure("Flask 서버가 실행되지 않았습니다!")
        print_info("다음 명령어로 서버를 시작하세요:")
        print(f"\n    {Colors.BOLD}python -m admin_web.app{Colors.ENDC}\n")
        return 1

    print_success("Flask 서버 연결 성공")

    # DB 파일 존재 확인
    if not os.path.exists(DB_PATH):
        print_failure(f"데이터베이스 파일이 없습니다: {DB_PATH}")
        return 1

    # 테스트 실행
    tester = APITester()
    tester.run_all_tests()

    # 결과 리포트
    tester.print_report()

    return 0 if tester.failed == 0 else 1


if __name__ == '__main__':
    exit(main())
