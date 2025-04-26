from datetime import datetime
from app import db
from app.models.user import User

class Consultant(db.Model):
    """
    咨询师模型
    
    @property id - 咨询师ID
    @property user_id - 关联的用户ID
    @property type - 咨询师类型（全职/兼职）
    @property verified - 是否已认证
    @property store_id - 关联的门店ID（全职咨询师）
    @property certification - 认证信息
    @property created_at - 创建时间
    @property updated_at - 更新时间
    """
    __tablename__ = 'consultants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(20))  # fulltime 或 parttime
    verified = db.Column(db.Boolean, default=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    certification = db.Column(db.Text)  # JSON存储认证信息
    
    # 个人简介
    bio = db.Column(db.Text)
    
    # 专业领域，如种植/正畸等，逗号分隔
    specialties = db.Column(db.String(256))
    
    # 评分
    rating = db.Column(db.Float, default=5.0)
    
    # 联系方式
    contact_info = db.Column(db.String(128))
    wechat = db.Column(db.String(64))
    
    # 工作时间
    working_hours = db.Column(db.String(256))
    
    # 教育背景
    education = db.Column(db.Text)
    
    # 专业证书
    certifications = db.Column(db.Text)
    
    # 工作经验
    experience = db.Column(db.Text)
    
    # 创建和更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('consultant_profile', uselist=False))
    store = db.relationship('Store', backref=db.backref('consultants', lazy='dynamic'))
    clients = db.relationship('Client', backref='assigned_consultant', lazy='dynamic', 
                              foreign_keys='Client.assigned_consultant_id')
    
    # 兼职咨询师的关联全职咨询师(指导关系)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('consultants.id'))
    subordinates = db.relationship('Consultant', backref=db.backref('supervisor', remote_side=[id]), 
                                   lazy='dynamic')
    
    def __repr__(self):
        return f'<Consultant {self.user.username} ({self.type})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'type': self.type,
            'verified': self.verified,
            'store_id': self.store_id,
            'bio': self.bio,
            'specialties': self.specialties,
            'rating': self.rating,
            'contact_info': self.contact_info,
            'wechat': self.wechat,
            'working_hours': self.working_hours,
            'education': self.education,
            'certifications': self.certifications,
            'experience': self.experience,
            'supervisor_id': self.supervisor_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 