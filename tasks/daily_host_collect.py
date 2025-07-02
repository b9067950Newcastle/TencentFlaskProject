from celery_app import celery
from app import db
from models import IDC, Host, HostStat

@celery.task
def daily_host_collect():
    """每天统计各机房主机数量"""
    from datetime import date
    today = date.today()

    # 查询所有机房的主机数量
    stats = db.session.query(
        IDC.city_id,
        IDC.id,
        db.func.count(IDC.id)
    ).join(Host).group_by(IDC.id).all()

    # 保存统计结果
    for city_id, idc_id, count in stats:
        stat = HostStat(
            date=today,
            city_id=city_id,
            data_center_id=idc_id,
            host_count=count
        )
        db.session.add(stat)
    db.session.commit()
    return f"Recorded {len(stats)} stats"