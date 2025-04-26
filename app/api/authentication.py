"""
认证相关API
"""
from flask import jsonify, request, g, current_app
from werkzeug.security import generate_password_hash
import jwt
from datetime import datetime, timedelta
import json
from app import db
from app.models import User
from app.api import api_bp
from app.utils.validators import validate_email, validate_phone
from functools import wraps

def token_required(f):
    """
    JWT令牌验证装饰器
    
    @param {function} f - 被装饰的函数
    @return {function} - 装饰后的函数
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 从请求头中获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': '缺少认证令牌！', 'code': 401}), 401
        
        try:
            # 解码token
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': '用户不存在！', 'code': 401}), 401
            
            # 将当前用户设置为全局变量
            g.current_user = current_user
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '认证令牌已过期！', 'code': 401}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的认证令牌！', 'code': 401}), 401
        
        return f(*args, **kwargs)
    return decorated

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """
    用户注册API
    """
    data = request.get_json()
    
    # 验证必填字段
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '用户名和密码为必填项！', 'code': 400}), 400
    
    # 验证用户名是否已存在
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'message': '用户名已存在！', 'code': 400}), 400
    
    # 验证邮箱
    email = data.get('email')
    if email:
        if not validate_email(email):
            return jsonify({'message': '邮箱格式不正确！', 'code': 400}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'message': '该邮箱已被注册！', 'code': 400}), 400
    
    # 验证手机号
    phone = data.get('phone')
    if phone:
        if not validate_phone(phone):
            return jsonify({'message': '手机号格式不正确！', 'code': 400}), 400
        if User.query.filter_by(phone=phone).first():
            return jsonify({'message': '该手机号已被注册！', 'code': 400}), 400
    
    # 创建新用户
    new_user = User(
        username=data.get('username'),
        email=email,
        phone=phone,
        password=data.get('password'),
        role=data.get('role', 'client')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': '用户注册成功！',
        'code': 201,
        'data': {
            'user_id': new_user.id,
            'username': new_user.username
        }
    }), 201

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    用户登录API
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'message': '无效的请求数据！', 'code': 400}), 400
    
    # 获取用户名/邮箱/手机号和密码
    identity = data.get('identity')
    password = data.get('password')
    
    if not identity or not password:
        return jsonify({'message': '用户名/邮箱/手机号和密码为必填项！', 'code': 400}), 400
    
    # 查找用户
    user = User.query.filter_by(username=identity).first() or \
           User.query.filter_by(email=identity).first() or \
           User.query.filter_by(phone=identity).first()
    
    if not user:
        return jsonify({'message': '用户不存在！', 'code': 404}), 404
    
    # 验证密码
    if not user.verify_password(password):
        return jsonify({'message': '密码错误！', 'code': 401}), 401
    
    if not user.is_active:
        return jsonify({'message': '账户已被禁用！', 'code': 403}), 403
    
    # 生成JWT令牌
    token_expiry = datetime.utcnow() + current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(days=1))
    token = jwt.encode({
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': token_expiry
    }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': '登录成功！',
        'code': 200,
        'data': {
            'token': token,
            'user': user.to_dict(),
            'expires_at': token_expiry.isoformat()
        }
    }), 200

@api_bp.route('/auth/profile', methods=['GET'])
@token_required
def get_profile():
    """
    获取当前用户个人资料
    """
    return jsonify({
        'message': '获取个人资料成功！',
        'code': 200,
        'data': g.current_user.to_dict()
    }), 200

@api_bp.route('/auth/profile', methods=['PUT'])
@token_required
def update_profile():
    """
    更新当前用户个人资料
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'message': '无效的请求数据！', 'code': 400}), 400
    
    user = g.current_user
    
    # 更新可编辑字段
    if 'email' in data and data['email'] != user.email:
        if not validate_email(data['email']):
            return jsonify({'message': '邮箱格式不正确！', 'code': 400}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': '该邮箱已被其他用户使用！', 'code': 400}), 400
        user.email = data['email']
    
    if 'phone' in data and data['phone'] != user.phone:
        if not validate_phone(data['phone']):
            return jsonify({'message': '手机号格式不正确！', 'code': 400}), 400
        if User.query.filter_by(phone=data['phone']).first():
            return jsonify({'message': '该手机号已被其他用户使用！', 'code': 400}), 400
        user.phone = data['phone']
    
    if 'avatar' in data:
        user.avatar = data['avatar']
    
    # 如果更新密码
    if 'password' in data and data['password'] and 'old_password' in data:
        if not user.verify_password(data['old_password']):
            return jsonify({'message': '原密码错误！', 'code': 401}), 401
        user.password = data['password']
    
    db.session.commit()
    
    return jsonify({
        'message': '个人资料更新成功！',
        'code': 200,
        'data': user.to_dict()
    }), 200 