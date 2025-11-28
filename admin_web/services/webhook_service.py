import os
import logging
import json
import sys
from mastodon import Mastodon
from admin_web.models.user import User
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository

def force_print(msg):
    print(f"[Service] {msg}", file=sys.stdout, flush=True)

class WebhookService:
    def __init__(self, db_path: str = 'economy.db'):
        self.user_repo = UserRepository(db_path)
        self.admin_log_repo = AdminLogRepository(db_path)
        self.api_base_url = os.getenv('MASTODON_INSTANCE_URL', 'https://testmast.duckdns.org')
        self.agents = []

        # 🤖 [봇 군단 소집] 팔로우 전담 요원들 (DM 기능 삭제됨)
        
        # 1. 👑 어드민
        admin_token = os.getenv('MASTODON_ACCESS_TOKEN')
        if admin_token:
            self.agents.append({'name': '👑 System Admin', 'token': admin_token})

        # 2. 🤖 시스템 봇
        sys_token = os.getenv('BOT_ACCESS_TOKEN')
        if sys_token:
            self.agents.append({'name': '🤖 System Bot', 'token': sys_token})

        # 3. 📖 스토리 봇
        story_token = os.getenv('STORY_ACCESS_TOKEN')
        if story_token:
            self.agents.append({'name': '📖 Story Bot', 'token': story_token})

        # 4. 👁️ 감독 봇
        sup_token = os.getenv('SUPERVISOR_ACCESS_TOKEN')
        if sup_token:
            self.agents.append({'name': '👁️ Supervisor Bot', 'token': sup_token})

    def handle_account_created(self, webhook_data: dict):
        obj = webhook_data.get('object', {})
        mastodon_id = obj.get('id')
        username = obj.get('username')
        
        if not mastodon_id or not username:
            force_print("❌ 데이터 누락")
            return

        # 1. DB 저장
        if not self.user_repo.find_by_id(mastodon_id):
            new_user = User(mastodon_id=mastodon_id, username=username, display_name=username, role='user')
            self.user_repo.create(new_user)
            self.admin_log_repo.create_log(
                admin_name='system', 
                action_type='webhook_account_created', 
                target_user=str(mastodon_id), 
                details=json.dumps({'username': username}, ensure_ascii=False)
            )
            force_print(f"✅ DB 등록: {username}")
        else:
            force_print(f"ℹ️ 기존 유저: {username}")

        # 2. 봇 군단 팔로우 실행
        if self.agents:
            force_print(f"🚀 {len(self.agents)}명의 요원이 팔로우를 시작합니다...")
            for agent in self.agents:
                self._perform_follow(agent, mastodon_id)

        return {'status': 'success', 'username': username}

    def _perform_follow(self, agent, target_id):
        """오직 팔로우만 수행"""
        try:
            client = Mastodon(api_base_url=self.api_base_url, access_token=agent['token'])
            client.account_follow(target_id)
            force_print(f"   └─ ✅ [{agent['name']}] 팔로우 완료")
        except Exception as e:
            force_print(f"   └─ ❌ [{agent['name']}] 실패: {e}")
