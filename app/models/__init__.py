"""
模型包初始化文件
"""

# 导入所有模型
from app.models.user import User
from app.models.client import Client
from app.models.consultant import Consultant
from app.models.store import Store
from app.models.doctor import Doctor
from app.models.treatment import Treatment
from app.models.message import Message, GroupMessage
from app.models.knowledge import KnowledgeArticle, KnowledgeQA 