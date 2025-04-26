"""
咨询师相关API
"""
from flask import request, g
from app import db
from app.models import User, Consultant, Client, Message
from app.api import api_bp
from app.utils.response import success_response, error_response, paginated_response
from app.utils.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.utils.validators import validate_required_fields
from app.api.authentication import token_required
from datetime import datetime, timedelta
import json

@api_bp.route('/consultants', methods=['GET'])
@token_required
def get_consultants():
    """
    获取咨询师列表
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role != 'admin':
        return error_response("无权限访问", status_code=403)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    type_filter = request.args.get('type')  # fulltime/parttime
    verified = request.args.get('verified', type=bool)
    
    # 构建查询
    query = Consultant.query
    
    if type_filter:
        query = query.filter_by(type=type_filter)
    if verified is not None:
        query = query.filter_by(verified=verified)
    
    # 执行分页查询
    pagination = query.paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[consultant.to_dict() for consultant in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取咨询师列表成功"
    )

@api_bp.route('/consultants/<int:consultant_id>', methods=['GET'])
@token_required
def get_consultant(consultant_id):
    """
    获取咨询师详情
    
    @param {int} consultant_id - 咨询师ID
    @return {tuple} - (JSON响应, 状态码)
    """
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # 检查权限
    if g.current_user.role != 'admin' and g.current_user.id != consultant.user_id:
        return error_response("无权限访问", status_code=403)
    
    return success_response(
        data=consultant.to_dict(),
        message="获取咨询师详情成功"
    )

@api_bp.route('/consultants/verify/<int:consultant_id>', methods=['POST'])
@token_required
def verify_consultant(consultant_id):
    """
    验证咨询师身份
    
    @param {int} consultant_id - 咨询师ID
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role != 'admin':
        return error_response("无权限操作", status_code=403)
    
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['certification']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 更新认证信息
    consultant.certification = json.dumps(data['certification'])
    consultant.verified = True
    consultant.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return success_response(
        data=consultant.to_dict(),
        message="咨询师认证成功"
    )

@api_bp.route('/consultants/<int:consultant_id>/clients', methods=['GET'])
@token_required
def get_consultant_clients(consultant_id):
    """
    获取咨询师的客户列表
    
    @param {int} consultant_id - 咨询师ID
    @return {tuple} - (JSON响应, 状态码)
    """
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # 检查权限
    if g.current_user.role != 'admin' and g.current_user.id != consultant.user_id:
        return error_response("无权限访问", status_code=403)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_orphan = request.args.get('is_orphan', type=bool)
    
    # 构建查询
    query = consultant.clients
    if is_orphan is not None:
        query = query.filter_by(is_orphan=is_orphan)
    
    # 执行分页查询
    pagination = query.paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[client.to_dict() for client in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取客户列表成功"
    )

@api_bp.route('/consultants/<int:consultant_id>/stats', methods=['GET'])
@token_required
def get_consultant_stats(consultant_id):
    """
    获取咨询师统计数据
    
    @param {int} consultant_id - 咨询师ID
    @return {tuple} - (JSON响应, 状态码)
    """
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # 检查权限
    if g.current_user.role != 'admin' and g.current_user.id != consultant.user_id:
        return error_response("无权限访问", status_code=403)
    
    # 获取时间范围
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 统计数据
    total_clients = consultant.clients.count()
    active_clients = consultant.clients.filter(Client.last_contact >= start_date).count()
    orphan_clients = consultant.clients.filter_by(is_orphan=True).count()
    
    # 获取最近的消息统计
    recent_messages = Message.query.filter(
        Message.sender_id == consultant.user_id,
        Message.created_at >= start_date
    ).count()
    
    stats = {
        'total_clients': total_clients,
        'active_clients': active_clients,
        'orphan_clients': orphan_clients,
        'recent_messages': recent_messages,
        'rating': consultant.rating,
        'period': f"最近{days}天"
    }
    
    return success_response(
        data=stats,
        message="获取统计数据成功"
    )

@api_bp.route('/consultants/<int:consultant_id>/supervisor', methods=['PUT'])
@token_required
def update_supervisor(consultant_id):
    """
    更新咨询师的指导老师
    
    @param {int} consultant_id - 咨询师ID
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role != 'admin':
        return error_response("无权限操作", status_code=403)
    
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # 验证必填字段
    data = request.get_json()
    if 'supervisor_id' not in data:
        return error_response("缺少指导老师ID", status_code=400)
    
    # 检查指导老师是否存在且为全职咨询师
    supervisor = Consultant.query.get(data['supervisor_id'])
    if not supervisor or supervisor.type != 'fulltime':
        return error_response("无效的指导老师", status_code=400)
    
    # 更新指导老师
    consultant.supervisor_id = supervisor.id
    consultant.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return success_response(
        data=consultant.to_dict(),
        message="更新指导老师成功"
    ) 