from celery_app import celery
import tasks.password_task
import tasks.daily_host_collect

if __name__ == '__main__':
    celery