from datetime import datetime
from app import db

class Store(db.Model):
    """
    门店模型
    
    @property id - 门店ID
    @property name - 门店名称
    @property address - 门店地址
    @property contact - 联系电话
    @property description - 门店描述
    @property latitude - 纬度坐标
    @property longitude - 经度坐标
    @property created_at - 创建时间
    @property updated_at - 更新时间
    """
    __tablename__ = 'stores'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    contact = db.Column(db.String(64))
    description = db.Column(db.Text)
    
    # 地理位置
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # 营业时间，JSON格式存储
    business_hours = db.Column(db.Text)
    
    # 门店照片，JSON数组存储
    photos = db.Column(db.Text)
    
    # 专长领域，逗号分隔
    specialties = db.Column(db.String(256))
    
    # 创建和更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 门店状态
    status = db.Column(db.String(20), default='active')  # active, inactive
    
    def __repr__(self):
        return f'<Store {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'contact': self.contact,
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'business_hours': self.business_hours,
            'photos': self.photos,
            'specialties': self.specialties,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 