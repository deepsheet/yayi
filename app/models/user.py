from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    """
    用户基类模型
    
    @property id - 用户ID
    @property username - 用户名
    @property email - 邮箱
    @property phone - 手机号
    @property password_hash - 密码哈希
    @property is_active - 账户是否激活
    @property created_at - 创建时间
    @property updated_at - 更新时间
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='client')  # client, consultant, fulltime_consultant, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 用户头像
    avatar = db.Column(db.String(200))
    
    # 用户验证状态
    is_verified = db.Column(db.Boolean, default=False)
    
    @property
    def password(self):
        raise AttributeError('密码不是可读属性')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'is_active': self.is_active,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'avatar': self.avatar
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 