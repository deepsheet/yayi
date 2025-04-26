"""
主页蓝图初始化文件
"""
from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes 