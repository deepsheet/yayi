"""
自定义异常模块
"""


class APIException(Exception):
    """
    API异常基类
    
    @param {string} message - 错误消息
    @param {int} status_code - HTTP状态码
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="系统异常", status_code=500, errors=None):
        self.message = message
        self.status_code = status_code
        self.errors = errors
        super().__init__(self.message)


class BadRequestException(APIException):
    """
    400 错误请求异常
    
    @param {string} message - 错误消息
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="请求参数错误", errors=None):
        super().__init__(message=message, status_code=400, errors=errors)


class UnauthorizedException(APIException):
    """
    401 未授权异常
    
    @param {string} message - 错误消息
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="未授权访问", errors=None):
        super().__init__(message=message, status_code=401, errors=errors)


class ForbiddenException(APIException):
    """
    403 禁止访问异常
    
    @param {string} message - 错误消息
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="禁止访问", errors=None):
        super().__init__(message=message, status_code=403, errors=errors)


class NotFoundException(APIException):
    """
    404 资源不存在异常
    
    @param {string} message - 错误消息
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="资源不存在", errors=None):
        super().__init__(message=message, status_code=404, errors=errors)


class ResourceExistsException(APIException):
    """
    409 资源已存在异常
    
    @param {string} message - 错误消息
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="资源已存在", errors=None):
        super().__init__(message=message, status_code=409, errors=errors)


class ValidationException(BadRequestException):
    """
    422 数据验证失败异常
    
    @param {string} message - 错误消息
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="数据验证失败", errors=None):
        super().__init__(message=message, errors=errors)
        self.status_code = 422


class ServerException(APIException):
    """
    500 服务器内部错误异常
    
    @param {string} message - 错误消息
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="服务器内部错误", errors=None):
        super().__init__(message=message, status_code=500, errors=errors)


class ServiceUnavailableException(APIException):
    """
    503 服务不可用异常
    
    @param {string} message - 错误消息
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="服务暂时不可用", errors=None):
        super().__init__(message=message, status_code=503, errors=errors)


class DatabaseException(ServerException):
    """
    数据库操作异常
    
    @param {string} message - 错误消息
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="数据库操作失败", errors=None):
        super().__init__(message=message, errors=errors)


class ExternalServiceException(ServerException):
    """
    外部服务调用异常
    
    @param {string} message - 错误消息
    @param {dict|list|None} errors - 详细错误信息
    """
    def __init__(self, message="外部服务调用失败", errors=None):
        super().__init__(message=message, errors=errors) 