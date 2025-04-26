"""
管理员路由
"""
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Client, Consultant, Store, Doctor, Treatment, KnowledgeArticle, KnowledgeQA
from app.views.admin import admin
import json
from datetime import datetime
from sqlalchemy import func

def check_admin_role(f):
    """
    检查用户是否为管理员角色
    """
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('您没有权限访问该页面', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

@admin.route('/')
@check_admin_role
def index():
    """
    管理员首页
    """
    # 统计数据
    user_count = User.query.count()
    client_count = Client.query.count()
    consultant_count = Consultant.query.count()
    store_count = Store.query.count()
    
    # 待审核咨询师数量
    pending_consultants = Consultant.query.filter_by(verified=False).count()
    
    # 待审核知识库内容
    pending_articles = KnowledgeArticle.query.filter_by(status='pending').count()
    pending_qa = KnowledgeQA.query.filter_by(status='pending').count()
    
    # 孤儿客户数量
    orphan_clients = Client.query.filter_by(is_orphan=True).count()
    
    return render_template('admin/index.html',
                          user_count=user_count,
                          client_count=client_count,
                          consultant_count=consultant_count,
                          store_count=store_count,
                          pending_consultants=pending_consultants,
                          pending_articles=pending_articles,
                          pending_qa=pending_qa,
                          orphan_clients=orphan_clients)

@admin.route('/users')
@check_admin_role
def user_list():
    """
    用户列表
    """
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/user_list.html', users=users)

@admin.route('/users/<int:user_id>', methods=['GET', 'POST'])
@check_admin_role
def user_detail(user_id):
    """
    用户详情
    """
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        data = request.form
        
        # 更新用户资料
        user.username = data.get('username')
        user.email = data.get('email')
        user.phone = data.get('phone')
        user.is_active = 'is_active' in data
        
        if data.get('role') in ['client', 'consultant', 'fulltime_consultant', 'admin']:
            user.role = data.get('role')
        
        if data.get('password'):
            user.password = data.get('password')
        
        db.session.commit()
        flash('用户资料已更新', 'success')
    
    # 获取相关资料
    client_profile = None
    consultant_profile = None
    
    if user.role == 'client':
        client_profile = Client.query.filter_by(user_id=user.id).first()
    
    if user.role in ['consultant', 'fulltime_consultant']:
        consultant_profile = Consultant.query.filter_by(user_id=user.id).first()
    
    return render_template('admin/user_detail.html',
                          user=user,
                          client_profile=client_profile,
                          consultant_profile=consultant_profile)

@admin.route('/consultants')
@check_admin_role
def consultant_list():
    """
    咨询师列表
    """
    consultants = Consultant.query.order_by(Consultant.created_at.desc()).all()
    return render_template('admin/consultant_list.html', consultants=consultants)

@admin.route('/consultants/pending')
@check_admin_role
def pending_consultants():
    """
    待审核咨询师
    """
    consultants = Consultant.query.filter_by(verified=False).order_by(Consultant.created_at).all()
    return render_template('admin/pending_consultants.html', consultants=consultants)

@admin.route('/consultants/verify/<int:consultant_id>', methods=['POST'])
@check_admin_role
def verify_consultant(consultant_id):
    """
    审核咨询师
    """
    consultant = Consultant.query.get_or_404(consultant_id)
    action = request.form.get('action')
    
    if action == 'approve':
        consultant.verified = True
        user = User.query.get(consultant.user_id)
        if user:
            user.role = consultant.type
            user.is_verified = True
        
        db.session.commit()
        flash('咨询师资格已审核通过', 'success')
    
    elif action == 'reject':
        # 可选：删除咨询师资料或标记为拒绝
        db.session.delete(consultant)
        db.session.commit()
        flash('已拒绝咨询师资格申请', 'info')
    
    return redirect(url_for('admin.pending_consultants'))

@admin.route('/stores')
@check_admin_role
def store_list():
    """
    门店列表
    """
    stores = Store.query.order_by(Store.created_at.desc()).all()
    return render_template('admin/store_list.html', stores=stores)

@admin.route('/stores/add', methods=['GET', 'POST'])
@check_admin_role
def add_store():
    """
    添加门店
    """
    if request.method == 'POST':
        data = request.form
        
        if not data.get('name') or not data.get('address'):
            flash('店名和地址为必填项', 'danger')
            return redirect(url_for('admin.add_store'))
        
        # 创建新门店
        new_store = Store(
            name=data.get('name'),
            address=data.get('address'),
            contact=data.get('contact'),
            description=data.get('description'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            business_hours=data.get('business_hours'),
            specialties=data.get('specialties'),
            status='active'
        )
        
        db.session.add(new_store)
        db.session.commit()
        
        flash('门店添加成功', 'success')
        return redirect(url_for('admin.store_list'))
    
    return render_template('admin/add_store.html')

@admin.route('/stores/<int:store_id>', methods=['GET', 'POST'])
@check_admin_role
def store_detail(store_id):
    """
    门店详情
    """
    store = Store.query.get_or_404(store_id)
    
    if request.method == 'POST':
        data = request.form
        
        # 更新门店资料
        store.name = data.get('name')
        store.address = data.get('address')
        store.contact = data.get('contact')
        store.description = data.get('description')
        store.latitude = data.get('latitude')
        store.longitude = data.get('longitude')
        store.business_hours = data.get('business_hours')
        store.specialties = data.get('specialties')
        store.status = data.get('status')
        
        db.session.commit()
        flash('门店资料已更新', 'success')
    
    # 获取门店相关数据
    doctors = Doctor.query.filter_by(store_id=store.id).all()
    consultants = Consultant.query.filter_by(store_id=store.id).all()
    
    return render_template('admin/store_detail.html',
                          store=store,
                          doctors=doctors,
                          consultants=consultants)

@admin.route('/doctors')
@check_admin_role
def doctor_list():
    """
    医生列表
    """
    doctors = Doctor.query.order_by(Doctor.created_at.desc()).all()
    return render_template('admin/doctor_list.html', doctors=doctors)

@admin.route('/doctors/add', methods=['GET', 'POST'])
@check_admin_role
def add_doctor():
    """
    添加医生
    """
    if request.method == 'POST':
        data = request.form
        
        if not data.get('name') or not data.get('store_id'):
            flash('姓名和所属门店为必填项', 'danger')
            return redirect(url_for('admin.add_doctor'))
        
        # 创建新医生
        new_doctor = Doctor(
            name=data.get('name'),
            title=data.get('title'),
            specialty=data.get('specialty'),
            bio=data.get('bio'),
            store_id=data.get('store_id'),
            status='available'
        )
        
        db.session.add(new_doctor)
        db.session.commit()
        
        flash('医生添加成功', 'success')
        return redirect(url_for('admin.doctor_list'))
    
    # 获取门店列表
    stores = Store.query.filter_by(status='active').all()
    
    return render_template('admin/add_doctor.html', stores=stores)

@admin.route('/doctors/<int:doctor_id>', methods=['GET', 'POST'])
@check_admin_role
def doctor_detail(doctor_id):
    """
    医生详情
    """
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        data = request.form
        
        # 更新医生资料
        doctor.name = data.get('name')
        doctor.title = data.get('title')
        doctor.specialty = data.get('specialty')
        doctor.bio = data.get('bio')
        doctor.store_id = data.get('store_id')
        doctor.status = data.get('status')
        
        db.session.commit()
        flash('医生资料已更新', 'success')
    
    # 获取门店列表
    stores = Store.query.filter_by(status='active').all()
    
    return render_template('admin/doctor_detail.html',
                          doctor=doctor,
                          stores=stores)

@admin.route('/orphan_clients')
@check_admin_role
def orphan_clients():
    """
    孤儿客户管理
    """
    clients = Client.query.filter_by(is_orphan=True).all()
    return render_template('admin/orphan_clients.html', clients=clients)

@admin.route('/orphan_clients/reassign/<int:client_id>', methods=['POST'])
@check_admin_role
def reassign_client(client_id):
    """
    重新分配孤儿客户
    """
    client = Client.query.get_or_404(client_id)
    consultant_id = request.form.get('consultant_id')
    
    if not consultant_id:
        flash('请选择咨询师', 'danger')
        return redirect(url_for('admin.orphan_clients'))
    
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # 更新客户资料
    client.assigned_consultant_id = consultant.id
    client.is_orphan = False
    client.last_contact = datetime.utcnow()
    
    db.session.commit()
    flash('客户已重新分配', 'success')
    
    return redirect(url_for('admin.orphan_clients'))

@admin.route('/knowledge/review')
@check_admin_role
def knowledge_review():
    """
    知识库内容审核
    """
    articles = KnowledgeArticle.query.filter_by(status='pending').all()
    qa_list = KnowledgeQA.query.filter_by(status='pending').all()
    
    return render_template('admin/knowledge_review.html',
                          articles=articles,
                          qa_list=qa_list)

@admin.route('/knowledge/review/article/<int:article_id>', methods=['POST'])
@check_admin_role
def review_article(article_id):
    """
    审核知识库文章
    """
    article = KnowledgeArticle.query.get_or_404(article_id)
    action = request.form.get('action')
    
    if action == 'approve':
        article.status = 'approved'
        db.session.commit()
        flash('文章已审核通过', 'success')
    
    elif action == 'reject':
        article.status = 'rejected'
        db.session.commit()
        flash('文章已拒绝', 'info')
    
    return redirect(url_for('admin.knowledge_review'))

@admin.route('/knowledge/review/qa/<int:qa_id>', methods=['POST'])
@check_admin_role
def review_qa(qa_id):
    """
    审核知识库问答
    """
    qa = KnowledgeQA.query.get_or_404(qa_id)
    action = request.form.get('action')
    
    if action == 'approve':
        qa.status = 'approved'
        db.session.commit()
        flash('问答已审核通过', 'success')
    
    elif action == 'reject':
        qa.status = 'rejected'
        db.session.commit()
        flash('问答已拒绝', 'info')
    
    return redirect(url_for('admin.knowledge_review'))

@admin.route('/stats')
@check_admin_role
def stats():
    """
    统计数据
    """
    # 用户增长统计
    user_stats = db.session.query(
        func.date_format(User.created_at, '%Y-%m').label('month'),
        func.count(User.id).label('count')
    ).group_by('month').order_by('month').all()
    
    # 客户分配统计
    consultant_stats = db.session.query(
        Consultant.id,
        User.username,
        func.count(Client.id).label('client_count')
    ).join(User, User.id == Consultant.user_id).outerjoin(
        Client, Client.assigned_consultant_id == Consultant.id
    ).group_by(Consultant.id).order_by(db.desc('client_count')).limit(10).all()
    
    # 治疗项目统计
    treatment_stats = db.session.query(
        Treatment.type,
        func.count(Treatment.id).label('count')
    ).group_by(Treatment.type).order_by(db.desc('count')).all()
    
    return render_template('admin/stats.html',
                          user_stats=user_stats,
                          consultant_stats=consultant_stats,
                          treatment_stats=treatment_stats) 