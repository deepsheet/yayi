"""
知识库相关API
"""
from flask import request, g
from app import db
from app.models import KnowledgeArticle, KnowledgeQA, User
from app.api import api_bp
from app.utils.response import success_response, error_response, paginated_response
from app.utils.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.utils.validators import validate_required_fields
from app.api.authentication import token_required
from datetime import datetime
import json

@api_bp.route('/knowledge/articles', methods=['GET'])
@token_required
def get_articles():
    """
    获取知识库文章列表
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    status = request.args.get('status')  # pending/approved/rejected
    
    # 构建查询
    query = KnowledgeArticle.query
    
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    
    # 执行分页查询
    pagination = query.order_by(KnowledgeArticle.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[article.to_dict() for article in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取知识库文章列表成功"
    )

@api_bp.route('/knowledge/articles/<int:article_id>', methods=['GET'])
@token_required
def get_article(article_id):
    """
    获取知识库文章详情
    
    @param {int} article_id - 文章ID
    @return {tuple} - (JSON响应, 状态码)
    """
    article = KnowledgeArticle.query.get_or_404(article_id)
    
    # 增加使用次数
    article.use_count += 1
    db.session.commit()
    
    return success_response(
        data=article.to_dict(),
        message="获取知识库文章详情成功"
    )

@api_bp.route('/knowledge/articles', methods=['POST'])
@token_required
def create_article():
    """
    创建知识库文章
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role not in ['admin', 'consultant', 'fulltime_consultant']:
        return error_response("无权限操作", status_code=403)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['title', 'content', 'category']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 创建新文章
    new_article = KnowledgeArticle(
        title=data['title'],
        content=data['content'],
        category=data['category'],
        tags=data.get('tags'),
        author_id=g.current_user.id,
        status='pending'
    )
    
    db.session.add(new_article)
    db.session.commit()
    
    return success_response(
        data=new_article.to_dict(),
        message="创建知识库文章成功",
        status_code=201
    )

@api_bp.route('/knowledge/articles/<int:article_id>', methods=['PUT'])
@token_required
def update_article(article_id):
    """
    更新知识库文章
    
    @param {int} article_id - 文章ID
    @return {tuple} - (JSON响应, 状态码)
    """
    article = KnowledgeArticle.query.get_or_404(article_id)
    
    # 检查权限
    if g.current_user.role != 'admin' and g.current_user.id != article.author_id:
        return error_response("无权限操作", status_code=403)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['title', 'content', 'category']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 更新文章
    article.title = data['title']
    article.content = data['content']
    article.category = data['category']
    article.tags = data.get('tags')
    article.updated_at = datetime.utcnow()
    
    # 如果是管理员，可以更新状态
    if g.current_user.role == 'admin' and 'status' in data:
        article.status = data['status']
    
    db.session.commit()
    
    return success_response(
        data=article.to_dict(),
        message="更新知识库文章成功"
    )

@api_bp.route('/knowledge/qa', methods=['GET'])
@token_required
def get_qa_list():
    """
    获取知识问答列表
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    status = request.args.get('status')  # pending/approved/rejected
    
    # 构建查询
    query = KnowledgeQA.query
    
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    
    # 执行分页查询
    pagination = query.order_by(KnowledgeQA.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return paginated_response(
        items=[qa.to_dict() for qa in pagination.items],
        page=page,
        per_page=per_page,
        total_items=pagination.total,
        message="获取知识问答列表成功"
    )

@api_bp.route('/knowledge/qa/<int:qa_id>', methods=['GET'])
@token_required
def get_qa(qa_id):
    """
    获取知识问答详情
    
    @param {int} qa_id - 问答ID
    @return {tuple} - (JSON响应, 状态码)
    """
    qa = KnowledgeQA.query.get_or_404(qa_id)
    
    # 增加使用次数
    qa.use_count += 1
    db.session.commit()
    
    return success_response(
        data=qa.to_dict(),
        message="获取知识问答详情成功"
    )

@api_bp.route('/knowledge/qa', methods=['POST'])
@token_required
def create_qa():
    """
    创建知识问答
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 检查权限
    if g.current_user.role not in ['admin', 'consultant', 'fulltime_consultant']:
        return error_response("无权限操作", status_code=403)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['question', 'answer', 'category']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 创建新问答
    new_qa = KnowledgeQA(
        question=data['question'],
        answer=data['answer'],
        category=data['category'],
        tags=data.get('tags'),
        source=data.get('source', 'preset'),
        source_id=data.get('source_id'),
        status='pending'
    )
    
    db.session.add(new_qa)
    db.session.commit()
    
    return success_response(
        data=new_qa.to_dict(),
        message="创建知识问答成功",
        status_code=201
    )

@api_bp.route('/knowledge/qa/<int:qa_id>', methods=['PUT'])
@token_required
def update_qa(qa_id):
    """
    更新知识问答
    
    @param {int} qa_id - 问答ID
    @return {tuple} - (JSON响应, 状态码)
    """
    qa = KnowledgeQA.query.get_or_404(qa_id)
    
    # 检查权限
    if g.current_user.role != 'admin':
        return error_response("无权限操作", status_code=403)
    
    # 验证必填字段
    data = request.get_json()
    required_fields = ['question', 'answer', 'category']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, status_code=400)
    
    # 更新问答
    qa.question = data['question']
    qa.answer = data['answer']
    qa.category = data['category']
    qa.tags = data.get('tags')
    qa.updated_at = datetime.utcnow()
    
    # 如果是管理员，可以更新状态
    if 'status' in data:
        qa.status = data['status']
    
    db.session.commit()
    
    return success_response(
        data=qa.to_dict(),
        message="更新知识问答成功"
    )

@api_bp.route('/knowledge/search', methods=['GET'])
@token_required
def search_knowledge():
    """
    搜索知识库
    
    @return {tuple} - (JSON响应, 状态码)
    """
    # 获取查询参数
    query = request.args.get('q', '')
    category = request.args.get('category')
    type_filter = request.args.get('type')  # article/qa
    
    if not query:
        return error_response("搜索关键词不能为空", status_code=400)
    
    # 构建查询
    results = []
    
    if not type_filter or type_filter == 'article':
        articles = KnowledgeArticle.query.filter(
            (KnowledgeArticle.title.like(f'%{query}%')) | 
            (KnowledgeArticle.content.like(f'%{query}%'))
        )
        if category:
            articles = articles.filter_by(category=category)
        articles = articles.filter_by(status='approved').all()
        results.extend([article.to_dict() for article in articles])
    
    if not type_filter or type_filter == 'qa':
        qas = KnowledgeQA.query.filter(
            (KnowledgeQA.question.like(f'%{query}%')) | 
            (KnowledgeQA.answer.like(f'%{query}%'))
        )
        if category:
            qas = qas.filter_by(category=category)
        qas = qas.filter_by(status='approved').all()
        results.extend([qa.to_dict() for qa in qas])
    
    return success_response(
        data=results,
        message="搜索成功"
    ) 