"""
咨询师蓝图初始化文件
"""
from flask import Blueprint

consultant = Blueprint('consultant', __name__)

from . import routes 