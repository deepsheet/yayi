"""
消息相关API
"""
from flask import request, g
from app import db
from app.models import Message, GroupMessage, User, Client, Consultant
from app.api import api_bp
from app.utils.response import success_response, error_response, paginated_response
from app.utils.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.utils.validators import validate_required_fields
from app.api.authentication import token_required
from datetime import datetime
import json

@api_bp.route('/messages', methods=['GET'])
@token_required
def get_messages():
    """
    获取消息列表
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sender_id = request.args.get('sender_id', type=int)
    receiver_id = request.args.get('receiver_id', type=int)
    is_read = request.args.get('is_read', type=bool)
    
    # 构建查询
    query = Message.query.filter(
        (Message.sender_id == g.current_user.id) | (Message.receiver_id == g.current_user.id)
    )
    
    if sender_id:
        query = query.filter_by(sender_id=sender_id)
    if receiver_id:
        query = query.filter_by(receiver_id=receiver_id)
    if is_read is not None:
        query = query.filter_by(is_read=is_read)
    
    # 执行分页查询
    pagination = query.order_by(Message.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[message.to_dict() for message in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取消息列表成功"
    )

@api_bp.route('/messages/<int:message_id>', methods=['GET'])
@token_required
def get_message(message_id):
    """
    获取消息详情
    
    @param {int} message_id - 消息ID
    @return {tuple} - (JSON响应, 状态码)
    """
    message = Message.query.get_or_404(message_id)
    
    # 检查权限
    if g.current_user.id not in [message.sender_id, message.receiver_id]:
        return error_response("无权限访问", status_code=403)
    
    # 如果是接收者，标记为已读
    if g.current_user.id == message.receiver_id and not message.is_read:
        message.is_read = True
        db.session.commit()
    
    return success_response(
        data=message.to_dict(),
        message="获取消息详情成功"
    )

@api_bp.route('/messages', methods=['POST'])
@token_required
def send_message():
    """
    发送消息
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 验证必填字段
    data = request.get_json()
    required_fields = ['receiver_id', 'content']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 检查接收者是否存在
    receiver = User.query.get(data['receiver_id'])
    if not receiver:
        return error_response("接收者不存在", status_code=400)
    
    # 创建新消息
    new_message = Message(
        sender_id=g.current_user.id,
        receiver_id=data['receiver_id'],
        content=data['content'],
        msg_type=data.get('msg_type', 'text'),
        attachment_url=data.get('attachment_url')
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return success_response(
        data=new_message.to_dict(),
        message="发送消息成功",
        status_code=201
    )

@api_bp.route('/messages/<int:message_id>/read', methods=['POST'])
@token_required
def mark_message_read(message_id):
    """
    标记消息为已读
    
    @param {int} message_id - 消息ID
    @return {tuple} - (JSON响应, 状态码)
    """
    message = Message.query.get_or_404(message_id)
    
    # 检查权限
    if g.current_user.id != message.receiver_id:
        return error_response("无权限操作", status_code=403)
    
    # 标记为已读
    message.is_read = True
    db.session.commit()
    
    return success_response(
        data=message.to_dict(),
        message="标记消息已读成功"
    )

@api_bp.route('/group_messages', methods=['GET'])
@token_required
def get_group_messages():
    """
    获取群发消息列表
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role not in ['admin', 'consultant', 'fulltime_consultant']:
        return error_response("无权限访问", status_code=403)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')  # pending/sending/sent/failed
    
    # 构建查询
    query = GroupMessage.query.filter_by(sender_id=g.current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    # 执行分页查询
    pagination = query.order_by(GroupMessage.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[message.to_dict() for message in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取群发消息列表成功"
    )

@api_bp.route('/group_messages', methods=['POST'])
@token_required
def send_group_message():
    """
    发送群发消息
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role not in ['admin', 'consultant', 'fulltime_consultant']:
        return error_response("无权限操作", status_code=403)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['content', 'target_type']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 创建群发消息
    new_message = GroupMessage(
        sender_id=g.current_user.id,
        content=data['content'],
        msg_type=data.get('msg_type', 'text'),
        target_type=data['target_type'],
        target_tags=data.get('target_tags'),
        attachment_url=data.get('attachment_url'),
        status='pending'
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    # 根据目标类型获取接收者列表
    if data['target_type'] == 'all_clients':
        receivers = Client.query.all()
    elif data['target_type'] == 'tagged_clients':
        if not data.get('target_tags'):
            return error_response("缺少目标标签", status_code=400)
        tags = data['target_tags'].split(',')
        receivers = Client.query.filter(Client.tags.like(f'%{tags[0]}%'))
        for tag in tags[1:]:
            receivers = receivers.union(Client.query.filter(Client.tags.like(f'%{tag}%')))
    else:
        return error_response("无效的目标类型", status_code=400)
    
    # 为每个接收者创建消息
    for receiver in receivers:
        message = Message(
            sender_id=g.current_user.id,
            receiver_id=receiver.user_id,
            content=data['content'],
            msg_type=data.get('msg_type', 'text'),
            attachment_url=data.get('attachment_url')
        )
        db.session.add(message)
    
    # 更新群发消息状态
    new_message.status = 'sent'
    new_message.sent_count = len(receivers)
    
    db.session.commit()
    
    return success_response(
        data=new_message.to_dict(),
        message="发送群发消息成功",
        status_code=201
    ) 