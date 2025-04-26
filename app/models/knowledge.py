from datetime import datetime
from app import db

class KnowledgeArticle(db.Model):
    """
    知识库文章模型
    
    @property id - 文章ID
    @property title - 标题
    @property content - 内容
    @property category - 分类
    @property tags - 标签
    @property author_id - 作者ID
    @property created_at - 创建时间
    @property updated_at - 更新时间
    """
    __tablename__ = 'knowledge_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64))  # 如种植、正畸、美白等
    tags = db.Column(db.String(256))  # 标签，逗号分隔
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 文章评分和使用次数
    rating = db.Column(db.Float, default=5.0)
    use_count = db.Column(db.Integer, default=0)
    
    # 创建和更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 审核状态
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # 关系
    author = db.relationship('User', backref=db.backref('knowledge_articles', lazy='dynamic'))
    
    def __repr__(self):
        return f'<KnowledgeArticle {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'tags': self.tags,
            'author_id': self.author_id,
            'rating': self.rating,
            'use_count': self.use_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class KnowledgeQA(db.Model):
    """
    知识问答模型
    
    @property id - 问答ID
    @property question - 问题
    @property answer - 回答
    @property category - 分类
    @property tags - 标签
    @property created_at - 创建时间
    @property updated_at - 更新时间
    """
    __tablename__ = 'knowledge_qa'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(512), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64))
    tags = db.Column(db.String(256))
    
    # 问答的源头，是预置的还是来自对话
    source = db.Column(db.String(20), default='preset')  # preset, conversation
    source_id = db.Column(db.Integer)  # 如果来自对话，存储对话ID
    
    # 使用次数和评分
    use_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=5.0)
    
    # 创建和更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 审核状态
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    def __repr__(self):
        return f'<KnowledgeQA {self.question[:30]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'tags': self.tags,
            'source': self.source,
            'source_id': self.source_id,
            'use_count': self.use_count,
            'rating': self.rating,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 