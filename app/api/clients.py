"""
客户相关API
"""
from flask import jsonify, request, g
from app import db
from app.models import Client, User, Consultant
from app.api import api_bp
from app.api.authentication import token_required
from datetime import datetime
import json

@api_bp.route('/clients', methods=['GET'])
@token_required
def get_clients():
    """
    获取客户列表
    
    @return {json} - 客户列表数据
    """
    # 判断用户角色
    if g.current_user.role not in ['consultant', 'fulltime_consultant', 'admin']:
        return jsonify({
            'message': '没有权限访问该资源',
            'code': 403
        }), 403
    
    # 如果是咨询师，只能查看自己的客户
    if g.current_user.role in ['consultant', 'fulltime_consultant']:
        consultant = Consultant.query.filter_by(user_id=g.current_user.id).first()
        if not consultant:
            return jsonify({
                'message': '咨询师信息不存在',
                'code': 404
            }), 404
        
        clients = Client.query.filter_by(assigned_consultant_id=consultant.id).all()
    else:
        # 管理员可以查看所有客户
        clients = Client.query.all()
    
    # 处理查询参数
    is_orphan = request.args.get('is_orphan')
    if is_orphan:
        is_orphan = is_orphan.lower() == 'true'
        clients = [client for client in clients if client.is_orphan == is_orphan]
    
    # 返回结果
    return jsonify({
        'message': '获取客户列表成功',
        'code': 200,
        'data': [client.to_dict() for client in clients]
    }), 200

@api_bp.route('/clients/<int:client_id>', methods=['GET'])
@token_required
def get_client(client_id):
    """
    获取单个客户信息
    
    @param {int} client_id - 客户ID
    @return {json} - 客户信息
    """
    client = Client.query.get_or_404(client_id)
    
    # 判断权限
    if g.current_user.role in ['consultant', 'fulltime_consultant']:
        consultant = Consultant.query.filter_by(user_id=g.current_user.id).first()
        if not consultant or client.assigned_consultant_id != consultant.id:
            return jsonify({
                'message': '没有权限访问该资源',
                'code': 403
            }), 403
    
    return jsonify({
        'message': '获取客户信息成功',
        'code': 200,
        'data': client.to_dict()
    }), 200

@api_bp.route('/clients', methods=['POST'])
@token_required
def create_client():
    """
    创建新客户
    
    @return {json} - 创建结果
    """
    # 判断权限
    if g.current_user.role not in ['consultant', 'fulltime_consultant', 'admin']:
        return jsonify({
            'message': '没有权限执行该操作',
            'code': 403
        }), 403
    
    data = request.get_json()
    if not data:
        return jsonify({
            'message': '无效的请求数据',
            'code': 400
        }), 400
    
    # 验证必填字段
    if not data.get('name') or not data.get('phone'):
        return jsonify({
            'message': '姓名和手机号为必填项',
            'code': 400
        }), 400
    
    # 检查手机号是否已存在
    existing_user = User.query.filter_by(phone=data.get('phone')).first()
    
    if existing_user:
        # 检查该用户是否已有客户资料
        existing_client = Client.query.filter_by(user_id=existing_user.id).first()
        
        if existing_client:
            if g.current_user.role != 'admin':
                consultant = Consultant.query.filter_by(user_id=g.current_user.id).first()
                if existing_client.assigned_consultant_id == consultant.id:
                    return jsonify({
                        'message': '该客户已在您的客户列表中',
                        'code': 400,
                        'data': existing_client.to_dict()
                    }), 400
                elif existing_client.is_orphan:
                    # 如果是"孤儿客户"，可以认领
                    existing_client.assigned_consultant_id = consultant.id
                    existing_client.is_orphan = False
                    existing_client.last_contact = datetime.utcnow()
                    db.session.commit()
                    return jsonify({
                        'message': '成功认领孤儿客户',
                        'code': 200,
                        'data': existing_client.to_dict()
                    }), 200
                else:
                    return jsonify({
                        'message': '该客户已被其他咨询师认领',
                        'code': 400
                    }), 400
        
        # 创建新客户资料
        assigned_consultant_id = None
        if g.current_user.role in ['consultant', 'fulltime_consultant']:
            consultant = Consultant.query.filter_by(user_id=g.current_user.id).first()
            assigned_consultant_id = consultant.id
        elif data.get('assigned_consultant_id'):
            assigned_consultant_id = data.get('assigned_consultant_id')
        
        new_client = Client(
            user_id=existing_user.id,
            name=data.get('name'),
            gender=data.get('gender'),
            birth_date=data.get('birth_date'),
            address=data.get('address'),
            contact_info=data.get('phone'),
            assigned_consultant_id=assigned_consultant_id,
            last_contact=datetime.utcnow()
        )
        db.session.add(new_client)
        db.session.commit()
        
        return jsonify({
            'message': '客户资料创建成功',
            'code': 201,
            'data': new_client.to_dict()
        }), 201
    else:
        # 创建新用户和客户资料
        new_user = User(
            username=f'client_{data.get("phone")}',
            phone=data.get('phone'),
            password='123456',  # 默认密码
            role='client'
        )
        db.session.add(new_user)
        db.session.flush()
        
        assigned_consultant_id = None
        if g.current_user.role in ['consultant', 'fulltime_consultant']:
            consultant = Consultant.query.filter_by(user_id=g.current_user.id).first()
            assigned_consultant_id = consultant.id
        elif data.get('assigned_consultant_id'):
            assigned_consultant_id = data.get('assigned_consultant_id')
        
        new_client = Client(
            user_id=new_user.id,
            name=data.get('name'),
            gender=data.get('gender'),
            birth_date=data.get('birth_date'),
            address=data.get('address'),
            contact_info=data.get('phone'),
            assigned_consultant_id=assigned_consultant_id,
            last_contact=datetime.utcnow()
        )
        db.session.add(new_client)
        db.session.commit()
        
        return jsonify({
            'message': '用户和客户资料创建成功',
            'code': 201,
            'data': new_client.to_dict()
        }), 201

@api_bp.route('/clients/<int:client_id>', methods=['PUT'])
@token_required
def update_client(client_id):
    """
    更新客户信息
    
    @param {int} client_id - 客户ID
    @return {json} - 更新结果
    """
    client = Client.query.get_or_404(client_id)
    
    # 判断权限
    if g.current_user.role in ['consultant', 'fulltime_consultant']:
        consultant = Consultant.query.filter_by(user_id=g.current_user.id).first()
        if not consultant or client.assigned_consultant_id != consultant.id:
            return jsonify({
                'message': '没有权限修改该客户信息',
                'code': 403
            }), 403
    
    data = request.get_json()
    if not data:
        return jsonify({
            'message': '无效的请求数据',
            'code': 400
        }), 400
    
    # 更新客户信息
    if 'name' in data:
        client.name = data['name']
    if 'gender' in data:
        client.gender = data['gender']
    if 'birth_date' in data:
        client.birth_date = data['birth_date']
    if 'address' in data:
        client.address = data['address']
    if 'contact_info' in data:
        client.contact_info = data['contact_info']
    if 'tags' in data:
        client.tags = data['tags']
    
    # 管理员可以修改分配的咨询师
    if g.current_user.role == 'admin' and 'assigned_consultant_id' in data:
        client.assigned_consultant_id = data['assigned_consultant_id']
        if client.assigned_consultant_id:
            client.is_orphan = False
            client.last_contact = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': '客户信息更新成功',
        'code': 200,
        'data': client.to_dict()
    }), 200

@api_bp.route('/clients/<int:client_id>/tags', methods=['POST'])
@token_required
def update_client_tags(client_id):
    """
    更新客户标签
    
    @param {int} client_id - 客户ID
    @return {json} - 更新结果
    """
    client = Client.query.get_or_404(client_id)
    
    # 判断权限
    if g.current_user.role in ['consultant', 'fulltime_consultant']:
        consultant = Consultant.query.filter_by(user_id=g.current_user.id).first()
        if not consultant or client.assigned_consultant_id != consultant.id:
            return jsonify({
                'message': '没有权限修改该客户标签',
                'code': 403
            }), 403
    
    data = request.get_json()
    if not data or 'tag' not in data:
        return jsonify({
            'message': '标签参数缺失',
            'code': 400
        }), 400
    
    tag = data['tag']
    add = data.get('add', True)
    
    # 更新标签
    current_tags = client.tags.split(',') if client.tags else []
    current_tags = [t.strip() for t in current_tags if t.strip()]
    
    if add and tag not in current_tags:
        current_tags.append(tag)
    elif not add and tag in current_tags:
        current_tags.remove(tag)
    
    client.tags = ','.join(current_tags)
    db.session.commit()
    
    return jsonify({
        'message': '客户标签更新成功',
        'code': 200,
        'data': {
            'client_id': client.id,
            'tags': client.tags
        }
    }), 200

@api_bp.route('/clients/orphan/check', methods=['POST'])
@token_required
def check_orphan_clients():
    """
    检查并更新孤儿客户状态
    
    @return {json} - 更新结果
    """
    # 只有管理员可以执行此操作
    if g.current_user.role != 'admin':
        return jsonify({
            'message': '没有权限执行该操作',
            'code': 403
        }), 403
    
    # 执行孤儿客户检查
    orphan_count = Client.check_orphan_status()
    
    return jsonify({
        'message': '孤儿客户状态检查完成',
        'code': 200,
        'data': {
            'orphan_count': orphan_count
        }
    }), 200 