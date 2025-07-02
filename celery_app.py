# celery_app.py
from celery import Celery
from app import app, db  # 从主应用导入


def make_celery(app):
    # 创建 Celery 实例
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )

    # 从 Flask 配置更新 Celery
    celery.conf.update(app.config)

    # 创建任务上下文（确保应用上下文）
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# 初始化 Celery
celery = make_celery(app)

# 导入任务（必须放在最后）
from tasks.password_task import update_all_hosts_passwords
from tasks.daily_host_collect import daily_host_collect