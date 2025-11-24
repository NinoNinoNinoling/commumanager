#!/usr/bin/env python3
"""
OAuth 관리자 목록 조회 스크립트

사용법:
    python3 list_oauth_admins.py
"""
from admin_web.services.oauth_admin_service import OAuthAdminService


def main():
    service = OAuthAdminService()
    admins = service.get_all_admins()

    print("\n📋 OAuth 관리자 목록\n")
    print("=" * 80)

    if not admins:
        print("등록된 관리자가 없습니다.")
        print("\n💡 관리자를 추가하려면:")
        print("   python3 add_oauth_admin.py <mastodon_acct> [display_name]")
    else:
        for admin in admins:
            status = "✅ 활성" if admin.is_active else "❌ 비활성"
            print(f"[{admin.id}] {status} {admin.mastodon_acct}")
            if admin.display_name:
                print(f"    표시 이름: {admin.display_name}")
            print(f"    추가 시각: {admin.added_at}")
            print(f"    추가한 관리자: {admin.added_by}")
            if admin.last_login_at:
                print(f"    마지막 로그인: {admin.last_login_at}")
            print()

    print("=" * 80)
    print(f"총 {len(admins)}명의 관리자 (활성: {sum(1 for a in admins if a.is_active)}명)\n")


if __name__ == '__main__':
    main()
