import pytest
from app import app as test_app
from models import Host, IDC, City, db


@pytest.fixture
def app():
    app = test_app
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///host.db:',
        'CELERY_ALWAYS_EAGER': True
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_data(app):
    with app.app_context():
        # 创建测试数据
        city = City(city_name="Test City")
        db.session.add(city)
        db.session.commit()

        idc = IDC(IDC_name="Test IDC", city_id=city.id)
        db.session.add(idc)
        db.session.commit()

        host = Host(
            host_name="Test Host",
            ip_address="192.168.1.1",
            IDC_id=idc.id,
            root_password="initial_password"
        )
        db.session.add(host)
        db.session.commit()

        return host


def test_generate_secure_password():
    from tasks.password_task import generate_secure_password
    password = generate_secure_password()
    assert len(password) >= 12
    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?~' for c in password)
