"""
治疗记录相关API
"""
from flask import request, g
from app import db
from app.models import Treatment, Client, Doctor, Store, Consultant
from app.api import api_bp
from app.utils.response import success_response, error_response, paginated_response
from app.utils.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.utils.validators import validate_required_fields
from app.api.authentication import token_required
from datetime import datetime
import json

@api_bp.route('/treatments', methods=['GET'])
@token_required
def get_treatments():
    """
    获取治疗记录列表
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    client_id = request.args.get('client_id', type=int)
    doctor_id = request.args.get('doctor_id', type=int)
    store_id = request.args.get('store_id', type=int)
    status = request.args.get('status')  # scheduled/in_progress/completed/cancelled
    type_filter = request.args.get('type')
    
    # 构建查询
    query = Treatment.query
    
    if client_id:
        query = query.filter_by(client_id=client_id)
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    if store_id:
        query = query.filter_by(store_id=store_id)
    if status:
        query = query.filter_by(status=status)
    if type_filter:
        query = query.filter_by(type=type_filter)
    
    # 执行分页查询
    pagination = query.paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[treatment.to_dict() for treatment in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取治疗记录列表成功"
    )

@api_bp.route('/treatments/<int:treatment_id>', methods=['GET'])
@token_required
def get_treatment(treatment_id):
    """
    获取治疗记录详情
    
    @param {int} treatment_id - 治疗记录ID
    @return {tuple} - (JSON响应, 状态码)
    """
    treatment = Treatment.query.get_or_404(treatment_id)
    
    # 检查权限
    if g.current_user.role == 'client' and g.current_user.id != treatment.client.user_id:
        return error_response("无权限访问", status_code=403)
    
    return success_response(
        data=treatment.to_dict(),
        message="获取治疗记录详情成功"
    )

@api_bp.route('/treatments', methods=['POST'])
@token_required
def create_treatment():
    """
    创建新治疗记录
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role not in ['admin', 'consultant', 'fulltime_consultant']:
        return error_response("无权限操作", status_code=403)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['client_id', 'doctor_id', 'store_id', 'type', 'appointment_date']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 检查相关记录是否存在
    client = Client.query.get(data['client_id'])
    if not client:
        return error_response("客户不存在", status_code=400)
    
    doctor = Doctor.query.get(data['doctor_id'])
    if not doctor:
        return error_response("医生不存在", status_code=400)
    
    store = Store.query.get(data['store_id'])
    if not store:
        return error_response("门店不存在", status_code=400)
    
    # 创建新治疗记录
    new_treatment = Treatment(
        client_id=data['client_id'],
        doctor_id=data['doctor_id'],
        store_id=data['store_id'],
        type=data['type'],
        description=data.get('description'),
        fee=data.get('fee'),
        appointment_date=datetime.fromisoformat(data['appointment_date']),
        status='scheduled',
        consultant_id=g.current_user.id if g.current_user.role in ['consultant', 'fulltime_consultant'] else None
    )
    
    db.session.add(new_treatment)
    db.session.commit()
    
    return success_response(
        data=new_treatment.to_dict(),
        message="创建治疗记录成功",
        status_code=201
    )

@api_bp.route('/treatments/<int:treatment_id>', methods=['PUT'])
@token_required
def update_treatment(treatment_id):
    """
    更新治疗记录
    
    @param {int} treatment_id - 治疗记录ID
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role not in ['admin', 'consultant', 'fulltime_consultant']:
        return error_response("无权限操作", status_code=403)
    
    treatment = Treatment.query.get_or_404(treatment_id)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['type', 'appointment_date']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 更新治疗记录
    treatment.type = data['type']
    treatment.description = data.get('description')
    treatment.fee = data.get('fee')
    treatment.appointment_date = datetime.fromisoformat(data['appointment_date'])
    treatment.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return success_response(
        data=treatment.to_dict(),
        message="更新治疗记录成功"
    )

@api_bp.route('/treatments/<int:treatment_id>/status', methods=['PUT'])
@token_required
def update_treatment_status(treatment_id):
    """
    更新治疗记录状态
    
    @param {int} treatment_id - 治疗记录ID
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role not in ['admin', 'consultant', 'fulltime_consultant']:
        return error_response("无权限操作", status_code=403)
    
    treatment = Treatment.query.get_or_404(treatment_id)
    
    # 验证必填字段
    data = request.get_json()
    if 'status' not in data or data['status'] not in ['scheduled', 'in_progress', 'completed', 'cancelled']:
        return error_response("无效的状态值", status_code=400)
    
    # 更新治疗记录状态
    treatment.status = data['status']
    treatment.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return success_response(
        data=treatment.to_dict(),
        message="更新治疗记录状态成功"
    )

@api_bp.route('/treatments/<int:treatment_id>/payment', methods=['PUT'])
@token_required
def update_treatment_payment(treatment_id):
    """
    更新治疗记录支付信息
    
    @param {int} treatment_id - 治疗记录ID
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role not in ['admin', 'consultant', 'fulltime_consultant']:
        return error_response("无权限操作", status_code=403)
    
    treatment = Treatment.query.get_or_404(treatment_id)
    
    # 验证必填字段
    data = request.get_json()
    if 'paid_amount' not in data:
        return error_response("缺少支付金额", status_code=400)
    
    # 更新支付信息
    treatment.paid_amount = data['paid_amount']
    if treatment.paid_amount >= treatment.fee:
        treatment.payment_status = 'paid'
    elif treatment.paid_amount > 0:
        treatment.payment_status = 'partial'
    else:
        treatment.payment_status = 'unpaid'
    
    treatment.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return success_response(
        data=treatment.to_dict(),
        message="更新支付信息成功"
    )

@api_bp.route('/treatments/<int:treatment_id>/rating', methods=['POST'])
@token_required
def rate_treatment(treatment_id):
    """
    评价治疗记录
    
    @param {int} treatment_id - 治疗记录ID
    @return {tuple} - (JSON响应, 状态码)
    """
    treatment = Treatment.query.get_or_404(treatment_id)
    
    # 检查权限
    if g.current_user.role == 'client' and g.current_user.id != treatment.client.user_id:
        return error_response("无权限操作", status_code=403)
    
    # 验证必填字段
    data = request.get_json()
    if 'rating' not in data or not isinstance(data['rating'], (int, float)) or data['rating'] < 1 or data['rating'] > 5:
        return error_response("无效的评分", status_code=400)
    
    # 更新评分
    treatment.rating = data['rating']
    treatment.updated_at = datetime.utcnow()
    
    # 更新医生的平均评分
    doctor = treatment.doctor
    treatments_with_rating = Treatment.query.filter(
        Treatment.doctor_id == doctor.id,
        Treatment.rating.isnot(None)
    ).all()
    
    doctor.rating = sum(t.rating for t in treatments_with_rating) / len(treatments_with_rating)
    doctor.rating_count = len(treatments_with_rating)
    
    db.session.commit()
    
    return success_response(
        data=treatment.to_dict(),
        message="评价成功"
    ) 