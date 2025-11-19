"""
Celery 설정

Broker: Redis
Result Backend: Redis
Timezone: Asia/Seoul
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Broker 설정
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# 타임존
timezone = 'Asia/Seoul'
enable_utc = False

# Task 설정
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# Worker 설정
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000

# 로그
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s'
