from datetime import datetime
from app import db
from app.models.user import User

class Client(db.Model):
    """
    客户模型
    
    @property id - 客户ID
    @property user_id - 关联的用户ID
    @property name - 客户姓名
    @property gender - 性别
    @property age - 年龄
    @property address - 地址
    @property contact_info - 联系方式
    @property created_at - 创建时间
    @property updated_at - 更新时间
    """
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(64))
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    address = db.Column(db.String(256))
    contact_info = db.Column(db.String(128))
    
    # 客户标签，逗号分隔
    tags = db.Column(db.String(256))
    
    # 记录客户是否为"孤儿客户"
    is_orphan = db.Column(db.Boolean, default=False)
    
    # 最后一次与咨询师沟通的时间
    last_contact = db.Column(db.DateTime)
    
    # 创建和更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('client_profile', uselist=False))
    assigned_consultant_id = db.Column(db.Integer, db.ForeignKey('consultants.id'))
    treatments = db.relationship('Treatment', backref='client', lazy='dynamic')
    
    def __repr__(self):
        return f'<Client {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'gender': self.gender,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'address': self.address,
            'contact_info': self.contact_info,
            'tags': self.tags,
            'is_orphan': self.is_orphan,
            'last_contact': self.last_contact.isoformat() if self.last_contact else None,
            'assigned_consultant_id': self.assigned_consultant_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def check_orphan_status(cls):
        """检查并更新孤儿客户状态"""
        from sqlalchemy import func
        from datetime import timedelta
        
        # 查找30天未联系的客户
        threshold_date = datetime.utcnow() - timedelta(days=30)
        orphan_clients = cls.query.filter(
            (cls.last_contact < threshold_date) & (cls.is_orphan == False)
        ).all()
        
        # 更新为孤儿客户
        for client in orphan_clients:
            client.is_orphan = True
            
        db.session.commit()
        return len(orphan_clients) 