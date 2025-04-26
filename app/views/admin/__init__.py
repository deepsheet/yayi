"""
管理员蓝图初始化文件
"""
from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import routes 