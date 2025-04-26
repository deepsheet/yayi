import mysql.connector
from mysql.connector import Error
from config.database import MYSQL_CONFIG

def execute_sql_file():
    try:
        # 连接数据库
        connection = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'],
            port=MYSQL_CONFIG['port']
        )
        
        if connection.is_connected():
            print("成功连接到MySQL数据库")
            
            # 读取SQL文件
            with open('init_database.sql', 'r', encoding='utf-8') as file:
                sql_commands = file.read()
            
            # 分割SQL命令
            commands = sql_commands.split(';')
            
            # 执行每个SQL命令
            cursor = connection.cursor()
            for command in commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                        print(f"执行SQL命令成功: {command[:50]}...")
                    except Error as e:
                        print(f"执行SQL命令失败: {command[:50]}...")
                        print(f"错误信息: {e}")
            
            # 提交事务
            connection.commit()
            print("所有SQL命令执行完成")
            
    except Error as e:
        print(f"连接数据库时出错: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    execute_sql_file() 