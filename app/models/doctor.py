from datetime import datetime
from app import db

class Doctor(db.Model):
    """
    医生模型
    
    @property id - 医生ID
    @property name - 医生姓名
    @property title - 职称
    @property specialty - 专业领域
    @property bio - 个人简介
    @property store_id - 所属门店ID
    @property created_at - 创建时间
    @property updated_at - 更新时间
    """
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(64))  # 如主任医师、副主任医师等
    specialty = db.Column(db.String(128))  # 专业领域，如种植、正畸等
    bio = db.Column(db.Text)  # 个人简介
    avatar = db.Column(db.String(200))  # 医生头像
    
    # 所属门店
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    store = db.relationship('Store', backref=db.backref('doctors', lazy='dynamic'))
    
    # 创建和更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 工作状态
    status = db.Column(db.String(20), default='available')  # available, busy, off_duty
    
    # 评价相关
    rating = db.Column(db.Float, default=5.0)
    rating_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Doctor {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'specialty': self.specialty,
            'bio': self.bio,
            'avatar': self.avatar,
            'store_id': self.store_id,
            'status': self.status,
            'rating': self.rating,
            'rating_count': self.rating_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 