from datetime import datetime
from app import db

class Message(db.Model):
    """
    消息记录模型
    
    @property id - 消息ID
    @property sender_id - 发送者用户ID
    @property receiver_id - 接收者用户ID
    @property content - 消息内容
    @property msg_type - 消息类型
    @property is_read - 是否已读
    @property created_at - 创建时间
    """
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    msg_type = db.Column(db.String(20), default='text')  # text, image, file, system
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 可能包含的附件
    attachment_url = db.Column(db.String(256))
    
    # 消息情感值（AI分析）
    sentiment_score = db.Column(db.Float)  # -1.0 到 1.0，负面到正面
    
    # 关系
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy='dynamic'))
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_messages', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id} to {self.receiver_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'msg_type': self.msg_type,
            'is_read': self.is_read,
            'attachment_url': self.attachment_url,
            'sentiment_score': self.sentiment_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
class GroupMessage(db.Model):
    """
    群组消息模型，用于咨询师向批量客户发送消息
    """
    __tablename__ = 'group_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    msg_type = db.Column(db.String(20), default='text')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 消息发送的目标组
    target_type = db.Column(db.String(20))  # all_clients, tagged_clients
    target_tags = db.Column(db.String(256))  # 如果是tagged_clients，存储目标标签
    
    # 附件
    attachment_url = db.Column(db.String(256))
    
    # 发送状态
    status = db.Column(db.String(20), default='pending')  # pending, sending, sent, failed
    sent_count = db.Column(db.Integer, default=0)
    
    # 关系
    sender = db.relationship('User', backref=db.backref('sent_group_messages', lazy='dynamic'))
    
    def __repr__(self):
        return f'<GroupMessage {self.id} from {self.sender_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'content': self.content,
            'msg_type': self.msg_type,
            'target_type': self.target_type,
            'target_tags': self.target_tags,
            'attachment_url': self.attachment_url,
            'status': self.status,
            'sent_count': self.sent_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 