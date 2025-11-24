#!/usr/bin/env python3
"""
OAuth 관리자 추가 스크립트

사용법:
    python3 add_oauth_admin.py <mastodon_acct> [display_name]

예시:
    python3 add_oauth_admin.py admin
    python3 add_oauth_admin.py admin@testmast.duckdns.org "관리자"
    python3 add_oauth_admin.py user@remote.instance "원격 관리자"
"""
import sys
from admin_web.services.oauth_admin_service import OAuthAdminService


def main():
    if len(sys.argv) < 2:
        print("❌ 사용법: python3 add_oauth_admin.py <mastodon_acct> [display_name]")
        print("\n예시:")
        print("  python3 add_oauth_admin.py admin")
        print("  python3 add_oauth_admin.py admin@testmast.duckdns.org \"관리자\"")
        sys.exit(1)

    mastodon_acct = sys.argv[1]
    display_name = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"\n📋 OAuth 관리자 추가")
    print(f"계정: {mastodon_acct}")
    if display_name:
        print(f"표시 이름: {display_name}")
    print()

    try:
        service = OAuthAdminService()
        admin = service.add_admin(
            mastodon_acct=mastodon_acct,
            added_by='system',
            display_name=display_name
        )

        print(f"✅ 관리자 추가 완료!")
        print(f"   ID: {admin.id}")
        print(f"   계정: {admin.mastodon_acct}")
        print(f"   표시 이름: {admin.display_name or '(없음)'}")
        print(f"   추가 시각: {admin.added_at}")
        print()
        print("💡 이제 OAuth 로그인을 시도해보세요!")

    except ValueError as e:
        print(f"❌ 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예기치 않은 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
