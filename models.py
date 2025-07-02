from datetime import datetime
from app import db, app
from cryptography.fernet import Fernet
from sqlalchemy.exc import IntegrityError
import bcrypt

def encrypt(value, encryptionKey):
    return Fernet(encryptionKey).encrypt(bytes(value, "utf-8"))

def decrypt(value, encryptionKey):
    return Fernet(encryptionKey).decrypt(value).decode("utf-8")

class City(db.Model):
    __tablename__ = 'tblCities'
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(length=100), nullable=False)

    idcs = db.relationship("IDC", backref="city", cascade="all, delete-orphan")

    def __init__(self, city_name):
        self.city_name = city_name

    # 增
    @classmethod
    def create(cls, city_name):
        if not city_name:
            raise ValueError("City name is required")
        if cls.query.filter_by(city_name=city_name).first():
            raise ValueError(f"City '{city_name}' already exists")
        new_city = cls(city_name)
        db.session.add(new_city)
        db.session.commit()
        return new_city

    # 删
    @classmethod
    def delete_by_id(cls, city_id):
        city = cls.query.get(city_id)
        if not city:
            raise ValueError(f"City with ID {city_id} not found")
        if city.idcs:
            raise ValueError("Cannot delete city with associated IDCs")

        db.session.delete(city)
        db.session.commit()

    @classmethod
    def delete_by_name(cls, city_name):
        city = cls.query.filter_by(city_name=city_name).first()
        if not city:
            raise ValueError(f"City '{city_name}' not found")
        if city.idcs:
            raise ValueError("Cannot delete city with associated IDCs")

        db.session.delete(city)
        db.session.commit()

    # 改
    @classmethod
    def update(cls, city_id, new_name):
        if not new_name:
            raise ValueError("New city name is required")
        city = cls.query.get(city_id)
        if not city:
            raise ValueError(f"City with ID {city_id} not found")
        if city.city_name == new_name:
            return city
        if cls.query.filter_by(city_name=new_name).first():
            raise ValueError(f"City '{new_name}' already exists")

        city.city_name = new_name
        db.session.commit()
        return city

    # 查
    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, city_id):
        return cls.query.get(city_id)

    @classmethod
    def get_by_name(cls, city_name):
        return cls.query.filter_by(city_name=city_name).first()

class IDC(db.Model):
    __tablename__ = 'tblIDC'
    id = db.Column(db.Integer, primary_key=True)
    IDC_name = db.Column(db.String(length=100), nullable=False, unique=True)
    city_id = db.Column(db.Integer, db.ForeignKey("tblCities.id"), nullable=False)

    host = db.relationship("Host", backref="idc", cascade="all, delete-orphan")

    def __init__(self, IDC_name, city_id):
        self.IDC_name = IDC_name
        self.city_id = city_id

    # 增 (需验证城市存在)
    @classmethod
    def create(cls, idc_name, city_id):
        if not idc_name:
            raise ValueError("IDC name is required")
        if not City.get_by_id(city_id):
            raise ValueError(f"City with ID {city_id} does not exist")
        if cls.query.filter_by(IDC_name=idc_name).first():
            raise ValueError(f"IDC '{idc_name}' already exists")

        new_idc = cls(idc_name, city_id)
        db.session.add(new_idc)
        db.session.commit()
        return new_idc

    # 删
    @classmethod
    def delete_by_id(cls, idc_id):
        idc = cls.query.get(idc_id)
        if not idc:
            raise ValueError(f"IDC with ID {idc_id} not found")

        db.session.delete(idc)
        db.session.commit()

    @classmethod
    def delete_by_name(cls, idc_name):
        idc = cls.query.filter_by(IDC_name=idc_name).first()
        if not idc:
            raise ValueError(f"IDC {idc_name} not found")

        db.session.delete(idc)
        db.session.commit()

    @classmethod
    def update(cls, idc_id, new_name=None, new_city_id=None):
        idc = cls.query.get(idc_id)
        if not idc:
            raise ValueError(f"IDC with ID {idc_id} not found")

        if new_name:
            if idc.IDC_name != new_name and cls.query.filter_by(IDC_name=new_name).first():
                raise ValueError(f"IDC '{new_name}' already exists")
            idc.IDC_name = new_name

        if new_city_id:
            if not City.get_by_id(new_city_id):
                raise ValueError(f"City with ID {new_city_id} does not exist")
            idc.city_id = new_city_id

        db.session.commit()
        return idc

    # 查
    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, idc_id):
        return cls.query.get(idc_id)

    @classmethod
    def get_by_name(cls, idc_name):
        return cls.query.filter_by(IDC_name=idc_name).first()

class Host(db.Model):
    __tablename__ = 'tblHost'
    id = db.Column(db.Integer, primary_key=True)
    host_name = db.Column(db.String(length=100), nullable=False)
    ip_address = db.Column(db.String(length=50), nullable=False, unique=True)
    IDC_id = db.Column(db.Integer, db.ForeignKey("tblIDC.id"), nullable=False)
    root_password = db.Column(db.String(length=100), nullable=False)
    encryption_key = db.Column(db.String(length=100), nullable=False)
    last_update_password = db.Column(db.DateTime, nullable=False)

    def __init__(self, host_name, ip_address, IDC_id, root_password):
        self.host_name = host_name
        self.ip_address = ip_address
        self.IDC_id = IDC_id
        self.root_password = bcrypt.hashpw(root_password.encode("utf-8"), bcrypt.gensalt())
        self.encryption_key = Fernet.generate_key()
        self.last_update_password = datetime.now()

    @classmethod
    def create(cls, host_name, ip_address, idc_id, root_password):
        if not IDC.get_by_id(idc_id):
            raise ValueError(f"IDC with ID {idc_id} does not exist")

        try:
            new_host = cls(host_name, ip_address, idc_id, root_password)
            db.session.add(new_host)
            db.session.commit()
            return new_host
        except IntegrityError:
            db.session.rollback()
            raise ValueError("IP address must be unique")

    @classmethod
    def delete_by_id(cls, host_id):
        host = cls.query.get(host_id)
        if not host:
            raise ValueError(f"Host with ID {host_id} not found")

        db.session.delete(host)
        db.session.commit()

    @classmethod
    def delete_by_ip(cls, host_ip):
        host = cls.query.filter_by(ip_address=host_ip).first()
        if not host:
            raise ValueError(f"Host with IP {host_ip} not found")

        db.session.delete(host)
        db.session.commit()

    @classmethod
    def update(cls, host_id, host_name=None, ip_address=None, idc_id=None, root_password=None):
        host = cls.query.get(host_id)
        if not host:
            raise ValueError(f"Host with ID {host_id} not found")

        if host_name:
            host.host_name = host_name

        if ip_address and ip_address != host.ip_address:
            if cls.query.filter_by(ip_address=ip_address).first():
                raise ValueError("IP address must be unique")
            host.ip_address = ip_address

        if idc_id:
            if not IDC.get_by_id(idc_id):
                raise ValueError(f"IDC with ID {idc_id} does not exist")
            host.IDC_id = idc_id

        if root_password:
            # 更新密码时重新生成加密密钥并更新时间戳
            host.root_password = bcrypt.hashpw(root_password.encode("utf-8"), bcrypt.gensalt())
            host.encryption_key = Fernet.generate_key()
            host.last_update_password = datetime.now()

        db.session.commit()
        return host

    # 查
    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, host_id):
        return cls.query.get(host_id)

    @classmethod
    def get_by_name(cls, host_name):
        return cls.query.filter_by(host_name=host_name).first()


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        # 创建深圳
        sz_city = City(city_name="深圳")
        db.session.add(sz_city)
        db.session.commit()

        # 创建深圳1号机房
        sz_idc = IDC(IDC_name="深圳1号机房", city_id=sz_city.id)
        db.session.add(sz_idc)
        db.session.commit()

        # 创建主机、
        host = Host(
            host_name="001",
            ip_address="0.0.0.0",
            IDC_id=sz_idc.id,
            root_password="a123456"
        )
        db.session.add(host)
        db.session.commit()