import string
from app import db
from models import Host
import random
from celery_app import celery


def generate_secure_password():
    # 定义字符集
    lowercase = string.ascii_lowercase  # 小写字母
    uppercase = string.ascii_uppercase  # 大写字母
    digits = string.digits              # 数字
    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'  # 特殊符号

    # 组合所有字符
    all_chars = lowercase + uppercase + digits + special_chars

    # 随机生成长度（12~16）
    length = random.randint(12, 16)

    # 确保每种字符至少出现一次
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special_chars)
    ]

    # 填充剩余长度
    password += random.choices(all_chars, k=length-4)

    # 打乱字符顺序
    random.shuffle(password)

    return ''.join(password)


@celery.task(name='tasks.password_tasks.update_all_hosts_passwords')
def update_all_hosts_passwords():
    try:
        hosts = Host.query.all()
        for host in hosts:
            new_password = generate_secure_password()
            host.update_password(new_password)

        db.session.commit()
        return {"status": "success", "updated_hosts": len(hosts)}

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": str(e)}