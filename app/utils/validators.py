"""
验证工具模块
"""
import re


def validate_email(email):
    """
    验证邮箱格式
    
    @param {string} email - 邮箱地址
    @return {bool} - 是否合法
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """
    验证手机号格式（中国大陆手机号）
    
    @param {string} phone - 手机号
    @return {bool} - 是否合法
    """
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))


def validate_password(password):
    """
    验证密码强度
    
    @param {string} password - 密码
    @return {tuple} - (是否合法, 错误信息)
    """
    if len(password) < 8:
        return False, "密码长度必须至少8位"
    
    if not re.search(r"[A-Z]", password):
        return False, "密码必须包含至少一个大写字母"
    
    if not re.search(r"[a-z]", password):
        return False, "密码必须包含至少一个小写字母"
    
    if not re.search(r"\d", password):
        return False, "密码必须包含至少一个数字"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "密码必须包含至少一个特殊字符"
    
    return True, ""


def validate_username(username):
    """
    验证用户名格式
    
    @param {string} username - 用户名
    @return {tuple} - (是否合法, 错误信息)
    """
    if len(username) < 3:
        return False, "用户名长度必须至少3位"
    
    if len(username) > 20:
        return False, "用户名长度不能超过20位"
    
    if not re.match(r"^[a-zA-Z0-9_\u4e00-\u9fa5]+$", username):
        return False, "用户名只能包含字母、数字、下划线和中文"
    
    return True, ""


def validate_required_fields(data, required_fields):
    """
    验证必填字段
    
    @param {dict} data - 请求数据
    @param {list} required_fields - 必填字段列表
    @return {tuple} - (是否合法, 错误信息)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    
    return True, ""


def validate_date_format(date_str):
    """
    验证日期格式 (YYYY-MM-DD)
    
    @param {string} date_str - 日期字符串
    @return {bool} - 是否合法
    """
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, date_str):
        return False
    
    try:
        year, month, day = map(int, date_str.split('-'))
        
        # 检查月份
        if month < 1 or month > 12:
            return False
        
        # 检查日期
        if day < 1:
            return False
        
        # 检查每月的天数
        if month in [4, 6, 9, 11] and day > 30:
            return False
        elif month == 2:
            # 闰年检查
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            if (is_leap and day > 29) or (not is_leap and day > 28):
                return False
        elif day > 31:
            return False
        
        return True
    except ValueError:
        return False


def validate_id_card(id_card):
    """
    验证身份证号（中国大陆居民身份证）
    
    @param {string} id_card - 身份证号
    @return {bool} - 是否合法
    """
    # 基本格式检查：18位，前17位为数字，最后一位可能是数字或X
    pattern = r"^\d{17}[\dX]$"
    if not re.match(pattern, id_card):
        return False
    
    # 检查省份代码
    province_codes = {"11", "12", "13", "14", "15", "21", "22", "23", "31", "32", "33", "34", "35", "36", "37", "41", "42", "43", "44", "45", "46", "50", "51", "52", "53", "54", "61", "62", "63", "64", "65", "71", "81", "82", "91"}
    if id_card[:2] not in province_codes:
        return False
    
    # 检查出生日期
    try:
        birth_year = int(id_card[6:10])
        birth_month = int(id_card[10:12])
        birth_day = int(id_card[12:14])
        
        # 简单的年月日检查
        if birth_year < 1900 or birth_year > 2100:
            return False
        if birth_month < 1 or birth_month > 12:
            return False
        if birth_day < 1 or birth_day > 31:
            return False
    except ValueError:
        return False
    
    # 简化版的校验位检查
    # 完整实现需要加权因子和校验算法，这里简化处理
    return True

def sanitize_html(html_content):
    """
    清理HTML内容中的恶意代码
    
    @param {string} html_content - HTML内容
    @return {string} - 清理后的HTML
    """
    # 这里可以使用bleach等库实现更完善的HTML清理
    # 简单实现，移除script标签
    cleaned = re.sub(r'<script[\s\S]*?</script>', '', html_content)
    return cleaned 