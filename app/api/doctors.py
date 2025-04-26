"""
医生相关API
"""
from flask import request, g
from app import db
from app.models import Doctor, Store, Treatment
from app.api import api_bp
from app.utils.response import success_response, error_response, paginated_response
from app.utils.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.utils.validators import validate_required_fields
from app.api.authentication import token_required
from datetime import datetime, timedelta
import json

@api_bp.route('/doctors', methods=['GET'])
@token_required
def get_doctors():
    """
    获取医生列表
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    store_id = request.args.get('store_id', type=int)
    specialty = request.args.get('specialty')
    status = request.args.get('status')  # available/busy/off_duty
    
    # 构建查询
    query = Doctor.query
    
    if store_id:
        query = query.filter_by(store_id=store_id)
    if specialty:
        query = query.filter(Doctor.specialty.like(f'%{specialty}%'))
    if status:
        query = query.filter_by(status=status)
    
    # 执行分页查询
    pagination = query.paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[doctor.to_dict() for doctor in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取医生列表成功"
    )

@api_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@token_required
def get_doctor(doctor_id):
    """
    获取医生详情
    
    @param {int} doctor_id - 医生ID
    @return {tuple} - (JSON响应, 状态码)
    """
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # 获取医生的治疗记录
    treatments = Treatment.query.filter_by(doctor_id=doctor_id).order_by(Treatment.created_at.desc()).limit(10).all()
    
    doctor_data = doctor.to_dict()
    doctor_data['recent_treatments'] = [treatment.to_dict() for treatment in treatments]
    
    return success_response(
        data=doctor_data,
        message="获取医生详情成功"
    )

@api_bp.route('/doctors', methods=['POST'])
@token_required
def create_doctor():
    """
    创建新医生
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role != 'admin':
        return error_response("无权限操作", status_code=403)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['name', 'store_id', 'specialty']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 检查门店是否存在
    store = Store.query.get(data['store_id'])
    if not store:
        return error_response("门店不存在", status_code=400)
    
    # 创建新医生
    new_doctor = Doctor(
        name=data['name'],
        title=data.get('title'),
        specialty=data['specialty'],
        bio=data.get('bio'),
        avatar=data.get('avatar'),
        store_id=data['store_id'],
        status='available'
    )
    
    db.session.add(new_doctor)
    db.session.commit()
    
    return success_response(
        data=new_doctor.to_dict(),
        message="创建医生成功",
        status_code=201
    )

@api_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@token_required
def update_doctor(doctor_id):
    """
    更新医生信息
    
    @param {int} doctor_id - 医生ID
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role != 'admin':
        return error_response("无权限操作", status_code=403)
    
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['name', 'specialty']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 更新医生信息
    doctor.name = data['name']
    doctor.title = data.get('title')
    doctor.specialty = data['specialty']
    doctor.bio = data.get('bio')
    doctor.avatar = data.get('avatar')
    doctor.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return success_response(
        data=doctor.to_dict(),
        message="更新医生信息成功"
    )

@api_bp.route('/doctors/<int:doctor_id>/status', methods=['PUT'])
@token_required
def update_doctor_status(doctor_id):
    """
    更新医生状态
    
    @param {int} doctor_id - 医生ID
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role != 'admin':
        return error_response("无权限操作", status_code=403)
    
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # 验证必填字段
    data = request.get_json()
    if 'status' not in data or data['status'] not in ['available', 'busy', 'off_duty']:
        return error_response("无效的状态值", status_code=400)
    
    # 更新医生状态
    doctor.status = data['status']
    doctor.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return success_response(
        data=doctor.to_dict(),
        message="更新医生状态成功"
    )

@api_bp.route('/doctors/<int:doctor_id>/stats', methods=['GET'])
@token_required
def get_doctor_stats(doctor_id):
    """
    获取医生统计数据
    
    @param {int} doctor_id - 医生ID
    @return {tuple} - (JSON响应, 状态码)
    """
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # 获取时间范围
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 统计数据
    total_treatments = Treatment.query.filter_by(doctor_id=doctor_id).count()
    recent_treatments = Treatment.query.filter(
        Treatment.doctor_id == doctor_id,
        Treatment.created_at >= start_date
    ).count()
    
    # 计算平均评分
    treatments_with_rating = Treatment.query.filter(
        Treatment.doctor_id == doctor_id,
        Treatment.rating.isnot(None)
    ).all()
    
    avg_rating = sum(t.rating for t in treatments_with_rating) / len(treatments_with_rating) if treatments_with_rating else 0
    
    stats = {
        'total_treatments': total_treatments,
        'recent_treatments': recent_treatments,
        'avg_rating': round(avg_rating, 1),
        'rating_count': len(treatments_with_rating),
        'period': f"最近{days}天"
    }
    
    return success_response(
        data=stats,
        message="获取统计数据成功"
    ) 