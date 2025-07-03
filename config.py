from celery.schedules import crontab

class Config:
    SECRET_KEY = 'LongAndRandomSecretKey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///host.db'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RECAPTCHA_PUBLIC_KEY = "6Lf41H4iAAAAALCDw0esznqOX1-uxAKABhCYQ51_"
    RECAPTCHA_PRIVATE_KEY = "6Lf41H4iAAAAALw_t1vVYYcr9fUvBkqR7yjZqCwN"

    # Celery 配置
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERYBEAT_SCHEDULE = {
        'update-passwords-every-8-hours': {
            'task': 'tasks.password_tasks.update_all_hosts_passwords',
            'schedule': 28800.0,
        },
        'daily-host-collect': {
            'task': 'tasks.daily_host_collect.daily_host_collect',
            'schedule': crontab(minute=0, hour=0),  # 每天0点
        },
    }