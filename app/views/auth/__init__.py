"""
认证蓝图初始化文件
"""
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes 