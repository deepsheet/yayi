"""
API蓝图初始化文件
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api import users, clients, consultants, stores, treatments, messages, knowledge, authentication 