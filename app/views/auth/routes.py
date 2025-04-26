"""
认证路由
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.views.auth import auth
from app.utils.validators import validate_email, validate_phone, validate_password

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        identity = request.form.get('identity')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        if not identity or not password:
            flash('请输入用户名/邮箱/手机号和密码', 'danger')
            return redirect(url_for('auth.login'))
        
        # 查找用户
        user = User.query.filter_by(username=identity).first() or \
               User.query.filter_by(email=identity).first() or \
               User.query.filter_by(phone=identity).first()
        
        if not user:
            flash('用户不存在', 'danger')
            return redirect(url_for('auth.login'))
        
        # 验证密码
        if not user.verify_password(password):
            flash('密码错误', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('账户已被禁用，请联系管理员', 'warning')
            return redirect(url_for('auth.login'))
        
        # 登录成功
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.dashboard')
        
        flash('登录成功！', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证必填项
        if not username or not password:
            flash('用户名和密码为必填项', 'danger')
            return redirect(url_for('auth.register'))
        
        # 验证密码
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('auth.register'))
        
        valid_password, password_error = validate_password(password)
        if not valid_password:
            flash(f'密码强度不够: {password_error}', 'danger')
            return redirect(url_for('auth.register'))
        
        # 验证用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('auth.register'))
        
        # 验证邮箱
        if email:
            if not validate_email(email):
                flash('邮箱格式不正确', 'danger')
                return redirect(url_for('auth.register'))
            if User.query.filter_by(email=email).first():
                flash('该邮箱已被注册', 'danger')
                return redirect(url_for('auth.register'))
        
        # 验证手机号
        if phone:
            if not validate_phone(phone):
                flash('手机号格式不正确', 'danger')
                return redirect(url_for('auth.register'))
            if User.query.filter_by(phone=phone).first():
                flash('该手机号已被注册', 'danger')
                return redirect(url_for('auth.register'))
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password=password,
            role='client'  # 默认为客户角色
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    """
    用户登出
    """
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('main.index'))

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    请求重置密码
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email or not validate_email(email):
            flash('请输入有效的邮箱地址', 'danger')
            return redirect(url_for('auth.reset_password_request'))
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('该邮箱未注册', 'danger')
            return redirect(url_for('auth.reset_password_request'))
        
        # 这里应该发送重置密码邮件，但为了简化示例，直接跳转到重置页面
        # 实际应用中需要生成唯一的token并发送邮件
        flash('重置密码的邮件已发送，请查收', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html')

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    重置密码
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # 这里应该验证token，但为了简化示例，直接显示重置页面
    # 实际应用中需要解析token获取用户信息
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
        
        valid_password, password_error = validate_password(password)
        if not valid_password:
            flash(f'密码强度不够: {password_error}', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
        
        # 这里应该通过token找到对应的用户并更新密码
        # 实际应用中需要从token中解析用户信息
        # user = User.verify_reset_token(token)
        # if not user:
        #     flash('无效或已过期的重置链接', 'danger')
        #     return redirect(url_for('auth.reset_password_request'))
        # 
        # user.password = password
        # db.session.commit()
        
        flash('密码已重置，请使用新密码登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html') 