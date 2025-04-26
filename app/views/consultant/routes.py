"""
咨询师路由
"""
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Client, Consultant, Store, Message, GroupMessage, KnowledgeArticle, KnowledgeQA, Treatment
from app.views.consultant import consultant
from app.utils.ai_helper import DeepSeekAI
from app.api.authentication import token_required
import json
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_
from functools import wraps

def check_consultant_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['consultant', 'fulltime_consultant']:
            flash('您没有权限访问该页面', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@consultant.route('/')
@login_required
@check_consultant_role
def index():
    """
    咨询师首页
    """
    # 获取当前咨询师信息
    consultant_profile = Consultant.query.filter_by(user_id=current_user.id).first()
    
    # 获取负责的客户列表
    clients = Client.query.filter_by(assigned_consultant_id=consultant_profile.id).all() if consultant_profile else []
    
    # 获取最近的预约
    recent_appointments = Treatment.query.filter_by(
        consultant_id=consultant_profile.id,
        status='scheduled'
    ).order_by(Treatment.appointment_date).limit(5).all() if consultant_profile else []
    
    # 获取未读消息
    unread_messages = Message.query.filter_by(
        receiver_id=current_user.id,
        is_read=False
    ).count()
    
    return render_template('consultant/index.html',
                          consultant=consultant_profile,
                          clients=clients,
                          recent_appointments=recent_appointments,
                          unread_messages=unread_messages)

@consultant.route('/verification', methods=['GET', 'POST'])
@login_required
def verification():
    """
    咨询师认证
    """
    # 检查是否已认证
    consultant_profile = Consultant.query.filter_by(user_id=current_user.id).first()
    
    if consultant_profile and consultant_profile.verified:
        flash('您已完成认证', 'info')
        return redirect(url_for('consultant.index'))
    
    if request.method == 'POST':
        data = request.form
        
        # 获取认证资料
        certification_info = {
            'id_number': data.get('id_number'),
            'real_name': data.get('real_name'),
            'education': data.get('education'),
            'work_experience': data.get('work_experience')
        }
        
        if not consultant_profile:
            # 创建新咨询师档案
            consultant_profile = Consultant(
                user_id=current_user.id,
                type=data.get('type', 'parttime'),
                certification=json.dumps(certification_info),
                verified=False,
                bio=data.get('bio', '')
            )
            db.session.add(consultant_profile)
        else:
            # 更新现有档案
            consultant_profile.type = data.get('type', 'parttime')
            consultant_profile.certification = json.dumps(certification_info)
            consultant_profile.bio = data.get('bio', '')
        
        db.session.commit()
        
        # 上传证件照片逻辑
        if 'id_front' in request.files and 'id_back' in request.files:
            # 处理文件上传
            flash('认证资料已提交，请等待审核', 'success')
            return redirect(url_for('consultant.pending_verification'))
        
        flash('认证资料已提交，但您需要上传证件照片', 'warning')
        return redirect(url_for('consultant.verification'))
    
    return render_template('consultant/verification.html', consultant=consultant_profile)

@consultant.route('/pending_verification')
@login_required
def pending_verification():
    """
    等待审核页面
    """
    return render_template('consultant/pending_verification.html')

@consultant.route('/clients')
@login_required
@check_consultant_role
def client_list():
    """
    客户列表
    """
    consultant_profile = Consultant.query.filter_by(user_id=current_user.id).first()
    if not consultant_profile:
        flash('请先完善个人资料', 'warning')
        return redirect(url_for('consultant.edit_profile'))
    
    # 获取查询参数
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    # 构建查询
    query = Client.query.filter_by(assigned_consultant_id=consultant_profile.id)
    
    # 搜索条件
    if search:
        query = query.filter(
            or_(
                Client.name.like(f'%{search}%'),
                Client.contact_info.like(f'%{search}%')
            )
        )
    
    # 状态筛选
    if status:
        query = query.filter_by(status=status)
    
    # 执行查询
    clients = query.order_by(Client.last_contact.desc()).all()
    
    return render_template('consultant/client_list.html',
                          consultant=consultant_profile,
                          clients=clients)

@consultant.route('/clients/new', methods=['GET', 'POST'])
@login_required
@check_consultant_role
def add_client():
    """
    添加新客户
    """
    consultant_profile = Consultant.query.filter_by(user_id=current_user.id).first()
    
    if not consultant_profile:
        flash('请先完成咨询师认证', 'warning')
        return redirect(url_for('consultant.verification'))
    
    if request.method == 'POST':
        data = request.form
        
        # 检查必填字段
        if not data.get('name') or not data.get('contact_info'):
            flash('姓名和手机号为必填项', 'danger')
            return redirect(url_for('consultant.add_client'))
        
        # 检查手机号是否已存在
        existing_user = User.query.filter_by(phone=data.get('contact_info')).first()
        
        if existing_user:
            # 检查该用户是否已有客户资料
            existing_client = Client.query.filter_by(user_id=existing_user.id).first()
            
            if existing_client:
                if existing_client.assigned_consultant_id == consultant_profile.id:
                    flash('该客户已在您的客户列表中', 'warning')
                    return redirect(url_for('consultant.client_list'))
                else:
                    # 如果客户已被其他咨询师认领，根据业务规则处理
                    if existing_client.is_orphan:
                        # 如果是"孤儿客户"，可以认领
                        existing_client.assigned_consultant_id = consultant_profile.id
                        existing_client.is_orphan = False
                        existing_client.last_contact = datetime.utcnow()
                        db.session.commit()
                        flash('成功认领孤儿客户', 'success')
                        return redirect(url_for('consultant.client_list'))
                    else:
                        flash('该客户已被其他咨询师认领', 'danger')
                        return redirect(url_for('consultant.add_client'))
            else:
                # 用户存在但没有客户资料，创建客户资料
                new_client = Client(
                    user_id=existing_user.id,
                    name=data.get('name'),
                    gender=data.get('gender'),
                    contact_info=data.get('contact_info'),
                    assigned_consultant_id=consultant_profile.id,
                    last_contact=datetime.utcnow()
                )
                db.session.add(new_client)
                db.session.commit()
                flash('客户添加成功', 'success')
                return redirect(url_for('consultant.client_list'))
        else:
            # 创建新用户和客户资料
            new_user = User(
                username=f'client_{data.get("contact_info")}',
                phone=data.get('contact_info'),
                password='123456',  # 默认密码
                role='client'
            )
            db.session.add(new_user)
            db.session.flush()
            
            new_client = Client(
                user_id=new_user.id,
                name=data.get('name'),
                gender=data.get('gender'),
                contact_info=data.get('contact_info'),
                assigned_consultant_id=consultant_profile.id,
                last_contact=datetime.utcnow()
            )
            db.session.add(new_client)
            db.session.commit()
            flash('客户添加成功', 'success')
            return redirect(url_for('consultant.client_list'))
    
    return render_template('consultant/add_client.html')

@consultant.route('/client/<int:client_id>')
@login_required
@check_consultant_role
def client_detail(client_id):
    """
    客户详情
    """
    client = Client.query.get_or_404(client_id)
    treatments = Treatment.query.filter_by(client_id=client.id).all()
    
    return render_template('consultant/client_detail.html',
                          client=client,
                          treatments=treatments)

@consultant.route('/chat/<int:client_id>')
@login_required
@check_consultant_role
def chat(client_id):
    """
    与客户聊天
    """
    client = Client.query.get_or_404(client_id)
    
    # 获取历史消息
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, 
                 Message.receiver_id == client.user_id),
            and_(Message.sender_id == client.user_id, 
                 Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at).all()
    
    return render_template('consultant/chat.html',
                          client=client,
                          messages=messages)

@consultant.route('/ai_suggest', methods=['POST'])
@login_required
@check_consultant_role
def ai_suggest():
    """
    获取AI回复建议
    """
    data = request.get_json()
    if not data or not data.get('question'):
        return jsonify({'success': False, 'message': '请提供问题内容'}), 400
    
    question = data.get('question')
    context = data.get('context', [])
    
    # 使用AI助手生成回复
    ai = DeepSeekAI()
    answer = ai.generate_response(question, context)
    
    return jsonify({
        'success': True,
        'answer': answer
    })

@consultant.route('/send_message', methods=['POST'])
@login_required
@check_consultant_role
def send_message():
    """
    发送消息
    """
    data = request.get_json()
    if not data or not data.get('content') or not data.get('client_id'):
        return jsonify({'success': False, 'message': '消息内容和客户ID为必填项'}), 400
    
    client = Client.query.get_or_404(data.get('client_id'))
    consultant_profile = Consultant.query.filter_by(user_id=current_user.id).first()
    
    # 检查权限
    if client.assigned_consultant_id != consultant_profile.id:
        return jsonify({'success': False, 'message': '您没有权限向该客户发送消息'}), 403
    
    # 创建新消息
    new_message = Message(
        sender_id=current_user.id,
        receiver_id=client.user_id,
        content=data.get('content'),
        msg_type=data.get('msg_type', 'text'),
        attachment_url=data.get('attachment_url')
    )
    db.session.add(new_message)
    
    # 更新最后联系时间
    client.last_contact = datetime.utcnow()
    if client.is_orphan:
        client.is_orphan = False
    
    db.session.commit()
    
    # 使用AI分析消息情感
    ai = DeepSeekAI()
    sentiment_score = ai.analyze_sentiment(data.get('content'))
    new_message.sentiment_score = sentiment_score
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': {
            'id': new_message.id,
            'content': new_message.content,
            'time': new_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'attachment_url': new_message.attachment_url,
            'sentiment_score': sentiment_score
        }
    })

@consultant.route('/group_messages', methods=['GET', 'POST'])
@login_required
@check_consultant_role
def group_messages():
    """
    群发消息
    """
    consultant_profile = Consultant.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        data = request.form
        
        if not data.get('content'):
            flash('消息内容不能为空', 'danger')
            return redirect(url_for('consultant.group_messages'))
        
        # 创建群发消息
        new_group_message = GroupMessage(
            sender_id=current_user.id,
            content=data.get('content'),
            msg_type=data.get('msg_type', 'text'),
            target_type=data.get('target_type', 'all_clients'),
            target_tags=data.get('target_tags'),
            attachment_url=data.get('attachment_url')
        )
        db.session.add(new_group_message)
        db.session.commit()
        
        # 查找目标客户
        target_clients = []
        if new_group_message.target_type == 'all_clients':
            target_clients = Client.query.filter_by(
                assigned_consultant_id=consultant_profile.id
            ).all()
        elif new_group_message.target_type == 'tagged_clients' and new_group_message.target_tags:
            tags = new_group_message.target_tags.split(',')
            for tag in tags:
                clients = Client.query.filter(
                    Client.assigned_consultant_id == consultant_profile.id,
                    Client.tags.like(f'%{tag.strip()}%')
                ).all()
                target_clients.extend(clients)
            # 去重
            target_clients = list(set(target_clients))
        
        # 发送个人消息给每个目标客户
        for client in target_clients:
            if client.user_id:
                message = Message(
                    sender_id=current_user.id,
                    receiver_id=client.user_id,
                    content=new_group_message.content,
                    msg_type=new_group_message.msg_type,
                    attachment_url=new_group_message.attachment_url
                )
                db.session.add(message)
                # 更新最后联系时间
                client.last_contact = datetime.utcnow()
                new_group_message.sent_count += 1
        
        new_group_message.status = 'sent'
        db.session.commit()
        
        flash(f'群发消息已成功发送给{new_group_message.sent_count}位客户', 'success')
        return redirect(url_for('consultant.group_messages'))
    
    # 获取历史群发消息
    group_messages = GroupMessage.query.filter_by(
        sender_id=current_user.id
    ).order_by(GroupMessage.created_at.desc()).all()
    
    # 获取客户标签列表
    all_tags = set()
    clients = Client.query.filter_by(assigned_consultant_id=consultant_profile.id).all()
    for client in clients:
        if client.tags:
            client_tags = client.tags.split(',')
            all_tags.update([tag.strip() for tag in client_tags])
    
    return render_template('consultant/group_messages.html',
                          group_messages=group_messages,
                          tags=list(all_tags))

@consultant.route('/knowledge')
@login_required
@check_consultant_role
def knowledge():
    """
    知识库
    """
    articles = KnowledgeArticle.query.filter_by(status='approved').order_by(
        KnowledgeArticle.created_at.desc()).all()
    
    qa_list = KnowledgeQA.query.filter_by(status='approved').order_by(
        KnowledgeQA.use_count.desc()).all()
    
    return render_template('consultant/knowledge.html',
                          articles=articles,
                          qa_list=qa_list)

@consultant.route('/knowledge/article/<int:article_id>')
@login_required
@check_consultant_role
def knowledge_article(article_id):
    """
    知识库文章详情
    """
    article = KnowledgeArticle.query.get_or_404(article_id)
    
    # 增加使用次数
    article.use_count += 1
    db.session.commit()
    
    return render_template('consultant/knowledge_article.html', article=article)

@consultant.route('/knowledge/submit', methods=['GET', 'POST'])
@login_required
@check_consultant_role
def submit_knowledge():
    """
    提交知识到知识库
    """
    if request.method == 'POST':
        data = request.form
        
        if data.get('type') == 'article':
            # 提交文章
            if not data.get('title') or not data.get('content'):
                flash('标题和内容为必填项', 'danger')
                return redirect(url_for('consultant.submit_knowledge'))
            
            new_article = KnowledgeArticle(
                title=data.get('title'),
                content=data.get('content'),
                category=data.get('category'),
                tags=data.get('tags'),
                author_id=current_user.id,
                status='pending'
            )
            db.session.add(new_article)
            db.session.commit()
            
            flash('文章已提交，等待审核', 'success')
            
        elif data.get('type') == 'qa':
            # 提交问答
            if not data.get('question') or not data.get('answer'):
                flash('问题和回答为必填项', 'danger')
                return redirect(url_for('consultant.submit_knowledge'))
            
            new_qa = KnowledgeQA(
                question=data.get('question'),
                answer=data.get('answer'),
                category=data.get('category'),
                tags=data.get('tags'),
                source='consultant',
                source_id=current_user.id,
                status='pending'
            )
            db.session.add(new_qa)
            db.session.commit()
            
            flash('问答已提交，等待审核', 'success')
        
        return redirect(url_for('consultant.knowledge'))
    
    return render_template('consultant/submit_knowledge.html')

@consultant.route('/settings')
@login_required
@check_consultant_role
def settings():
    """
    设置页面
    """
    consultant_profile = Consultant.query.filter_by(user_id=current_user.id).first()
    
    return render_template('consultant/settings.html', consultant=consultant_profile)

@consultant.route('/appointments')
@login_required
@check_consultant_role
def appointment_list():
    """
    预约列表
    """
    consultant_profile = Consultant.query.filter_by(user_id=current_user.id).first()
    if not consultant_profile:
        flash('请先完善个人资料', 'warning')
        return redirect(url_for('consultant.edit_profile'))
    
    # 获取查询参数
    date = request.args.get('date', '')
    status = request.args.get('status', '')
    
    # 构建查询
    query = Treatment.query.filter_by(consultant_id=consultant_profile.id)
    
    # 日期筛选
    if date:
        try:
            filter_date = datetime.strptime(date, '%Y-%m-%d').date()
            query = query.filter(func.date(Treatment.appointment_date) == filter_date)
        except ValueError:
            pass
    
    # 状态筛选
    if status:
        query = query.filter_by(status=status)
    
    # 执行查询
    appointments = query.order_by(Treatment.appointment_date).all()
    
    return render_template('consultant/appointment_list.html',
                          consultant=consultant_profile,
                          appointments=appointments)

@consultant.route('/messages')
@login_required
@check_consultant_role
def messages():
    """
    消息列表
    """
    # 获取查询参数
    message_type = request.args.get('type', 'all')
    
    # 构建查询
    query = Message.query.filter_by(receiver_id=current_user.id)
    
    # 消息类型筛选
    if message_type == 'unread':
        query = query.filter_by(is_read=False)
    elif message_type == 'system':
        query = query.filter_by(type='system')
    elif message_type == 'appointment':
        query = query.filter_by(type='appointment')
    
    # 执行查询
    messages = query.order_by(Message.created_at.desc()).all()
    
    # 标记所有未读消息为已读
    unread_messages = [msg for msg in messages if not msg.is_read]
    for msg in unread_messages:
        msg.is_read = True
    
    if unread_messages:
        db.session.commit()
    
    return render_template('consultant/messages.html',
                          messages=messages)

@consultant.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@check_consultant_role
def edit_profile():
    """
    编辑个人资料
    """
    consultant_profile = Consultant.query.filter_by(user_id=current_user.id).first()
    
    # 如果咨询师档案不存在，创建一个新的
    if not consultant_profile:
        consultant_profile = Consultant(
            user_id=current_user.id,
            type='parttime',  # 默认为兼职咨询师
            verified=False,
            bio='',
            specialties='',
            working_hours='',
            contact_info='',
            wechat='',
            education='',
            certifications='',
            experience=''
        )
        db.session.add(consultant_profile)
        db.session.commit()
    
    if request.method == 'POST':
        data = request.form
        
        # 更新基本信息
        consultant_profile.bio = data.get('bio', '')
        consultant_profile.specialties = data.get('specialties', '')
        consultant_profile.working_hours = data.get('working_hours', '')
        
        # 更新联系方式
        consultant_profile.contact_info = data.get('contact_info', '')
        consultant_profile.wechat = data.get('wechat', '')
        
        # 更新其他信息
        consultant_profile.education = data.get('education', '')
        consultant_profile.certifications = data.get('certifications', '')
        consultant_profile.experience = data.get('experience', '')
        
        db.session.commit()
        flash('个人资料更新成功', 'success')
        return redirect(url_for('consultant.index'))
    
    return render_template('consultant/edit_profile.html', consultant=consultant_profile)

@consultant.route('/init_test_data')
@login_required
@check_consultant_role
def init_test_data_route():
    """
    初始化测试数据路由
    """
    # 获取当前咨询师
    consultant_profile = Consultant.query.filter_by(user_id=current_user.id).first()
    if not consultant_profile:
        flash('请先完善个人资料', 'warning')
        return redirect(url_for('consultant.edit_profile'))
    
    # 创建测试客户
    test_clients = [
        {
            'name': '张三',
            'gender': '男',
            'contact_info': '13800138001',
            'status': 'active'
        },
        {
            'name': '李四',
            'gender': '女',
            'contact_info': '13800138002',
            'status': 'active'
        },
        {
            'name': '王五',
            'gender': '男',
            'contact_info': '13800138003',
            'status': 'inactive'
        }
    ]
    
    for client_data in test_clients:
        # 检查客户是否已存在
        existing_client = Client.query.filter_by(
            contact_info=client_data['contact_info']
        ).first()
        
        if not existing_client:
            new_client = Client(
                name=client_data['name'],
                gender=client_data['gender'],
                contact_info=client_data['contact_info'],
                status=client_data['status'],
                assigned_consultant_id=consultant_profile.id,
                last_contact=datetime.utcnow()
            )
            db.session.add(new_client)
    
    # 创建测试预约
    test_appointments = [
        {
            'client_name': '张三',
            'type': '洗牙',
            'appointment_date': datetime.utcnow() + timedelta(days=1),
            'status': 'pending'
        },
        {
            'client_name': '李四',
            'type': '补牙',
            'appointment_date': datetime.utcnow() + timedelta(days=2),
            'status': 'confirmed'
        },
        {
            'client_name': '王五',
            'type': '拔牙',
            'appointment_date': datetime.utcnow() + timedelta(days=3),
            'status': 'completed'
        }
    ]
    
    for appointment_data in test_appointments:
        client = Client.query.filter_by(name=appointment_data['client_name']).first()
        if client:
            new_appointment = Treatment(
                client_id=client.id,
                consultant_id=consultant_profile.id,
                type=appointment_data['type'],
                appointment_date=appointment_data['appointment_date'],
                status=appointment_data['status']
            )
            db.session.add(new_appointment)
    
    # 创建测试消息
    test_messages = [
        {
            'title': '系统通知',
            'content': '欢迎使用LY牙助手系统',
            'type': 'system',
            'is_read': False
        },
        {
            'title': '预约提醒',
            'content': '您有一个新的预约请求',
            'type': 'appointment',
            'is_read': False
        },
        {
            'title': '客户消息',
            'content': '您好，我想咨询一下洗牙的价格',
            'type': 'chat',
            'is_read': True
        }
    ]
    
    for message_data in test_messages:
        new_message = Message(
            sender_id=current_user.id,
            receiver_id=current_user.id,
            title=message_data['title'],
            content=message_data['content'],
            type=message_data['type'],
            is_read=message_data['is_read']
        )
        db.session.add(new_message)
    
    # 提交所有更改
    db.session.commit()
    flash('测试数据初始化成功', 'success')
    return redirect(url_for('consultant.index')) 