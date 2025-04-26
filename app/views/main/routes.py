"""
主页路由
"""
from flask import render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from app import db
from app.models import Store, Doctor
from app.views.main import main
from datetime import datetime, timedelta

@main.route('/')
def index():
    """
    主页
    """
    # 添加缓存控制
    response = make_response(render_template('main/index.html', 
                          featured_stores=[],
                          featured_doctors=[]))
    # 设置缓存，有效期10分钟
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response

@main.route('/about')
def about():
    """
    关于我们页面
    """
    # 添加缓存控制
    response = make_response(render_template('main/about.html'))
    # 设置缓存，有效期1小时
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response

@main.route('/services')
def services():
    """
    服务介绍页面
    """
    # 添加缓存控制
    response = make_response(render_template('main/services.html'))
    # 设置缓存，有效期1小时
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response

@main.route('/contact')
def contact():
    """
    联系我们页面
    """
    # 添加缓存控制
    response = make_response(render_template('main/contact.html'))
    # 设置缓存，有效期1小时
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response

@main.route('/dashboard')
@login_required
def dashboard():
    """
    根据用户角色重定向到对应的仪表盘
    """
    if current_user.role == 'admin':
        return redirect(url_for('admin.index'))
    elif current_user.role in ['consultant', 'fulltime_consultant']:
        return redirect(url_for('consultant.index'))
    else:
        return redirect(url_for('client.index')) 