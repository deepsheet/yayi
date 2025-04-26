from datetime import datetime
from app import db

class Treatment(db.Model):
    """
    治疗记录模型
    
    @property id - 治疗记录ID
    @property client_id - 客户ID
    @property store_id - 门店ID
    @property doctor_id - 医生ID
    @property type - 治疗类型
    @property description - 治疗描述
    @property fee - 治疗费用
    @property status - 治疗状态
    @property appointment_date - 预约日期
    @property created_at - 创建时间
    @property updated_at - 更新时间
    """
    __tablename__ = 'treatments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    
    # 治疗类型和内容
    type = db.Column(db.String(64))  # 如种植、正畸、美白等
    description = db.Column(db.Text)
    
    # 费用和支付信息
    fee = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, partial, paid
    paid_amount = db.Column(db.Float, default=0)
    
    # 治疗状态
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    
    # 预约信息
    appointment_date = db.Column(db.DateTime)
    
    # 创建和更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    store = db.relationship('Store', backref=db.backref('treatments', lazy='dynamic'))
    doctor = db.relationship('Doctor', backref=db.backref('treatments', lazy='dynamic'))
    
    # 记录负责该订单的咨询师信息
    consultant_id = db.Column(db.Integer, db.ForeignKey('consultants.id'))
    consultant = db.relationship('Consultant', backref=db.backref('handled_treatments', lazy='dynamic'),
                                foreign_keys=[consultant_id])
    
    def __repr__(self):
        return f'<Treatment {self.id} for Client {self.client_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'store_id': self.store_id,
            'doctor_id': self.doctor_id,
            'consultant_id': self.consultant_id,
            'type': self.type,
            'description': self.description,
            'fee': self.fee,
            'payment_status': self.payment_status,
            'paid_amount': self.paid_amount,
            'status': self.status,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 