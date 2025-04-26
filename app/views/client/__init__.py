"""
客户端蓝图初始化文件
"""
from flask import Blueprint

client = Blueprint('client', __name__)

from . import routes 