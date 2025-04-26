"""
用户API
"""
from flask import jsonify, request, g
from app import db
from app.models import User
from app.api import api_bp
from app.api.authentication import token_required
from app.utils.validators import validate_email, validate_phone, validate_password

@api_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    """
    获取用户列表 (仅管理员)
    
    @return {json} - 用户列表数据
    """
    # 检查权限，只有管理员可以查看所有用户
    if g.current_user.role != 'admin':
        return jsonify({
            'message': '没有权限访问该资源',
            'code': 403
        }), 403
    
    # 获取查询参数
    role = request.args.get('role')
    is_active = request.args.get('is_active')
    
    # 构建查询
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    
    if is_active is not None:
        is_active = is_active.lower() == 'true'
        query = query.filter_by(is_active=is_active)
    
    users = query.all()
    
    return jsonify({
        'message': '获取用户列表成功',
        'code': 200,
        'data': [user.to_dict() for user in users]
    }), 200

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """
    获取单个用户信息
    
    @param {int} user_id - 用户ID
    @return {json} - 用户信息
    """
    # 普通用户只能查看自己的信息
    if g.current_user.role != 'admin' and g.current_user.id != user_id:
        return jsonify({
            'message': '没有权限访问该资源',
            'code': 403
        }), 403
    
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'message': '获取用户信息成功',
        'code': 200,
        'data': user.to_dict()
    }), 200

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """
    更新用户信息
    
    @param {int} user_id - 用户ID
    @return {json} - 更新结果
    """
    # 普通用户只能更新自己的信息
    if g.current_user.role != 'admin' and g.current_user.id != user_id:
        return jsonify({
            'message': '没有权限更新该用户',
            'code': 403
        }), 403
    
    user = User.query.get_or_404(user_id)
    
    data = request.get_json()
    if not data:
        return jsonify({
            'message': '无效的请求数据',
            'code': 400
        }), 400
    
    # 验证并更新数据
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'message': '用户名已存在',
                'code': 400
            }), 400
        user.username = data['username']
    
    if 'email' in data and data['email'] != user.email:
        if not validate_email(data['email']):
            return jsonify({
                'message': '邮箱格式不正确',
                'code': 400
            }), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'message': '该邮箱已被其他用户使用',
                'code': 400
            }), 400
        user.email = data['email']
    
    if 'phone' in data and data['phone'] != user.phone:
        if not validate_phone(data['phone']):
            return jsonify({
                'message': '手机号格式不正确',
                'code': 400
            }), 400
        if User.query.filter_by(phone=data['phone']).first():
            return jsonify({
                'message': '该手机号已被其他用户使用',
                'code': 400
            }), 400
        user.phone = data['phone']
    
    if 'password' in data:
        valid_password, error = validate_password(data['password'])
        if not valid_password:
            return jsonify({
                'message': f'密码强度不够：{error}',
                'code': 400
            }), 400
        user.password = data['password']
    
    # 仅管理员可以更改角色和激活状态
    if g.current_user.role == 'admin':
        if 'role' in data:
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': '用户信息更新成功',
        'code': 200,
        'data': user.to_dict()
    }), 200

@api_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@token_required
def activate_user(user_id):
    """
    激活用户
    
    @param {int} user_id - 用户ID
    @return {json} - 激活结果
    """
    # 只有管理员可以激活用户
    if g.current_user.role != 'admin':
        return jsonify({
            'message': '没有权限执行该操作',
            'code': 403
        }), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.is_active:
        return jsonify({
            'message': '该用户已经是激活状态',
            'code': 400
        }), 400
    
    user.is_active = True
    db.session.commit()
    
    return jsonify({
        'message': '用户激活成功',
        'code': 200,
        'data': {
            'user_id': user.id,
            'is_active': user.is_active
        }
    }), 200

@api_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@token_required
def deactivate_user(user_id):
    """
    停用用户
    
    @param {int} user_id - 用户ID
    @return {json} - 停用结果
    """
    # 只有管理员可以停用用户
    if g.current_user.role != 'admin':
        return jsonify({
            'message': '没有权限执行该操作',
            'code': 403
        }), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.id == g.current_user.id:
        return jsonify({
            'message': '不能停用自己的账户',
            'code': 400
        }), 400
    
    if not user.is_active:
        return jsonify({
            'message': '该用户已经是停用状态',
            'code': 400
        }), 400
    
    user.is_active = False
    db.session.commit()
    
    return jsonify({
        'message': '用户停用成功',
        'code': 200,
        'data': {
            'user_id': user.id,
            'is_active': user.is_active
        }
    }), 200 