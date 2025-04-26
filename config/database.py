import os

MYSQL_CONFIG = {
    'host': 'rdsen5kmj2c7h6kj0708o.mysql.rds.aliyuncs.com',  # 直接使用硬编码值
    'user': 'yayiadmin',
    'password': 'Wang7788',
    'database': 'yayi',
    'port': 3306,
    'charset': 'utf8mb4'} 

REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', '46f28b3f2f604625302.redis.rds.aliyuncs.com'),
    'port': int(os.getenv('REDIS_PORT', '6379')),
    'db': int(os.getenv('REDIS_DB', '0')),
    'password': os.getenv('REDIS_PASSWORD', 'Chenkunjiliukai11112222'),
}