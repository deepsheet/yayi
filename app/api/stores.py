"""
门店相关API
"""
from flask import request, g
from app import db
from app.models import Store, Doctor, Consultant
from app.api import api_bp
from app.utils.response import success_response, error_response, paginated_response
from app.utils.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.utils.validators import validate_required_fields
from app.api.authentication import token_required
from datetime import datetime
import json

@api_bp.route('/stores', methods=['GET'])
@token_required
def get_stores():
    """
    获取门店列表
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')  # active/inactive
    specialty = request.args.get('specialty')
    
    # 构建查询
    query = Store.query
    
    if status:
        query = query.filter_by(status=status)
    if specialty:
        query = query.filter(Store.specialties.like(f'%{specialty}%'))
    
    # 执行分页查询
    pagination = query.paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[store.to_dict() for store in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取门店列表成功"
    )

@api_bp.route('/stores/<int:store_id>', methods=['GET'])
@token_required
def get_store(store_id):
    """
    获取门店详情
    
    @param {int} store_id - 门店ID
    @return {tuple} - (JSON响应, 状态码)
    """
    store = Store.query.get_or_404(store_id)
    
    # 获取门店的医生和咨询师信息
    doctors = Doctor.query.filter_by(store_id=store_id).all()
    consultants = Consultant.query.filter_by(store_id=store_id).all()
    
    store_data = store.to_dict()
    store_data['doctors'] = [doctor.to_dict() for doctor in doctors]
    store_data['consultants'] = [consultant.to_dict() for consultant in consultants]
    
    return success_response(
        data=store_data,
        message="获取门店详情成功"
    )

@api_bp.route('/stores', methods=['POST'])
@token_required
def create_store():
    """
    创建新门店
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role != 'admin':
        return error_response("无权限操作", status_code=403)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['name', 'address']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 创建新门店
    new_store = Store(
        name=data['name'],
        address=data['address'],
        contact=data.get('contact'),
        description=data.get('description'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        business_hours=json.dumps(data.get('business_hours', {})),
        photos=json.dumps(data.get('photos', [])),
        specialties=data.get('specialties'),
        status='active'
    )
    
    db.session.add(new_store)
    db.session.commit()
    
    return success_response(
        data=new_store.to_dict(),
        message="创建门店成功",
        status_code=201
    )

@api_bp.route('/stores/<int:store_id>', methods=['PUT'])
@token_required
def update_store(store_id):
    """
    更新门店信息
    
    @param {int} store_id - 门店ID
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role != 'admin':
        return error_response("无权限操作", status_code=403)
    
    store = Store.query.get_or_404(store_id)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['name', 'address']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 更新门店信息
    store.name = data['name']
    store.address = data['address']
    store.contact = data.get('contact')
    store.description = data.get('description')
    store.latitude = data.get('latitude')
    store.longitude = data.get('longitude')
    store.business_hours = json.dumps(data.get('business_hours', {}))
    store.photos = json.dumps(data.get('photos', []))
    store.specialties = data.get('specialties')
    store.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return success_response(
        data=store.to_dict(),
        message="更新门店信息成功"
    )

@api_bp.route('/stores/<int:store_id>/status', methods=['PUT'])
@token_required
def update_store_status(store_id):
    """
    更新门店状态
    
    @param {int} store_id - 门店ID
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role != 'admin':
        return error_response("无权限操作", status_code=403)
    
    store = Store.query.get_or_404(store_id)
    
    # 验证必填字段
    data = request.get_json()
    if 'status' not in data or data['status'] not in ['active', 'inactive']:
        return error_response("无效的状态值", status_code=400)
    
    # 更新门店状态
    store.status = data['status']
    store.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return success_response(
        data=store.to_dict(),
        message="更新门店状态成功"
    )

@api_bp.route('/stores/<int:store_id>/doctors', methods=['GET'])
@token_required
def get_store_doctors(store_id):
    """
    获取门店的医生列表
    
    @param {int} store_id - 门店ID
    @return {tuple} - (JSON响应, 状态码)
    """
    store = Store.query.get_or_404(store_id)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    specialty = request.args.get('specialty')
    
    # 构建查询
    query = Doctor.query.filter_by(store_id=store_id)
    if specialty:
        query = query.filter(Doctor.specialty.like(f'%{specialty}%'))
    
    # 执行分页查询
    pagination = query.paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[doctor.to_dict() for doctor in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取医生列表成功"
    )

@api_bp.route('/stores/<int:store_id>/consultants', methods=['GET'])
@token_required
def get_store_consultants(store_id):
    """
    获取门店的咨询师列表
    
    @param {int} store_id - 门店ID
    @return {tuple} - (JSON响应, 状态码)
    """
    store = Store.query.get_or_404(store_id)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    type_filter = request.args.get('type')  # fulltime/parttime
    
    # 构建查询
    query = Consultant.query.filter_by(store_id=store_id)
    if type_filter:
        query = query.filter_by(type=type_filter)
    
    # 执行分页查询
    pagination = query.paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[consultant.to_dict() for consultant in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取咨询师列表成功"
    ) 