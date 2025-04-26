"""
响应处理工具模块
"""
from flask import jsonify


def success_response(data=None, message="操作成功", status_code=200):
    """
    成功响应格式化
    
    @param {any} data - 响应数据
    @param {string} message - 响应消息
    @param {int} status_code - HTTP状态码
    @return {tuple} - (JSON响应, 状态码)
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code


def error_response(message="操作失败", errors=None, status_code=400):
    """
    错误响应格式化
    
    @param {string} message - 错误消息
    @param {dict|list} errors - 详细错误信息
    @param {int} status_code - HTTP状态码
    @return {tuple} - (JSON响应, 状态码)
    """
    response = {
        "success": False,
        "message": message,
        "errors": errors
    }
    return jsonify(response), status_code


def pagination_meta(page, per_page, total_items):
    """
    分页元数据格式化
    
    @param {int} page - 当前页码
    @param {int} per_page - 每页条数
    @param {int} total_items - 总条数
    @return {dict} - 分页元数据
    """
    total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 0
    
    return {
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


def paginated_response(items, page, per_page, total_items, message="获取成功"):
    """
    分页数据响应格式化
    
    @param {list} items - 分页数据项
    @param {int} page - 当前页码
    @param {int} per_page - 每页条数
    @param {int} total_items - 总条数
    @param {string} message - 响应消息
    @return {tuple} - (JSON响应, 状态码)
    """
    response = {
        "success": True,
        "message": message,
        "data": items,
        "pagination": pagination_meta(page, per_page, total_items)
    }
    return jsonify(response), 200


# 常见HTTP错误的便捷函数
def bad_request(message="请求参数错误", errors=None):
    """
    400错误响应
    
    @param {string} message - 错误消息
    @param {dict|list} errors - 详细错误信息
    @return {tuple} - (JSON响应, 状态码)
    """
    return error_response(message, errors, 400)


def unauthorized(message="未授权访问", errors=None):
    """
    401错误响应
    
    @param {string} message - 错误消息
    @param {dict|list} errors - 详细错误信息
    @return {tuple} - (JSON响应, 状态码)
    """
    return error_response(message, errors, 401)


def forbidden(message="禁止访问", errors=None):
    """
    403错误响应
    
    @param {string} message - 错误消息
    @param {dict|list} errors - 详细错误信息
    @return {tuple} - (JSON响应, 状态码)
    """
    return error_response(message, errors, 403)


def not_found(message="资源不存在", errors=None):
    """
    404错误响应
    
    @param {string} message - 错误消息
    @param {dict|list} errors - 详细错误信息
    @return {tuple} - (JSON响应, 状态码)
    """
    return error_response(message, errors, 404)


def server_error(message="服务器内部错误", errors=None):
    """
    500错误响应
    
    @param {string} message - 错误消息
    @param {dict|list} errors - 详细错误信息
    @return {tuple} - (JSON响应, 状态码)
    """
    return error_response(message, errors, 500) 