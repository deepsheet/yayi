"""
客户端路由
"""
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Store, Doctor, Client, Treatment, Message
from app.views.client import client
from app.utils.ai_helper import DeepSeekAI
import json

@client.route('/')
@login_required
def index():
    """
    客户端首页
    """
    # 获取当前用户的客户信息
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    # 获取该客户的治疗记录
    treatments = Treatment.query.filter_by(client_id=client.id).all() if client else []
    
    return render_template('client/index.html',
                          client=client,
                          treatments=treatments)

@client.route('/map')
@login_required
def store_map():
    """
    门店地图
    """
    stores = Store.query.filter_by(status='active').all()
    store_data = [store.to_dict() for store in stores]
    return render_template('client/map.html', stores=store_data)

@client.route('/store/<int:store_id>')
@login_required
def store_detail(store_id):
    """
    门店详情
    """
    store = Store.query.get_or_404(store_id)
    doctors = Doctor.query.filter_by(store_id=store_id).all()
    return render_template('client/store_detail.html', store=store, doctors=doctors)

@client.route('/doctor/<int:doctor_id>')
@login_required
def doctor_detail(doctor_id):
    """
    医生详情
    """
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template('client/doctor_detail.html', doctor=doctor)

@client.route('/profile')
@login_required
def profile():
    """
    个人资料
    """
    # 获取当前用户的客户资料
    client_profile = Client.query.filter_by(user_id=current_user.id).first()
    treatments = []
    
    if client_profile:
        treatments = Treatment.query.filter_by(client_id=client_profile.id).all()
    
    return render_template('client/profile.html', 
                          client=client_profile, 
                          treatments=treatments)

@client.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    编辑个人资料
    """
    client_profile = Client.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        data = request.form
        
        if not client_profile:
            client_profile = Client(user_id=current_user.id)
            db.session.add(client_profile)
        
        client_profile.name = data.get('name')
        client_profile.gender = data.get('gender')
        client_profile.birth_date = data.get('birth_date')
        client_profile.address = data.get('address')
        client_profile.contact_info = data.get('contact_info')
        
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('client.profile'))
    
    return render_template('client/edit_profile.html', client=client_profile)

@client.route('/appointment')
@login_required
def appointment_list():
    """
    预约列表
    """
    client_profile = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client_profile:
        flash('请先完善个人资料', 'warning')
        return redirect(url_for('client.edit_profile'))
    
    appointments = Treatment.query.filter_by(
        client_id=client_profile.id, 
        status='scheduled'
    ).order_by(Treatment.appointment_date).all()
    
    return render_template('client/appointment_list.html', appointments=appointments)

@client.route('/appointment/new')
@login_required
def new_appointment():
    """
    新建预约
    """
    stores = Store.query.filter_by(status='active').all()
    return render_template('client/new_appointment.html', stores=stores)

@client.route('/messages')
@login_required
def messages():
    """
    消息列表
    """
    messages = Message.query.filter_by(receiver_id=current_user.id).order_by(
        Message.created_at.desc()).all()
    
    # 标记所有未读消息为已读
    unread_messages = [msg for msg in messages if not msg.is_read]
    for msg in unread_messages:
        msg.is_read = True
    
    if unread_messages:
        db.session.commit()
    
    return render_template('client/messages.html', messages=messages)

@client.route('/chat')
@login_required
def chat():
    """
    在线咨询
    """
    client_profile = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client_profile:
        flash('请先完善个人资料', 'warning')
        return redirect(url_for('client.edit_profile'))
    
    # 查找该客户的咨询师
    assigned_consultant = None
    if client_profile.assigned_consultant_id:
        from app.models import Consultant
        assigned_consultant = Consultant.query.get(client_profile.assigned_consultant_id)
    
    # 获取历史消息
    chat_history = []
    if assigned_consultant:
        from sqlalchemy import or_, and_
        messages = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, 
                     Message.receiver_id == assigned_consultant.user_id),
                and_(Message.sender_id == assigned_consultant.user_id, 
                     Message.receiver_id == current_user.id)
            )
        ).order_by(Message.created_at).all()
        
        chat_history = [{
            'id': msg.id,
            'content': msg.content,
            'is_self': msg.sender_id == current_user.id,
            'time': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'attachment_url': msg.attachment_url
        } for msg in messages]
    
    return render_template('client/chat.html', 
                          consultant=assigned_consultant, 
                          chat_history=json.dumps(chat_history))

@client.route('/ask', methods=['POST'])
@login_required
def ask_ai():
    """
    向AI助手提问
    """
    data = request.get_json()
    if not data or not data.get('question'):
        return jsonify({'success': False, 'message': '请提供问题内容'}), 400
    
    question = data.get('question')
    
    # 使用AI助手生成回复
    ai = DeepSeekAI()
    answer = ai.generate_response(question)
    
    return jsonify({
        'success': True,
        'answer': answer
    })

@client.route('/treatments')
@login_required
def treatment_history():
    """
    治疗记录
    """
    client_profile = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client_profile:
        flash('请先完善个人资料', 'warning')
        return redirect(url_for('client.edit_profile'))
    
    treatments = Treatment.query.filter_by(client_id=client_profile.id).order_by(
        Treatment.created_at.desc()).all()
    
    return render_template('client/treatment_history.html', treatments=treatments) 